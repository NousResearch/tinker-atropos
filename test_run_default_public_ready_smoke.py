from run_default_public_ready_smoke import (
    assess_run,
    build_report_markdown,
    has_useful_progress,
    load_run_settings,
    summarize_env_text,
    summarize_trainer_text,
)


def test_summarize_trainer_text_extracts_progress_markers():
    text = """
Registered as trainer: 123
Step 8/50
Got 96 Datum objects
Loss: 303.06928539276123
Reward/mean: 0.3438
"""
    summary = summarize_trainer_text(text)

    assert summary["registered"] is True
    assert summary["last_step"] == "8/50"
    assert summary["got_datum_objects"] == 96
    assert summary["reward_mean"] == 0.3438
    assert summary["completed"] is False


def test_summarize_trainer_text_detects_completion_and_weights():
    text = """
Registered as trainer: 999
Training completed successfully!
Final weights are available here: tinker://abc/final
"""
    summary = summarize_trainer_text(text)

    assert summary["registered"] is True
    assert summary["completed"] is True
    assert summary["final_weights"] == "tinker://abc/final"


def test_summarize_trainer_text_uses_latest_progress_values_when_multiple_steps_exist():
    text = """
Step 0/12
Got 0 Datum objects
Loss: 0.0
Reward/mean: 0.0000
Step 2/12
Got 8 Datum objects
Loss: 11.713069915771484
Reward/mean: 0.0625
"""
    summary = summarize_trainer_text(text)

    assert summary["last_step"] == "2/12"
    assert summary["got_datum_objects"] == 8
    assert summary["loss"] == 11.713069915771484
    assert summary["reward_mean"] == 0.0625


def test_has_useful_progress_waits_past_zero_datum_first_step():
    early_text = """
Step 0/12
Got 0 Datum objects
Loss: 0.0
Reward/mean: 0.0000
"""
    later_text = """
Step 1/12
Got 4 Datum objects
Loss: 11.713069915771484
Reward/mean: 0.0625
"""

    assert has_useful_progress(early_text) is False
    assert has_useful_progress(later_text) is True


def test_load_run_settings_accepts_env_overrides(monkeypatch):
    monkeypatch.setenv("DEFAULT_PUBLIC_READY_CONFIG", "configs/default_public_normal_lite.yaml")
    monkeypatch.setenv("DEFAULT_PUBLIC_READY_ENV_PY", "tinker_atropos/environments/gsm8k_tinker.py")
    monkeypatch.setenv("DEFAULT_PUBLIC_READY_TIMEOUT", "75")

    settings = load_run_settings()

    assert settings["config"] == "configs/default_public_normal_lite.yaml"
    assert settings["timeout_seconds"] == 75
    assert settings["config_stem"] == "default_public_normal_lite"


def test_build_report_markdown_includes_assessment_and_cleanup():
    summary = {
        "config": "configs/default_public_normal_lite.yaml",
        "environment": "tinker_atropos/environments/gsm8k_tinker.py",
        "assessment": {"status": "working", "working": True, "reason": "ok"},
        "health_ready": True,
        "trainer_progress_seen": True,
        "trainer": {"registered": True, "last_step": "1/12", "got_datum_objects": 64, "reward_mean": 0.125},
        "environment_summary": {"started": True, "connect_8000_failed": False, "traceback": False},
        "trainer_active_before_cleanup": True,
        "env_active_before_cleanup": True,
        "run_api_active_before_cleanup": True,
        "cleanup_applied": {"trainer": True, "environment": True, "run_api": True},
        "trainer_log_path": "/tmp/trainer.log",
        "env_log_path": "/tmp/env.log",
    }

    text = build_report_markdown(summary)

    assert "status: working" in text
    assert "config: configs/default_public_normal_lite.yaml" in text
    assert "trainer_active_before_cleanup: True" in text
    assert "cleanup_applied" in text


def test_assess_run_marks_working_when_progress_and_env_are_healthy():
    verdict = assess_run(
        health_ready=True,
        trainer_progress_seen=True,
        trainer_summary={"registered": True, "completed": False},
        env_summary={"started": True, "connect_8000_failed": False, "traceback": False},
    )

    assert verdict["working"] is True
    assert verdict["status"] == "working"


def test_assess_run_marks_run_api_disconnect_when_env_loses_8000():
    verdict = assess_run(
        health_ready=True,
        trainer_progress_seen=True,
        trainer_summary={"registered": True, "completed": False},
        env_summary={"started": True, "connect_8000_failed": True, "traceback": True},
    )

    assert verdict["working"] is False
    assert verdict["status"] == "run_api_disconnect"


def test_summarize_env_text_detects_rollout_disconnect_root_cause():
    text = """
BaseEnvConfig(
ERROR:root:Error in collect_trajectories: RetryError[<Future at 0x1 state=finished raised ClientConnectorError>]
aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host localhost:8000 ssl:default [Errno 61]
INFO:atroposlib.envs.base:worker_done: item_uuid=abc cancelled=False done=True
"""
    summary = summarize_env_text(text)

    assert summary["started"] is True
    assert summary["connect_8000_failed"] is True
    assert summary["worker_done_count"] == 1
