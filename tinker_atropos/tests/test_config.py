from pathlib import Path

import yaml

from tinker_atropos.config import OpenAIServerConfig, TinkerAtroposConfig


def test_inference_api_url_strips_single_v1_suffix_without_truncating_port():
    config = TinkerAtroposConfig(
        openai=[OpenAIServerConfig(model_name="model", base_url="http://localhost:8001/v1")]
    )

    assert config.inference_api_url == "http://localhost:8001"


def test_inference_api_url_handles_trailing_slash():
    config = TinkerAtroposConfig(
        openai=[OpenAIServerConfig(model_name="model", base_url="http://localhost:8001/v1/")]
    )

    assert config.inference_api_url == "http://localhost:8001"


def test_inference_api_url_preserves_non_v1_paths():
    config = TinkerAtroposConfig(
        openai=[OpenAIServerConfig(model_name="model", base_url="http://localhost:8100/custom")]
    )

    assert config.inference_api_url == "http://localhost:8100/custom"


def test_quick_test_yaml_uses_current_schema_key():
    repo_root = Path(__file__).resolve().parents[2]
    quick_test_path = repo_root / "configs" / "quick_test.yaml"
    raw = yaml.safe_load(quick_test_path.read_text(encoding="utf-8"))

    assert "ensure_scores_are_not_same" in raw["env"]
    assert "ensure_scores_not_the_same" not in raw["env"]

    config = TinkerAtroposConfig.from_yaml(quick_test_path)

    assert config.ensure_scores_are_not_same is False


def test_default_config_uses_public_qwen_model_by_default():
    config = TinkerAtroposConfig()

    assert config.base_model == "Qwen/Qwen3-8B"
    assert config.openai[0].model_name == "Qwen/Qwen3-8B"


def test_default_yaml_uses_public_qwen_model():
    repo_root = Path(__file__).resolve().parents[2]
    default_path = repo_root / "configs" / "default.yaml"
    raw = yaml.safe_load(default_path.read_text(encoding="utf-8"))

    assert raw["env"]["tokenizer_name"] == "Qwen/Qwen3-8B"
    assert raw["openai"][0]["model_name"] == "Qwen/Qwen3-8B"


def test_default_public_normal_lite_yaml_uses_public_qwen_model_and_lighter_settings():
    repo_root = Path(__file__).resolve().parents[2]
    normal_lite_path = repo_root / "configs" / "default_public_normal_lite.yaml"
    raw = yaml.safe_load(normal_lite_path.read_text(encoding="utf-8"))

    assert raw["env"]["tokenizer_name"] == "Qwen/Qwen3-8B"
    assert raw["openai"][0]["model_name"] == "Qwen/Qwen3-8B"
    assert raw["env"]["batch_size"] < 128
    assert raw["env"]["group_size"] < 16
    assert raw["env"]["total_steps"] < 50
    assert raw["env"]["use_wandb"] is False
