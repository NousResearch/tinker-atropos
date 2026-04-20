from __future__ import annotations

from pathlib import Path

from scripts.evaluate_min_hermes_offline_set import evaluate_benchmark, load_json
from scripts.generate_min_hermes_policy_answers import generate_lane_answers

ROOT = Path(__file__).resolve().parent
BENCHMARK_V3_PATH = ROOT / "research" / "min_hermes_offline_eval_v3.json"


def test_v3_benchmark_restores_promotion_discrimination() -> None:
    benchmark = load_json(BENCHMARK_V3_PATH)
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

    assert benchmark["version"] == "v3"
    assert current_lane["task_count"] == 1
    assert patched_lane["task_count"] == 1
    assert current_lane["lane_passed"] is False
    assert patched_lane["lane_passed"] is True
    assert current_lane["mean_total"] < patched_lane["mean_total"]
    assert current_lane["task_pass_count"] == 0
    assert patched_lane["task_pass_count"] == 1
