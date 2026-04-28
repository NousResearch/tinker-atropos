from __future__ import annotations

import os
import random
import re
import time
from typing import Dict, List, Optional, Tuple, TypedDict, Union

try:
    from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
    from atroposlib.type_definitions import Item
    from tinker_atropos.config import TinkerAtroposConfig
except ModuleNotFoundError:  # Allows local evaluator tests without the RL runtime installed.
    APIServerConfig = None
    BaseEnv = None
    BaseEnvConfig = None
    ScoredDataGroup = dict
    Item = dict
    TinkerAtroposConfig = None

CONFIG_PATH = "configs/default.yaml"

IMAGE_REQUIRED_FIELDS = [
    "Template",
    "Modality",
    "Prompt",
    "Visual Details",
    "Composition",
    "Style",
    "Constraints",
    "Negative Constraints",
    "Note References",
    "Readiness Rationale",
]

VIDEO_REQUIRED_FIELDS = [
    "Template",
    "Modality",
    "Shot Plan",
    "Camera Motion",
    "Temporal Structure",
    "Constraints",
    "Negative Constraints",
    "Note References",
    "Readiness Rationale",
]

PLACEHOLDER_PATTERNS = [
    "todo",
    "tbd",
    "[insert",
    "<insert",
    "your prompt here",
    "make it good",
    "멋지게",
]

LIVE_GENERATION_PATTERNS = [
    "call gpt-image-2",
    "call seedance",
    "generate image",
    "generate video",
    "run seedance",
    "이미지 생성 실행",
    "영상 생성 실행",
]

DETAIL_TERMS = [
    "lighting",
    "camera",
    "lens",
    "composition",
    "foreground",
    "background",
    "palette",
    "motion",
    "shot",
    "frame",
    "장면",
    "구도",
    "조명",
    "카메라",
    "움직임",
    "색감",
]

MIN_GENERATED_TOKENS = 8


class ObsidianNoteStub(TypedDict):
    note_id: str
    title: str
    tags: List[str]
    frontmatter: Dict[str, str]
    links: List[str]
    guidance_terms: List[str]


class PromptPlanningItem(TypedDict):
    task_id: str
    modality: str
    user_request: str
    template_ids: List[str]
    selected_notes: List[ObsidianNoteStub]
    required_guidance_terms: List[str]


PROMPT_PLANNING_ITEMS: List[PromptPlanningItem] = [
    {
        "task_id": "image-editorial-product-hero",
        "modality": "image",
        "user_request": "Plan a GPT-image-2 prompt for a premium desk setup hero image.",
        "template_ids": ["image_prompt_v1", "video_shot_plan_v1"],
        "selected_notes": [
            {
                "note_id": "obs-img-hero-001",
                "title": "Image hero prompt rules",
                "tags": ["gpt-image-2", "prompt-template", "hero"],
                "frontmatter": {"modality": "image", "quality": "approved"},
                "links": ["style-lighting", "negative-constraints"],
                "guidance_terms": ["lighting", "composition", "negative constraints"],
            }
        ],
        "required_guidance_terms": ["lighting", "composition", "negative constraints"],
    },
    {
        "task_id": "video-short-product-reveal",
        "modality": "video",
        "user_request": "Plan a Seedance 2.0 shot sequence for a short product reveal.",
        "template_ids": ["image_prompt_v1", "video_shot_plan_v1"],
        "selected_notes": [
            {
                "note_id": "obs-video-shot-001",
                "title": "Seedance shot planning rules",
                "tags": ["seedance-2.0", "shot-plan", "motion"],
                "frontmatter": {"modality": "video", "quality": "approved"},
                "links": ["camera-motion", "temporal-structure"],
                "guidance_terms": ["camera motion", "temporal structure", "constraints"],
            }
        ],
        "required_guidance_terms": ["camera motion", "temporal structure", "constraints"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _lower(text: str) -> str:
    return _normalize_text(text).lower()


def extract_field_map(answer: str) -> Dict[str, str]:
    labels = IMAGE_REQUIRED_FIELDS + [field for field in VIDEO_REQUIRED_FIELDS if field not in IMAGE_REQUIRED_FIELDS]
    labels_pattern = "|".join(re.escape(label) for label in labels)
    pattern = re.compile(rf"^({labels_pattern})\s*:\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(answer))
    fields: Dict[str, str] = {}
    for index, match in enumerate(matches):
        field_name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(answer)
        body = _normalize_text(match.group(2) + " " + answer[start:end])
        fields[field_name] = body.strip()
    return fields


def _coverage(text: str, terms: List[str]) -> float:
    if not terms:
        return 1.0
    lowered = _lower(text)
    hits = sum(1 for term in terms if term.lower() in lowered)
    return hits / len(terms)


def _has_any(text: str, patterns: List[str]) -> bool:
    lowered = _lower(text)
    return any(pattern.lower() in lowered for pattern in patterns)


def _required_fields_for_modality(modality: str) -> List[str]:
    return VIDEO_REQUIRED_FIELDS if modality == "video" else IMAGE_REQUIRED_FIELDS


def format_prompt_planning_prompt(item: PromptPlanningItem) -> str:
    note_lines = []
    for note in item["selected_notes"]:
        note_lines.append(
            f"- {note['note_id']} | tags={','.join(note['tags'])} | "
            f"frontmatter={note['frontmatter']} | links={','.join(note['links'])} | "
            f"guidance={', '.join(note['guidance_terms'])}"
        )
    required_fields = "\n".join(f"{field}:" for field in _required_fields_for_modality(item["modality"]))
    return (
        "Create a text-only generation-ready prompt plan. Do not call image/video generation APIs.\n\n"
        f"User request: {item['user_request']}\n"
        f"Target modality: {item['modality']}\n"
        f"Available templates: {', '.join(item['template_ids'])}\n"
        "Selected synthetic Obsidian metadata:\n"
        + "\n".join(note_lines)
        + "\n\nUse the exact fields below:\n"
        + required_fields
        + "\n"
    )


def score_prompt_planning_answer(answer: str, item: PromptPlanningItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    fields = extract_field_map(answer)
    required_fields = _required_fields_for_modality(item["modality"])

    field_coverage = sum(1 for field in required_fields if fields.get(field)) / len(required_fields)

    template_text = fields.get("Template", "")
    template_conformance = 1.0 if any(template_id.lower() in template_text.lower() for template_id in item["template_ids"]) else 0.0
    modality_text = fields.get("Modality", "")
    if item["modality"] not in modality_text.lower():
        template_conformance *= 0.5

    note_text = fields.get("Note References", "") + " " + normalized
    note_ids = [note["note_id"] for note in item["selected_notes"]]
    tag_terms = [tag for note in item["selected_notes"] for tag in note["tags"]]
    note_grounding = min(1.0, 0.65 * _coverage(note_text, note_ids) + 0.35 * _coverage(note_text, tag_terms[:4]))

    guidance_text = normalized + " " + " ".join(fields.values())
    guidance_coverage = _coverage(guidance_text, item["required_guidance_terms"])

    detail_hits = sum(1 for term in DETAIL_TERMS if term.lower() in lowered)
    length_bonus = 1.0 if len(normalized) >= 280 else max(0.0, len(normalized) / 280)
    specificity = min(1.0, 0.10 * detail_hits + 0.45 * length_bonus + 0.45 * guidance_coverage)

    constraints_present = bool(fields.get("Constraints")) and bool(fields.get("Negative Constraints"))
    constraint_hygiene = 1.0 if constraints_present else 0.35 if fields.get("Constraints") or fields.get("Negative Constraints") else 0.0

    readiness_text = fields.get("Readiness Rationale", "")
    readiness_terms = ["ready", "direct", "complete", "generation", "검토", "바로", "완성"]
    tool_readiness = min(1.0, 0.55 * (1.0 if readiness_text else 0.0) + 0.45 * _coverage(readiness_text, readiness_terms))

    placeholder_penalty = 0.25 if _has_any(answer, PLACEHOLDER_PATTERNS) else 0.0
    live_generation_penalty = 0.35 if _has_any(answer, LIVE_GENERATION_PATTERNS) else 0.0
    wrong_modality_penalty = 0.25 if (item["modality"] == "image" and "video_shot_plan" in lowered) or (item["modality"] == "video" and "image_prompt" in lowered and "video_shot_plan" not in lowered) else 0.0

    total = (
        0.18 * field_coverage
        + 0.16 * template_conformance
        + 0.18 * specificity
        + 0.18 * note_grounding
        + 0.15 * tool_readiness
        + 0.15 * constraint_hygiene
        - placeholder_penalty
        - live_generation_penalty
        - wrong_modality_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "field_coverage": field_coverage,
        "template_conformance": template_conformance,
        "specificity": specificity,
        "note_grounding": note_grounding,
        "tool_readiness": tool_readiness,
        "constraint_hygiene": constraint_hygiene,
        "placeholder_penalty": -placeholder_penalty,
        "live_generation_penalty": -live_generation_penalty,
        "wrong_modality_penalty": -wrong_modality_penalty,
    }


def generation_max_tokens(configured_max: int) -> int:
    return min(int(configured_max), 1024)


if BaseEnv is not None:

    class MinImageVideoPromptPlanningEnv(BaseEnv):
        """Text-only prompt/shot-plan readiness environment using synthetic Obsidian metadata."""

        name = "min_image_video_prompt_planning"

        def __init__(self, config: BaseEnvConfig, server_configs: List[APIServerConfig], slurm: bool = True, testing: bool = False):
            super().__init__(config, server_configs, slurm, testing)
            self.percent_correct_buffer = []
            self.eval_metrics = []
            self.items = PROMPT_PLANNING_ITEMS
            self.iter = 0

        @classmethod
        def config_init(cls) -> Tuple[BaseEnvConfig, List[APIServerConfig]]:
            config = TinkerAtroposConfig.from_yaml(CONFIG_PATH) if CONFIG_PATH else TinkerAtroposConfig()
            env_config = BaseEnvConfig(
                tokenizer_name=config.base_model,
                group_size=config.group_size,
                use_wandb=config.use_wandb,
                rollout_server_url=config.atropos_api_url,
                total_steps=config.num_steps,
                batch_size=config.batch_size,
                steps_per_eval=config.steps_per_eval,
                max_token_length=config.max_token_env_length,
                max_num_workers=config.max_num_workers,
                max_batches_offpolicy=config.max_batches_offpolicy,
                wandb_name=f"{config.wandb_run_name}-env",
                ensure_scores_are_not_same=False,
            )
            server_configs = [
                APIServerConfig(
                    model_name=config.base_model,
                    base_url=config.inference_api_url + "/v1",
                    api_key="x",
                    server_type="sglang",
                    num_requests_for_eval=config.num_requests_for_eval,
                )
            ]
            return env_config, server_configs

        async def setup(self):
            if self.tokenizer.chat_template is None:
                self.tokenizer.chat_template = (
                    "{% for message in messages %}"
                    "{% if message['role'] == 'user' %}"
                    "{{ '<|start_header_id|>user<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}"
                    "{% elif message['role'] == 'assistant' %}"
                    "{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}"
                    "{% endif %}"
                    "{% if loop.last and message['role'] != 'assistant' %}"
                    "{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' }}"
                    "{% endif %}"
                    "{% endfor %}"
                )

        async def wandb_log(self, wandb_metrics: Optional[Dict] = None):
            wandb_metrics = wandb_metrics or {}
            if self.percent_correct_buffer:
                wandb_metrics["train/percent_correct"] = sum(self.percent_correct_buffer) / len(self.percent_correct_buffer)
            self.percent_correct_buffer = []
            for item in self.eval_metrics:
                wandb_metrics[item[0]] = item[1]
            self.eval_metrics = []
            await super().wandb_log(wandb_metrics)

        async def collect_trajectories(self, item: PromptPlanningItem) -> Tuple[ScoredDataGroup, List[Item]]:
            user_message = {"role": "user", "content": format_prompt_planning_prompt(item)}
            async with self.server.managed_server(tokenizer=self.tokenizer) as managed:
                chat_completion = await managed.chat_completion(
                    messages=[user_message],
                    n=self.config.group_size,
                    max_tokens=generation_max_tokens(self.config.max_token_length),
                    temperature=1.0,
                )
                nodes = managed.get_state()["nodes"]
            to_score = []
            for choice, node in zip(chat_completion.choices, nodes):
                to_score.append(
                    {
                        "messages": (user_message, {"role": "assistant", "content": choice.message.content}),
                        "item": item,
                        "finish_reason": choice.finish_reason,
                        "tokens": node.tokens,
                        "masked_tokens": node.masked_tokens,
                        "logprobs": node.logprobs,
                    }
                )
            return await self.score(to_score), []

        async def score(self, rollout_group_data) -> Union[Optional[ScoredDataGroup], List[Optional[ScoredDataGroup]]]:
            scores = ScoredDataGroup()
            scores["tokens"] = []
            scores["masks"] = []
            scores["scores"] = []
            scores["inference_logprobs"] = []
            random.shuffle(rollout_group_data)
            for item in rollout_group_data:
                reward_info = score_prompt_planning_answer(item["messages"][-1]["content"], item["item"])
                masked_tokens = item["masked_tokens"]
                if len([token for token in masked_tokens if token != -100]) < MIN_GENERATED_TOKENS:
                    continue
                scores["tokens"].append(item["tokens"])
                scores["masks"].append(masked_tokens)
                scores["inference_logprobs"].append(item["logprobs"])
                scores["scores"].append(float(reward_info["total"]))
                self.percent_correct_buffer.append(1.0 if reward_info["total"] >= 0.8 else 0.0)
                if len(scores["tokens"]) >= self.config.group_size:
                    break
            return scores if scores["scores"] else None

        async def rollout_and_score_eval(self, item: PromptPlanningItem) -> Dict[str, object]:
            completion = await self.server.chat_completion(
                messages=[{"role": "user", "content": format_prompt_planning_prompt(item)}],
                n=1,
                max_tokens=generation_max_tokens(self.config.max_token_length),
                temperature=0.0,
                split="eval",
            )
            response_content = completion.choices[0].message.content
            reward_info = score_prompt_planning_answer(response_content, item)
            return {
                "score": reward_info["total"],
                "sample": {
                    "prompt": item["user_request"],
                    "answer": response_content,
                    "score": reward_info["total"],
                    "details": reward_info,
                    "finish_reason": completion.choices[0].finish_reason,
                },
            }

        async def evaluate(self, *args, **kwargs):
            start_time = time.time()
            results = [await self.rollout_and_score_eval(item) for item in self.items]
            mean_score = sum(result["score"] for result in results) / len(results)
            self.eval_metrics.append(("eval/mean_score", mean_score))
            await self.evaluate_log(
                metrics={"eval/mean_score": mean_score},
                samples=[result["sample"] for result in results],
                start_time=start_time,
                end_time=time.time(),
                generation_parameters={"temperature": 0.0, "max_tokens": generation_max_tokens(self.config.max_token_length)},
            )

        async def get_next_item(self) -> PromptPlanningItem:
            next_item = self.items[self.iter % len(self.items)]
            self.iter += 1
            return next_item

else:

    class MinImageVideoPromptPlanningEnv:
        name = "min_image_video_prompt_planning"

        @classmethod
        def cli(cls):
            raise RuntimeError("atroposlib is required to run the environment CLI")


if __name__ == "__main__":
    MinImageVideoPromptPlanningEnv.cli()
