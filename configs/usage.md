# Tinker-Atropos Configuration Files

This directory contains YAML configuration files for the Tinker-Atropos training system. Config files provide an easy way to manage different training environments and can be combined with CLI overrides.

## Available Configurations

### `default.yaml`
Standard configuration suitable for typical training runs. This config demonstrates all available options with reasonable defaults.

**Use case**: Regular training experiments with moderate resources

### `default_public_normal_lite.yaml`
Lighter public-model configuration for repeatable local proof runs on the canonical GSM8k path.

**Features**:
- Public `Qwen/Qwen3-8B` model
- Lower batch, group, worker, and step counts than `default.yaml`
- Wandb disabled by default to reduce local friction
- Pairs well with `run_default_public_ready_smoke.py`

**Use case**: Stable local proof bundles and lower-cost public-model validation before longer default runs

### `quick_test.yaml`
Minimal resource configuration optimized for rapid testing and debugging.

**Features**:
- Smaller 1B model and shorter training steps
- Keeps the default batch/token settings, so it mainly reduces cost through model size, step count, and disabled wandb
- Wandb disabled by default
- Ideal for validating setup and code changes

**Use case**: Local testing, debugging, CI/CD pipelines

### `smoke_qwen_instruct_g4_steps3.yaml`
Bounded public-model smoke configuration for fast validation with an instruct-tuned Qwen model.

**Features**:
- Qwen3-4B-Instruct model with a tiny 3-step run
- Lower batch, group, and worker counts than the default config
- Wandb disabled by default

**Use case**: Cheap public-model smoke validation before larger training runs

## Configuration Parameters

### Tinker Model Configuration
- `base_model`: HuggingFace model identifier (default: "Qwen/Qwen3-8B")
- `lora_rank`: Rank of LoRA adapters (default: 32)
- `learning_rate`: Optimizer learning rate (default: 0.00004)

### Training Configuration
- `num_steps`: Total number of training steps (default: 100)
- `batch_size`: Number of datums per training batch (default: 128)
- `group_size`: Number of rollouts generated per question (default: 16)
- `max_token_env_length`: Maximum tokens for environment rollouts (default: 256)
- `max_token_trainer_length`: Maximum tokens for trainer processing (default: 2048)
- `max_num_workers`: Maximum parallel workers for rollout generation (calculated as (batch_size * num_offpolicy // group_size)) (default: 24)
- `max_batches_offpolicy`: Maximum batches before data considered stale (default: 3)

### Weights & Biases Configuration
- `use_wandb`: Enable/disable wandb logging (default: true)
- `wandb_project`: Wandb project name (default: "atropos-tinker")
- `wandb_group`: Wandb group name for organizing runs (default: null, auto-generated)
- `wandb_run_name`: Base name for wandb runs (default: "atropos-tinker-run")
- `wandb_run_suffix`: Random suffix for unique run names (auto-generated)

### API Endpoints
- `atropos_api_url`: URL for Atropos rollout server (default: "http://localhost:8000")
- `inference_api_url`: URL for unified trainer inference endpoint (default: "http://localhost:8001")

### Evaluation
- `steps_per_eval`: Steps between evaluation runs (default: 100)
- `num_requests_for_eval`: Number of requests per evaluation (default: 256)

### Debug Options
- `ensure_scores_are_not_same`: Validate that scores differ within groups (default: false)

## Usage Examples

### Basic Usage
```bash
# Use default config
python launch_training.py --config configs/default.yaml

# Use normal-lite public proof config
python launch_training.py --config configs/default_public_normal_lite.yaml

# Use quick test config
python launch_training.py --config configs/quick_test.yaml
```

### With CLI Overrides
```bash
# Override specific parameters
python launch_training.py --config configs/default.yaml \
    --num-steps 50 \
    --batch-size 64 \
    --no-wandb

# Change model and adjust hyperparameters
python launch_training.py --config configs/quick_test.yaml \
    --base-model "meta-llama/Llama-3.2-1B-Instruct" \
    --learning-rate 0.0001
```

### Programmatic Usage
```python
from tinker_atropos.config import TinkerAtroposConfig

# Load from YAML
config = TinkerAtroposConfig.from_yaml("configs/quick_test.yaml")

# Modify programmatically
config.num_steps = 500
config.use_wandb = True

# Use with trainer
from tinker_atropos.trainer import TinkerAtroposTrainer
trainer = TinkerAtroposTrainer(config=config)
```

## Creating Custom Configs

To create a new configuration:

1. Copy an existing config file as a template
2. Modify parameters as needed
3. Save with a descriptive name (e.g., `configs/my_experiment.yaml`)
4. Run with: `python launch_training.py --config configs/my_experiment.yaml`

### Example Custom Config

```yaml
# configs/my_custom_config.yaml
base_model: "meta-llama/Llama-3.2-3B-Instruct"
lora_rank: 48
learning_rate: 0.00005

num_steps: 200
batch_size: 96
group_size: 24

use_wandb: true
wandb_project: "my-custom-experiment"
wandb_run_name: "custom-run"

checkpoint_dir: "./my_checkpoints/"
save_checkpoint_interval: 50
```

## Configuration Priority

When parameters are specified in multiple places, the priority order is:

1. **CLI arguments** (highest priority)
2. **YAML config file**
3. **Environment variables** (with `TINKER_ATROPOS_` prefix)
4. **Default values** (lowest priority)

Example:
```bash
# YAML has num_steps: 100
# CLI overrides to 50
python launch_training.py --config configs/default.yaml --num-steps 50
# Result: num_steps = 50
```

## Environment Variables

All config parameters can be set via environment variables with the `TINKER_ATROPOS_` prefix:

```bash
export TINKER_ATROPOS_BASE_MODEL="meta-llama/Llama-3.2-1B-Instruct"
export TINKER_ATROPOS_NUM_STEPS=200
export TINKER_ATROPOS_USE_WANDB=true

python launch_training.py
```

## Tips

- Start with `quick_test.yaml` to validate your setup
- Use `default_public_normal_lite.yaml` when you want a cheaper canonical public-model proof lane
- Use `default.yaml` as a template for custom configs
- Enable wandb logging for runs to track metrics
- Adjust `max_num_workers` based on your batch size, group size, and max_batches_offpolicy value
- Use CLI overrides for one-off experiments without creating new config files
