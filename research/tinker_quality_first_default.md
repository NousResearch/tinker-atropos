# Tinker-Atropos Quality-First Default

## Scope and evidence

This recommendation is grounded in the current main working tree rather than the narrower autoresearch recovery worktree. For a repository-level default, the most relevant generic candidates currently visible here are:

- `configs/default.yaml`
- `configs/smoke_qwen_instruct_g4_steps3.yaml`
- `configs/quick_test.yaml`

The `min_*` family is excluded from the default comparison because those files are domain-specific environment lanes for custom Hermes workflows, not the general-purpose starting point implied by the repo README. Other smoke variants are also excluded because the instruct smoke file is the clearest beginner-facing public-model smoke lane among the newly added local configs.

## Candidate comparison

| Candidate | Config | Quality signal | Cost / scale note | Beginner repeatability |
| --- | --- | --- | --- | --- |
| Canonical 8B default | `configs/default.yaml` | Uses public `Qwen/Qwen3-8B` with `total_steps: 50`, so it keeps an 8B quality lane while removing the gated-model blocker from the canonical path. | Highest cost of the compared configs: 8B model, 50-step run, and wandb enabled. | Best documented path because the README quickstart already points to this config directly. |
| Public instruct smoke lane | `configs/smoke_qwen_instruct_g4_steps3.yaml` | Uses `Qwen/Qwen3-4B-Instruct-2507` with instruct tuning and clean config naming, but only `total_steps: 3`, so it is a validation lane more than a quality-first default. | Much cheaper and easier to start than the default: 4B model, tiny batch/group size, and wandb disabled. | Good beginner repeatability for first smoke runs because it is bounded and cheap, but it is too short to be the default quality lane. |
| Quick test lane | `configs/quick_test.yaml` | Uses `meta-llama/Llama-3.2-1B` and `total_steps: 10`, so it is the weakest quality candidate of the three. | Cheapest debug-oriented lane of the compared configs: smaller 1B model and no wandb. | Very easy to rerun, but it is more of a setup/debug path than a default operating recommendation. |

## Recommended default

Recommend `configs/default.yaml` as the quality-first default operating setup.

It is the best fit for the current goal because result quality comes first, and `configs/default.yaml` is the only generic repo-level option here that pairs a stronger 8B public model with a materially longer 50-step training window. Beginner repeatability is better than before because the canonical README path no longer depends on gated Hugging Face access.

## Recommended lighter proof lane

For repeatable local proof runs where the goal is fast evidence rather than a long default experiment, use:
- `configs/default_public_normal_lite.yaml`
- `run_default_public_ready_smoke.py`

This lane keeps the same public `Qwen/Qwen3-8B` family but reduces batch, group, worker, and step counts so the canonical path can be revalidated more cheaply and with clearer local proof artifacts.

## Exclusions and risks

- Excluded the `min_*` configs from the default recommendation because they are environment-specific lanes for custom business/X/landing/retention/research workflows, not the generic starting point for the repository as a whole.
- Excluded `configs/smoke_qwen.yaml` and `configs/smoke_qwen_g4_steps3.yaml` from the final three-way comparison because `configs/smoke_qwen_instruct_g4_steps3.yaml` is the clearer public instruct smoke lane for beginner validation.
- `configs/usage.md` still describes `quick_test.yaml` as if it reduces batch size and token lengths, but the file currently keeps `batch_size: 128`, `group_size: 16`, `max_token_length: 256`, and `max_num_workers: 24`, so the docs are partially out of sync.
- `quick_test.yaml` uses `ensure_scores_not_the_same`, while the rest of the repo and the config schema convention use `ensure_scores_are_not_same`; that mismatch reinforces treating it as a debug lane rather than the default contract.

## Minimal validation plan

1. Run one README-style startup sequence with `configs/default.yaml` and confirm trainer setup, Atropos registration, and first-step progress.
2. Run one bounded smoke pass with `configs/smoke_qwen_instruct_g4_steps3.yaml` to preserve a cheap public-model validation lane and compare operator friction against the default path.
3. Align `configs/usage.md` with the actual `quick_test.yaml` values before promoting that config as a beginner-facing recommendation beyond setup/debug use.
