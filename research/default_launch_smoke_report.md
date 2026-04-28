# Default Launch Smoke Report

## Scope

This report records the most recent real smoke attempt for `configs/default.yaml`.

The goal was to verify the README-style startup sequence:

1. `run-api`
2. `python launch_training.py --config configs/default.yaml`
3. `python tinker_atropos/environments/gsm8k_tinker.py serve --config configs/default.yaml`

## Outcome summary

- `run-api`: local startup succeeded from a repo-local virtual environment in a clean clone
- trainer smoke: startup reached local inference wiring, then failed because `TINKER_API_KEY` was not set
- environment smoke: the earlier gated-model failure was tied to `meta-llama/Llama-3.1-8B-Instruct`; the default config has now been moved to a public `Qwen/Qwen3-8B` path to remove that blocker

## Local fixes completed during follow-up

- Fixed `TinkerAtroposConfig.inference_api_url` so `http://localhost:8001/v1` no longer truncates to `http://localhost:800`
- Added regression tests for inference API URL normalization
- Aligned `configs/quick_test.yaml` with the current schema key `ensure_scores_are_not_same`
- Updated docs and research artifacts to reflect the current recommended quality-first default and the smoke result

## External blockers still unresolved

- `TINKER_API_KEY` is still required for trainer startup, but it is now present in `~/.hermes/.env`
- the gated Hugging Face model blocker has been removed by switching the canonical default path to public `Qwen/Qwen3-8B`

## Latest validation after the public-model switch

A fresh README-style rerun was completed against `configs/default.yaml` with the current local credentials loaded.

Observed trainer proof:
- `Base Model: Qwen/Qwen3-8B`
- `Loaded tokenizer for Qwen/Qwen3-8B`
- `Registered as trainer: ...`
- `Step 0/50`
- `Got 32 Datum objects`
- `Loss: 122.31032180786133`
- `Reward/mean: 0.0781`

Observed rollout-server proof:
- repeated `POST /scored_data HTTP/1.1 200 OK`
- `GET /batch HTTP/1.1 200 OK`

This shows the canonical default path is no longer blocked by gated model access and can reach real first-step training progress.

## Practical next step

With the gated-model bottleneck removed, the next useful follow-up is to capture a clean file-backed three-process proof bundle for the default path.

A dedicated runner now exists for this:
- `run_default_public_ready_smoke.py`

For a lighter canonical proof lane, use:
- `DEFAULT_PUBLIC_READY_CONFIG=configs/default_public_normal_lite.yaml python run_default_public_ready_smoke.py`

The runner records:
- `assessment.status`
- `trainer_progress_seen`
- `trainer.last_step`
- `trainer.got_datum_objects`
- `trainer.reward_mean`
- `environment_summary.connect_8000_failed`
- `trainer_active_before_cleanup`, `env_active_before_cleanup`, `run_api_active_before_cleanup`
- `cleanup_applied`
- `saved_artifacts.json`, `saved_artifacts.markdown`

Interpretation rule:
- if `assessment.status == "working"`, then later `*_returncode_final = -9` only means the runner deliberately cleaned up the still-running processes after proof collection
- do not misread those cleanup kills as the root cause of the run
