from __future__ import annotations

import json
import sys

from ops.perf_guard import run_perf_guard, summarize_result


def test_run_perf_guard_returns_median_and_delta_against_baseline() -> None:
    command = [sys.executable, "-c", "print('ok')"]

    result = run_perf_guard(command, samples=3, baseline_seconds=1.0)

    assert result["command"] == command
    assert result["sample_count"] == 3
    assert len(result["samples_seconds"]) == 3
    assert result["median_seconds"] > 0
    assert result["min_seconds"] <= result["median_seconds"] <= result["max_seconds"]
    assert result["stdev_seconds"] >= 0
    assert result["baseline_seconds"] == 1.0
    assert result["delta_percent"] < 0


def test_summarize_result_is_json_serializable_and_mentions_regression_status() -> None:
    summary = summarize_result(
        {
            "command": ["python", "-c", "print('ok')"],
            "samples_seconds": [0.1, 0.2, 0.3],
            "sample_count": 3,
            "median_seconds": 0.2,
            "baseline_seconds": 0.25,
            "delta_percent": -20.0,
        }
    )

    assert "improved" in summary
    assert "-20.00%" in summary
    json.dumps(summary)
