from __future__ import annotations

import json
from pathlib import Path

from scripts.evaluate_min_hermes_offline_set import build_markdown_report, evaluate_benchmark, load_json

ROOT = Path(__file__).resolve().parent
BENCHMARK_PATH = ROOT / "research" / "min_hermes_offline_eval_v1.json"
HUMAN_PATH = ROOT / "research" / "min_hermes_offline_eval_v1_human_baseline.json"
CURRENT_TEMPLATE_PATH = ROOT / "research" / "min_hermes_offline_eval_v1_current_policy_template.json"
PATCHED_TEMPLATE_PATH = ROOT / "research" / "min_hermes_offline_eval_v1_patched_policy_template.json"


def test_human_baseline_passes_benchmark() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "human_baseline": {
                **load_json(HUMAN_PATH),
                "_path": str(HUMAN_PATH),
            }
        },
    )

    lane = result["lanes"]["human_baseline"]
    assert result["task_count"] == 15
    assert lane["lane_passed"] is True
    assert lane["mean_total"] >= 0.85
    assert lane["pass_rate"] >= 0.8
    assert len(lane["env_summary"]) == 5
    assert all(summary["mean_total"] >= 0.78 for summary in lane["env_summary"].values())


def test_policy_templates_capture_real_comparison() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "current_policy": {
                **load_json(CURRENT_TEMPLATE_PATH),
                "_path": str(CURRENT_TEMPLATE_PATH),
            },
            "patched_policy": {
                **load_json(PATCHED_TEMPLATE_PATH),
                "_path": str(PATCHED_TEMPLATE_PATH),
            },
        },
    )

    current_lane = result["lanes"]["current_policy"]
    patched_lane = result["lanes"]["patched_policy"]
    assert current_lane["lane_passed"] is True
    assert patched_lane["lane_passed"] is True
    assert current_lane["mean_total"] >= 0.91
    assert current_lane["task_pass_count"] == 15
    assert patched_lane["mean_total"] >= current_lane["mean_total"]
    assert patched_lane["task_pass_count"] == 15
    assert patched_lane["pass_rate"] >= current_lane["pass_rate"]
    assert patched_lane["env_summary"]["min_landing_cro"]["mean_total"] >= current_lane["env_summary"]["min_landing_cro"]["mean_total"]
    assert patched_lane["env_summary"]["min_x_strategy"]["mean_total"] >= current_lane["env_summary"]["min_x_strategy"]["mean_total"]


def test_markdown_report_contains_lane_summary() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "human_baseline": {
                **load_json(HUMAN_PATH),
                "_path": str(HUMAN_PATH),
            }
        },
    )

    markdown = build_markdown_report(result)
    assert "# 민 전용 Hermes 오프라인 평가 결과" in markdown
    assert "| lane | mean_total | pass_rate | task_pass_count | lane_passed |" in markdown
    assert "## human_baseline" in markdown
    assert "min_business_strategy" in markdown
    assert "Weakest tasks" in markdown

    parsed = json.loads(json.dumps(result, ensure_ascii=False))
    assert parsed["benchmark_version"] == "v1"
