"""Regression tests for CLI / env-var config overrides.

The flat accessors on ``TinkerAtroposConfig`` (``lora_rank``, ``num_steps``,
``base_model`` ...) are read-only ``@property`` wrappers around the nested
``env`` / ``tinker`` fields, not model fields themselves. Passing them as
top-level kwargs let pydantic's default ``extra="ignore"`` silently drop them,
so both the ``--lora-rank`` style CLI flags and the ``LORA_RANK`` /
``LEARNING_RATE`` env vars had no effect. These tests pin the fix.
"""

import sys
from argparse import Namespace
from pathlib import Path

# launch_training.py lives at the repo root, next to the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from launch_training import load_config  # noqa: E402
from tinker_atropos.trainer import build_config_from_env  # noqa: E402


def _args(**overrides) -> Namespace:
    defaults = dict(
        config=None,
        base_model=None,
        lora_rank=None,
        learning_rate=None,
        num_steps=None,
        batch_size=None,
        group_size=None,
        wandb_project=None,
        wandb_group=None,
        no_wandb=False,
    )
    defaults.update(overrides)
    return Namespace(**defaults)


class TestCLIOverrides:
    def test_overrides_reach_nested_fields(self):
        config = load_config(
            _args(
                base_model="OVERRIDDEN",
                lora_rank=64,
                learning_rate=1e-3,
                num_steps=7,
                batch_size=4,
                group_size=2,
                wandb_project="proj",
                wandb_group="grp",
                no_wandb=True,
            )
        )
        # Values must land on the real nested fields (and be visible via the
        # convenience properties), not be silently discarded.
        assert config.base_model == "OVERRIDDEN"
        assert config.env.tokenizer_name == "OVERRIDDEN"
        assert config.lora_rank == 64
        assert config.tinker.lora_rank == 64
        assert config.learning_rate == 1e-3
        assert config.num_steps == 7
        assert config.env.total_steps == 7
        assert config.batch_size == 4
        assert config.group_size == 2
        assert config.wandb_project == "proj"
        assert config.wandb_group == "grp"
        assert config.use_wandb is False

    def test_no_overrides_keeps_defaults(self):
        config = load_config(_args())
        assert config.lora_rank == 32
        assert config.num_steps == 50
        assert config.use_wandb is True


class TestEnvOverrides:
    def test_env_vars_reach_nested_fields(self, monkeypatch):
        monkeypatch.setenv("LORA_RANK", "128")
        monkeypatch.setenv("LEARNING_RATE", "2e-4")
        config = build_config_from_env()
        assert config.lora_rank == 128
        assert config.learning_rate == 2e-4
        assert config.num_steps == 50

    def test_env_defaults_when_unset(self, monkeypatch):
        monkeypatch.delenv("LORA_RANK", raising=False)
        monkeypatch.delenv("LEARNING_RATE", raising=False)
        config = build_config_from_env()
        assert config.lora_rank == 32
        assert config.learning_rate == 4e-5
