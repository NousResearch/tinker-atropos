from pathlib import Path


def test_daily_wrapper_exists_and_mentions_full_funnel():
    text = Path("/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_daily.sh").read_text(encoding="utf-8")
    assert "run_research_to_full_funnel.py" in text
    assert "PROJECT_SLUG" in text
    assert "PRESET" in text


def test_operational_wrapper_mentions_export_and_sync():
    text = Path("/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh").read_text(encoding="utf-8")
    assert "publish_ready_exporter.py" in text
    assert "paperclip_tinker_atropos_sync.py" in text
    assert "PIPELINE_JSON" in text
    assert "set +u" in text



def test_operational_wrapper_allows_local_trusted_sync_without_api_key():
    text = Path("/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh").read_text(encoding="utf-8")
    assert "/api/health" in text
    assert "deploymentMode" in text
    assert "paperclip_sync=skipped_missing_api_key" not in text



def test_automation_examples_mentions_cron_and_launchd():
    text = Path("/Users/heomin/.hermes/hermes-agent/tinker-atropos/automation_examples.md").read_text(encoding="utf-8")
    assert "Cron example" in text
    assert "launchd" in text
    assert "ordinarybiz" in text
    assert "run_full_funnel_operational.sh" in text
