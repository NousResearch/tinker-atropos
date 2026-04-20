import asyncio
import os
import time
import numpy as np
import torch
import random
from typing import Dict, Any, List

import tinker
from tinker.types import AdamParams, ModelInput, SamplingParams
import wandb
import requests
from fastapi import FastAPI, HTTPException
from transformers import AutoTokenizer
from tenacity import retry, stop_after_attempt, wait_exponential

from tinker_atropos.types import (
    GenerateRequest,
    GenerateResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    LogprobsRequest,
    LogprobsResponse,
    TokenLogprob,
)
from tinker_atropos.config import TinkerAtroposConfig


class TinkerAtroposTrainer:
    """
    Trainer that handles both RL training and inference through Tinker API.
    Connects to Atropos Trajectory API to coordinate environment interaciton.
    """

    def __init__(self, config: TinkerAtroposConfig):
        self.config = config

        # Model and training config
        self.base_model = config.base_model
        self.lora_rank = config.lora_rank
        self.learning_rate = config.learning_rate
        self.atropos_api_url = config.atropos_api_url
        self.num_steps = config.num_steps

        # Tinker clients
        self.service_client = None
        self.training_client = None
        self.current_sampling_client = None

        self.tokenizer = None

        # Atropos registration
        self.trainer_id = None
        self.group_mean_rewards = []
        self.wandb_group = None

    async def setup(self):
        print("Setting up Tinker-Atropos Trainer...")

        # Create single ServiceClient for both training and inference
        print(f"Creating ServiceClient for {self.base_model}...")
        self.service_client = tinker.ServiceClient()

        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        print(f"Loaded tokenizer for {self.base_model}")

        # Create LoRA training client
        print("Creating training client...")
        self.training_client = await self.service_client.create_lora_training_client_async(
            base_model=self.base_model,
            rank=self.lora_rank,
        )
        print("Training client created")

        # Save initial weights and create sampling client
        print("Saving initial weights...")
        initial_path = self.training_client.save_weights_for_sampler(name="step_0").result().path
        self.current_sampling_client = self.service_client.create_sampling_client(
            model_path=initial_path
        )
        print(f"Initial sampling client created: {initial_path}")

        self.wandb_group = self.config.wandb_group or wandb.sdk.lib.runid.generate_id()

        print("Registering with Atropos API...")
        self.trainer_id = await self._register_trainer()
        print(f"Registered as trainer: {self.trainer_id}")

        if self.config.use_wandb:
            try:
                wandb.init(
                    project=self.config.wandb_project,
                    name=f"{self.config.wandb_run_name}-trainer-{self.config.wandb_run_suffix}",
                    group=self.wandb_group,
                    tags=["trainer"],
                )
                print(f"Wandb initialized (trainer): {wandb.run.name} in group: {self.wandb_group}")
            except Exception as e:
                print(f"Error initializing wandb: {e}")
                self.config.use_wandb = False

    async def _register_trainer(self) -> str:
        """Register this trainer with the Atropos API server."""
        url = f"{self.atropos_api_url}/register"

        payload = {
            "wandb_project": self.config.wandb_project,
            "wandb_group": self.wandb_group,
            "batch_size": self.config.batch_size,
            "max_token_len": self.config.max_token_trainer_length,
            "starting_step": 0,
            "checkpoint_dir": self.config.checkpoint_dir,
            "save_checkpoint_interval": self.config.save_checkpoint_interval,
            "num_steps": self.num_steps,
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("uuid")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
    def get_batch(self):
        """Fetch a batch of rollouts from Atropos API with retry logic."""
        data = requests.get(f"{self.atropos_api_url}/batch", timeout=10).json()
        return data

    @staticmethod
    def _validate_distil_field(field_data, field_name: str, seq_len: int):
        """
        Validate a distillation field has shape [seq_len, K].

        The API always uses 2D (seq_len, K) to support top-K distillation
        on torchtitan. Tinker only supports K=1 since forward_backward_custom
        only provides per-token logprobs — no full vocab distribution.

        Returns a squeezed 1D array of shape [seq_len] for Tinker consumption.
        """
        if field_data is None:
            return None

        arr = np.array(field_data)

        if arr.ndim == 1:
            raise ValueError(
                f"Distillation field '{field_name}' has shape {arr.shape} (1D). "
                f"Expected 2D shape [seq_len, K]. The distillation API always "
                f"uses [seq_len, K] format — pass K=1 for per-token distillation."
            )
        if arr.ndim != 2:
            raise ValueError(
                f"Distillation field '{field_name}' has unexpected ndim={arr.ndim}, "
                f"shape={arr.shape}. Expected 2D shape [seq_len, K]."
            )
        if arr.shape[0] != seq_len:
            raise ValueError(
                f"Distillation field '{field_name}' has {arr.shape[0]} positions "
                f"but expected {seq_len} (seq_len)."
            )
        if arr.shape[1] != 1:
            raise ValueError(
                f"Distillation field '{field_name}' has K={arr.shape[1]} (shape {arr.shape}). "
                f"Tinker only supports K=1 — its forward_backward_custom only provides "
                f"per-token logprobs, not full vocab distribution. "
                f"Use torchtitan for top-K distillation (K>1)."
            )

        # Squeeze to 1D for Tinker's per-token loss functions
        return arr.squeeze(axis=1)

    def pad_data_to_good_offset(
        self, data: Dict[str, Any]
    ) -> tuple[List[tinker.Datum], List[float], bool]:
        """
        Convert Atropos batch into Tinker Datums for training.

        Pads logprobs and advantages to align with token sequences:
        - Prompt tokens get 0.0 for logprobs and advantages (no gradient)
        - Generated tokens get actual logprobs and advantages

        When distillation data is present, per-token advantages are overwritten
        with (logp_teacher - logp_student) for on-policy distillation.
        Reference: https://thinkingmachines.ai/blog/on-policy-distillation/

        Returns:
            datums: List of Tinker Datum objects for training
            group_mean_rewards: Mean reward per group
            has_distil_data: Whether distillation data was present

        Distillation fields (optional, in each batch item):
            distill_token_ids: Teacher token IDs, shape [n_trajectories][seq_len][K].
                K=1 for Tinker (per-token only). K>1 errors here — use torchtitan.
            distill_logprobs: Teacher log-probabilities, shape [n_trajectories][seq_len][K].
                Same K constraint as distill_token_ids.
        """
        batch = data["batch"]

        datums = []
        group_mean_rewards = []
        all_reference_logprobs = []
        all_advantages = []
        has_distil_data = False
        skipped_count = 0
        # Distil-specific tracking
        all_teacher_logprobs = []
        all_student_logprobs_for_distil = []
        all_per_token_advantages = []

        for item in batch:
            # Calculate advantages
            scores = np.array(item["scores"])
            original_mean = np.mean(scores)
            advantages = scores - original_mean

            group_mean_rewards.append(original_mean)

            # Skip groups where all advantages are zero
            if len(scores) > 1 and np.all(advantages == 0.0):
                skipped_count += 1
                continue

            # Apply advantage overrides
            if item.get("overrides") is not None:
                for i in range(len(item["overrides"])):
                    if item["overrides"][i].get("set_advantage_to_zero", False):
                        advantages[i] = 0.0

            # Check for distillation data at the group level
            # Atropos uses "distill_" (double L) field names
            item_has_distil = (
                item.get("distill_token_ids") is not None
                and item.get("distill_logprobs") is not None
            )
            if item_has_distil:
                has_distil_data = True

            for i in range(len(item["tokens"])):
                tokens = item["tokens"][i]
                trajectory_logprobs = item["inference_logprobs"][i]
                advantage = advantages[i]

                all_advantages.append(advantage)

                input_tokens = tokens[:-1]
                target_tokens = tokens[1:]

                all_logprobs = trajectory_logprobs[1:]  # Shift right to align with targets

                all_advantages_padded = [0.0 if lp == 1.0 else advantage for lp in all_logprobs]

                all_reference_logprobs.extend(all_logprobs)

                seq_len = len(target_tokens)

                assert (
                    len(input_tokens) == seq_len == len(all_logprobs) == len(all_advantages_padded)
                ), f"Length mismatch: input={len(input_tokens)}, target={seq_len}, logprobs={len(all_logprobs)}, advantages={len(all_advantages_padded)}"

                # On-policy distillation: overwrite advantages with logp_t - logp_s
                # Reference: https://thinkingmachines.ai/blog/on-policy-distillation/
                if item_has_distil:
                    raw_distil_ids = item["distill_token_ids"][i]
                    raw_distil_lps = item["distill_logprobs"][i]

                    # These come as the full sequence; shift to align with targets
                    raw_distil_ids = (
                        raw_distil_ids[1:] if len(raw_distil_ids) > seq_len else raw_distil_ids
                    )
                    raw_distil_lps = (
                        raw_distil_lps[1:] if len(raw_distil_lps) > seq_len else raw_distil_lps
                    )

                    # Validate: must be 1D (per-token), not 2D (top-K)
                    self._validate_distil_field(raw_distil_ids, "distil_token_ids", seq_len)
                    distil_lps = self._validate_distil_field(
                        raw_distil_lps, "distil_logprobs", seq_len
                    )

                    # Overwrite advantages: per-token logp_teacher - logp_student
                    all_advantages_padded = [
                        0.0 if lp == 1.0 else float(t_lp - lp)
                        for lp, t_lp in zip(all_logprobs, distil_lps)
                    ]

                    # Track distil stats (non-prompt tokens only)
                    for lp, t_lp, adv in zip(all_logprobs, distil_lps, all_advantages_padded):
                        if lp != 1.0:  # skip prompt sentinel tokens
                            all_teacher_logprobs.append(float(t_lp))
                            all_student_logprobs_for_distil.append(float(lp))
                            all_per_token_advantages.append(adv)

                datum = tinker.Datum(
                    model_input=tinker.ModelInput.from_ints(tokens=input_tokens),
                    loss_fn_inputs={
                        "target_tokens": tinker.TensorData.from_torch(
                            torch.tensor(target_tokens, dtype=torch.int64)
                        ),
                        "logprobs": tinker.TensorData.from_torch(
                            torch.tensor(all_logprobs, dtype=torch.float32)
                        ),
                        "advantages": tinker.TensorData.from_torch(
                            torch.tensor(all_advantages_padded, dtype=torch.float32)
                        ),
                    },
                )
                datums.append(datum)

        # Calculate logprob stats
        if all_reference_logprobs:
            logprob_array = np.array(all_reference_logprobs)
            # Filter out both 0.0 and 1.0 (1.0 are placeholder values for prompt tokens)
            logprob_array_actual = logprob_array[(logprob_array != 0.0) & (logprob_array != 1.0)]
            if len(logprob_array_actual) > 0:
                self.logprob_stats = {
                    "logprobs/mean": float(np.mean(logprob_array_actual)),
                    "logprobs/std": float(np.std(logprob_array_actual)),
                    "logprobs/min": float(np.min(logprob_array_actual)),
                    "logprobs/p50": float(np.percentile(logprob_array_actual, 50)),
                }
            else:
                self.logprob_stats = {}
        else:
            self.logprob_stats = {}

        # Calculate advantage stats
        if all_advantages:
            advantages_array = np.array(all_advantages)
            if np.std(advantages_array) > 1e-6:
                self.advantage_stats = {
                    "advantages/mean": float(np.mean(advantages_array)),
                    "advantages/std": float(np.std(advantages_array)),
                    "advantages/sum": float(np.sum(advantages_array)),
                }
            else:
                self.advantage_stats = {}
        else:
            self.advantage_stats = {}

        # Calculate distillation stats
        if all_teacher_logprobs:
            teacher_arr = np.array(all_teacher_logprobs)
            student_arr = np.array(all_student_logprobs_for_distil)
            adv_arr = np.array(all_per_token_advantages)
            self.distil_stats = {
                "distil/teacher_logp_mean": float(np.mean(teacher_arr)),
                "distil/teacher_logp_std": float(np.std(teacher_arr)),
                "distil/teacher_logp_min": float(np.min(teacher_arr)),
                "distil/student_logp_mean": float(np.mean(student_arr)),
                "distil/student_logp_std": float(np.std(student_arr)),
                "distil/advantage_mean": float(np.mean(adv_arr)),
                "distil/advantage_std": float(np.std(adv_arr)),
                "distil/advantage_abs_mean": float(np.mean(np.abs(adv_arr))),
                "distil/kl_approx": float(np.mean(student_arr - teacher_arr)),
                "distil/num_tokens": len(all_teacher_logprobs),
            }
        else:
            self.distil_stats = {}

        if skipped_count > 0:
            print(f"Skipped {skipped_count} groups with zero advantages")

        return datums, group_mean_rewards, has_distil_data

    def get_data(self) -> tuple[List[tinker.Datum], bool]:
        """
        Poll Atropos for a batch of rollouts and convert to Tinker Datums.
        Waits until a batch is available.

        Returns:
            datums: List of Tinker Datum objects
            has_distil_data: Whether distillation data was present (advantages
                were overwritten with logp_teacher - logp_student)
        """
        import time
        import json

        while True:
            data = self.get_batch()

            if data.get("batch") is not None:
                with open("temp.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)

                datums, group_mean_rewards, has_distil = self.pad_data_to_good_offset(data)
                self.group_mean_rewards = group_mean_rewards
                return datums, has_distil
            else:
                time.sleep(1)

    async def train_step(self, step: int) -> Dict[str, Any]:
        """Execute one training step: fetch batch, forward-backward, optimizer step."""
        print(f"\n{'='*60}")
        print(f"Step {step}/{self.num_steps}")
        print(f"{'='*60}")

        step_start = time.time()
        metrics = {"step": step}

        # Fetch batch from Atropos
        print("Fetching data from Atropos...")
        data, has_distil = self.get_data()
        print(f"Got {len(data)} Datum objects")
        if has_distil:
            print("  with on-policy distillation (advantages = logp_t - logp_s)")
            if hasattr(self, "distil_stats") and self.distil_stats:
                ds = self.distil_stats
                print(
                    f"  teacher_logp={ds.get('distil/teacher_logp_mean', 0):.4f} "
                    f"student_logp={ds.get('distil/student_logp_mean', 0):.4f} "
                    f"adv_mean={ds.get('distil/advantage_mean', 0):.4f} "
                    f"kl≈{ds.get('distil/kl_approx', 0):.4f} "
                    f"({ds.get('distil/num_tokens', 0)} tokens)"
                )

        # Forward-backward pass (IS loss handles both RL and distillation —
        # when distillation is active, advantages were already overwritten
        # with per-token logp_teacher - logp_student)
        print("Running forward-backward pass...")
        fwd_bwd_result = await self.training_client.forward_backward_async(
            data, loss_fn="importance_sampling"
        )

        # Optimizer step
        print("Running optimizer step...")
        adam_params = AdamParams(learning_rate=self.learning_rate, beta1=0.9, beta2=0.95, eps=1e-8)
        optim_result = await self.training_client.optim_step_async(adam_params)

        # Await results
        if hasattr(fwd_bwd_result, "result_async"):
            fwd_bwd_result = await fwd_bwd_result.result_async()
        elif hasattr(fwd_bwd_result, "result"):
            fwd_bwd_result = fwd_bwd_result.result()
        optim_result = await optim_result.result_async()

        loss_val = (
            fwd_bwd_result.metrics["loss:sum"] if "loss:sum" in fwd_bwd_result.metrics else 0.0
        )

        print(f"Loss: {loss_val}")

        if has_distil:
            metrics["distil/active"] = 1

        # Calculate training logprob stats
        training_logprobs_all = []
        for datum, output in zip(data, fwd_bwd_result.loss_fn_outputs):
            training_logprobs = output["logprobs"].to_torch()
            advantages = datum.loss_fn_inputs["advantages"].to_torch()
            mask = advantages != 0.0
            training_lp_masked = training_logprobs[mask]
            training_logprobs_all.extend(training_lp_masked.cpu().numpy().tolist())

        if training_logprobs_all:
            training_lp_array = np.array(training_logprobs_all)
            self.training_logprob_stats = {
                "logprobs/mean_training": float(np.mean(training_lp_array)),
                "logprobs/std_training": float(np.std(training_lp_array)),
                "logprobs/min_training": float(np.min(training_lp_array)),
                "logprobs/p50_training": float(np.percentile(training_lp_array, 50)),
            }

            # Calculate logprob drift
            if hasattr(self, "logprob_stats") and "logprobs/mean" in self.logprob_stats:
                ref_mean = self.logprob_stats["logprobs/mean"]
                train_mean = float(np.mean(training_lp_array))
                self.training_logprob_stats["logprobs/diff"] = ref_mean - train_mean
        else:
            self.training_logprob_stats = {}

        # Update sampling client with new weights
        print("Saving checkpoint and updating sampling client...")
        new_path = (
            self.training_client.save_weights_for_sampler(name=f"step_{step+1}").result().path
        )
        self.current_sampling_client = self.service_client.create_sampling_client(
            model_path=new_path
        )
        print(f"Sampling client updated: {new_path}")

        step_time = time.time() - step_start
        metrics["step_time"] = step_time
        metrics["learning_rate"] = self.learning_rate
        metrics["loss"] = loss_val

        if self.group_mean_rewards:
            metrics["reward/mean"] = np.mean(self.group_mean_rewards)
            print(f"Reward/mean: {metrics['reward/mean']:.4f}")

        if self.config.use_wandb:
            wandb_metrics = {
                "train/loss": loss_val,
                "train/learning_rate": self.learning_rate,
                "reward/mean": metrics["reward/mean"],
            }

            if hasattr(self, "logprob_stats"):
                wandb_metrics.update(self.logprob_stats)
            if hasattr(self, "training_logprob_stats"):
                wandb_metrics.update(self.training_logprob_stats)
            if hasattr(self, "advantage_stats"):
                wandb_metrics.update(self.advantage_stats)

            if has_distil:
                wandb_metrics["distil/active"] = 1
            if hasattr(self, "distil_stats"):
                wandb_metrics.update(self.distil_stats)

            wandb.log(wandb_metrics, step=step + 1)

        return metrics

    async def run(self):
        """Main training loop."""
        print("\n" + "=" * 60)
        print("Starting Tinker-Atropos Training")
        print("=" * 60 + "\n")

        await self.setup()

        for step in range(self.num_steps):
            try:
                metrics = await self.train_step(step)
                print(f"\nStep {step} complete - Loss: {metrics.get('loss', 'N/A')}")
            except Exception as e:
                print(f"Error in step {step}: {e}")
                import traceback

                traceback.print_exc()
                break

        print("\n" + "=" * 60)
        print("Training complete!")
        print("=" * 60 + "\n")

        print(
            f"Final weights are available here: tinker://{str(self.training_client.model_id)}/sampler_weights/final"
        )


trainer: TinkerAtroposTrainer | None = None


def _trainer_not_ready_reason() -> str | None:
    if trainer is None:
        return "Trainer not initialized"
    if trainer.tokenizer is None:
        return "Trainer not ready: tokenizer not initialized yet"
    if trainer.current_sampling_client is None:
        return "Trainer not ready: sampling client not initialized yet"
    return None


# FastAPI server for Atropos environment to call for inference
app = FastAPI(title="Tinker-Atropos Service")


@app.get("/health")
async def health():
    """Health check endpoint."""
    ready_reason = _trainer_not_ready_reason()
    return {
        "status": "ok" if ready_reason is None else "starting",
        "trainer_initialized": trainer is not None,
        "trainer_ready": ready_reason is None,
        "detail": ready_reason,
    }


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest):
    """
    OpenAI-compatible completions endpoint.
    Called by inference server wrapper for regular completions (non-chat).
    """
    ready_reason = _trainer_not_ready_reason()
    if ready_reason is not None:
        raise HTTPException(status_code=503, detail=ready_reason)

    try:
        # Handle single prompt (string) or batch (list of strings)
        if isinstance(request.prompt, str):
            prompts = [request.prompt]
        else:
            prompts = request.prompt

        all_choices = []
        choice_index = 0

        for prompt in prompts:
            # Tokenize prompt
            prompt_tokens = trainer.tokenizer.encode(prompt, add_special_tokens=False)
            model_input = ModelInput.from_ints(prompt_tokens)

            # Generate using Tinker sampling client
            sampling_params = SamplingParams(
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stop=request.stop if request.stop else [],
            )

            result = await trainer.current_sampling_client.sample_async(
                prompt=model_input,
                sampling_params=sampling_params,
                num_samples=request.n,
            )

            # Format choices
            for sequence in result.sequences:
                output_text = trainer.tokenizer.decode(sequence.tokens, skip_special_tokens=True)
                all_choices.append(
                    {
                        "text": output_text,
                        "index": choice_index,
                        "finish_reason": "stop",
                    }
                )
                choice_index += 1

        return CompletionResponse(
            id=f"cmpl-{random.randint(0, 999999)}",
            choices=all_choices,
            created=int(time.time()),
            model=trainer.base_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completion failed: {str(e)}")


@app.get("/wandb_info")
async def wandb_info():
    if trainer is None:
        raise HTTPException(status_code=503, detail="Trainer not initialized")

    return {
        "group": trainer.wandb_group,
        "project": trainer.config.wandb_project,
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    Called by inference server wrapper for chat completions.
    """
    ready_reason = _trainer_not_ready_reason()
    if ready_reason is not None:
        raise HTTPException(status_code=503, detail=ready_reason)

    try:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Apply chat template and tokenize
        prompt_text = trainer.tokenizer.apply_chat_template(
            messages_dict, tokenize=False, add_generation_prompt=True
        )
        prompt_tokens = trainer.tokenizer.encode(prompt_text, add_special_tokens=False)
        model_input = ModelInput.from_ints(prompt_tokens)

        # Generate using Tinker sampling client
        sampling_params = SamplingParams(
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=request.stop if request.stop else [],
        )

        result = await trainer.current_sampling_client.sample_async(
            prompt=model_input,
            sampling_params=sampling_params,
            num_samples=request.n,
        )

        # Format as OpenAI response
        choices = []
        for i, sequence in enumerate(result.sequences):
            output_text = trainer.tokenizer.decode(sequence.tokens, skip_special_tokens=True)
            choices.append(
                {
                    "message": {
                        "role": "assistant",
                        "content": output_text,
                    },
                    "index": i,
                    "finish_reason": "stop",
                }
            )

        return ChatCompletionResponse(
            id=f"chatcmpl-{random.randint(0, 999999)}",
            choices=choices,
            created=int(time.time()),
            model=trainer.base_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@app.post("/generate", response_model=GenerateResponse | List[GenerateResponse])
async def generate(request: GenerateRequest):
    """
    /generate endpoint for ManagedServer.
    Called by ManagedServer with tokenized input_ids.
    Returns GenerateResponse for single completion (n=1) or List[GenerateResponse] for multiple (n>1).
    """
    ready_reason = _trainer_not_ready_reason()
    if ready_reason is not None:
        raise HTTPException(status_code=503, detail=ready_reason)

    try:
        # Extract input_ids (ManagedServer sends tokenized input)
        if request.input_ids is None:
            raise HTTPException(status_code=400, detail="input_ids is required")

        prompt_tokens = request.input_ids

        # Extract sampling params
        sampling_params = request.sampling_params or {}
        n = sampling_params.get("n", 1)
        max_tokens = sampling_params.get("max_new_tokens", 256)
        temperature = sampling_params.get("temperature", 1.0)
        stop = sampling_params.get("stop", [])

        # Generate using Tinker sampling client
        model_input = ModelInput.from_ints(prompt_tokens)
        tinker_sampling_params = SamplingParams(
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop if isinstance(stop, list) else [stop],
        )

        result = await trainer.current_sampling_client.sample_async(
            prompt=model_input,
            sampling_params=tinker_sampling_params,
            num_samples=n,
        )

        if n == 1:
            sequence = result.sequences[0]
            output_tokens = sequence.tokens
            output_logprobs = sequence.logprobs if sequence.logprobs else []
            output_text = trainer.tokenizer.decode(output_tokens, skip_special_tokens=True)

            output_token_logprobs = []
            for token_id, logprob in zip(output_tokens, output_logprobs):
                token_text = trainer.tokenizer.decode([token_id])
                output_token_logprobs.append((logprob, token_id, token_text))

            return GenerateResponse(
                text=output_text,
                meta_info={
                    "prompt_tokens": len(prompt_tokens),
                    "completion_tokens": len(output_tokens),
                    "finish_reason": "stop",
                    "output_token_logprobs": output_token_logprobs,
                },
            )
        else:
            # Multiple completions - return list of GenerateResponse objects
            results = []
            for sequence in result.sequences:
                output_tokens = sequence.tokens
                output_logprobs = sequence.logprobs if sequence.logprobs else []
                output_text = trainer.tokenizer.decode(output_tokens, skip_special_tokens=True)

                # Format logprobs for response
                output_token_logprobs = []
                for token_id, logprob in zip(output_tokens, output_logprobs):
                    token_text = trainer.tokenizer.decode([token_id])
                    output_token_logprobs.append((logprob, token_id, token_text))

                results.append(
                    GenerateResponse(
                        text=output_text,
                        meta_info={
                            "prompt_tokens": len(prompt_tokens),
                            "completion_tokens": len(output_tokens),
                            "finish_reason": "stop",
                            "output_token_logprobs": output_token_logprobs,
                        },
                    )
                )

            return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/logprobs", response_model=LogprobsResponse)
async def logprobs(request: LogprobsRequest):
    """
    Compute per-token log probabilities for input tokens without generation.

    Accepts either raw token IDs (input_ids) or text (which gets tokenized).
    Uses the current sampling client's compute_logprobs under the hood.
    """
    if trainer is None:
        raise HTTPException(status_code=503, detail="Trainer not initialized")

    try:
        # Resolve token IDs
        if request.input_ids is not None:
            token_ids = request.input_ids
        elif request.text is not None:
            token_ids = trainer.tokenizer.encode(request.text, add_special_tokens=False)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'input_ids' or 'text' must be provided",
            )

        if len(token_ids) == 0:
            raise HTTPException(status_code=400, detail="Input must have at least one token")

        model_input = ModelInput.from_ints(token_ids)
        prompt_lps = await trainer.current_sampling_client.compute_logprobs_async(model_input)

        token_logprobs = []
        for i, token_id in enumerate(token_ids):
            lp = prompt_lps[i] if i < len(prompt_lps) and prompt_lps[i] is not None else 0.0

            token_text = None
            if request.return_text:
                token_text = trainer.tokenizer.decode([token_id])

            token_logprobs.append(
                TokenLogprob(
                    token_id=token_id,
                    logprob=lp,
                    token=token_text,
                )
            )

        return LogprobsResponse(
            logprobs=token_logprobs,
            num_tokens=len(token_ids),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logprobs computation failed: {str(e)}")


def run_fastapi_server():
    """Run FastAPI server in background thread."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


async def main():
    global trainer

    config = TinkerAtroposConfig(
        lora_rank=int(os.getenv("LORA_RANK", "32")),
        learning_rate=float(os.getenv("LEARNING_RATE", "4e-5")),
        num_steps=50,
    )

    print(f"Using wandb run: {config.wandb_run_name}")

    trainer = TinkerAtroposTrainer(config)

    # Start FastAPI server in background thread for Atropos to call
    import threading

    server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    server_thread.start()

    print("Waiting for FastAPI server to start...")
    await asyncio.sleep(3)

    await trainer.run()


if __name__ == "__main__":
    asyncio.run(main())
