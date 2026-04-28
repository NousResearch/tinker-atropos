from __future__ import annotations

from pathlib import Path

from scripts.evaluate_min_hermes_offline_set import evaluate_benchmark, load_json
from scripts.generate_min_hermes_policy_answers import evaluate_answers, generate_lane_answers

ROOT = Path(__file__).resolve().parent
BENCHMARK_V2_PATH = ROOT / "research" / "min_hermes_offline_eval_v2.json"


def test_v2_benchmark_records_current_hardening_recovery() -> None:
    benchmark = load_json(BENCHMARK_V2_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "current_policy": {
                "benchmark_version": benchmark["version"],
                "answers": generate_lane_answers(benchmark, strong=False),
            },
            "patched_policy": {
                "benchmark_version": benchmark["version"],
                "answers": generate_lane_answers(benchmark, strong=True),
            },
        },
    )

    current_lane = result["lanes"]["current_policy"]
    patched_lane = result["lanes"]["patched_policy"]

    assert benchmark["version"] == "v2"
    assert benchmark["comparison_lanes"] == ["current_policy", "patched_policy"]
    assert current_lane["task_count"] == 12
    assert patched_lane["task_count"] == 12
    assert current_lane["lane_passed"] is True
    assert patched_lane["lane_passed"] is True
    assert current_lane["task_pass_count"] == 12
    assert patched_lane["task_pass_count"] == 12
    assert current_lane["env_summary"]["min_business_strategy"]["mean_total"] >= 0.99
    assert current_lane["env_summary"]["min_landing_cro"]["mean_total"] >= 0.98 - 0.005
    assert current_lane["env_summary"]["min_x_strategy"]["mean_total"] >= 1.0


def test_current_policy_v2_recovers_tail_tasks_after_generator_upgrade() -> None:
    benchmark = load_json(BENCHMARK_V2_PATH)
    current_summary = evaluate_answers(benchmark, generate_lane_answers(benchmark, strong=False))

    assert current_summary["task_count"] == 12
    assert current_summary["task_pass_count"] == 12
    assert current_summary["mean_total"] >= 0.995
    assert current_summary["env_summary"]["min_business_strategy"] >= 0.99
    assert current_summary["env_summary"]["min_landing_cro"] >= 0.98
    assert current_summary["env_summary"]["min_x_strategy"] >= 1.0


def test_current_policy_v2_business_tail_tasks_gain_beginner_channel_and_proposal_strength() -> None:
    benchmark = load_json(BENCHMARK_V2_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "current_policy": {
                "benchmark_version": benchmark["version"],
                "answers": generate_lane_answers(benchmark, strong=False),
            }
        },
    )
    task_map = {task["task_id"]: task for task in benchmark["tasks"]}
    result_map = {task["task_id"]: task for task in result["lanes"]["current_policy"]["task_results"]}

    for task_id in [
        "biz-google-ads-low-risk",
        "biz-brand-collab-structure",
        "biz-sydney-action-note",
        "biz-gws-time-saving",
    ]:
        task = task_map[task_id]
        score = result_map[task_id]["score"]
        assert task["env"] == "min_business_strategy"
        assert score["beginner_friendliness"] >= 0.8
        assert score["channel_fit"] >= 1.0
        assert score["proposal_alignment"] >= 0.8


def test_current_policy_v2_landing_tail_tasks_gain_metric_quality() -> None:
    benchmark = load_json(BENCHMARK_V2_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "current_policy": {
                "benchmark_version": benchmark["version"],
                "answers": generate_lane_answers(benchmark, strong=False),
            }
        },
    )
    result_map = {task["task_id"]: task for task in result["lanes"]["current_policy"]["task_results"]}

    for task_id in ["landing-brand-collab-inquiry", "landing-live-session-signup"]:
        score = result_map[task_id]["score"]
        assert score["metric_quality"] >= 0.8
        assert score["total"] >= 0.975


def test_current_policy_v2_x_tail_tasks_gain_single_action_clarity() -> None:
    benchmark = load_json(BENCHMARK_V2_PATH)
    result = evaluate_benchmark(
        benchmark,
        {
            "current_policy": {
                "benchmark_version": benchmark["version"],
                "answers": generate_lane_answers(benchmark, strong=False),
            }
        },
    )
    result_map = {task["task_id"]: task for task in result["lanes"]["current_policy"]["task_results"]}

    for task_id in ["x-ailit-entry-link", "x-vip-reactivation-checkin", "x-landing-headline-conversion"]:
        score = result_map[task_id]["score"]
        assert score["single_action_clarity"] >= 1.0
        assert score["total"] >= 1.0
