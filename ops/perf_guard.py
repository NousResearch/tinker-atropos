from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any, Sequence


def run_perf_guard(
    command: Sequence[str],
    *,
    samples: int = 5,
    warmups: int = 1,
    baseline_seconds: float | None = None,
    cwd: str | None = None,
) -> dict[str, Any]:
    if samples < 1:
        raise ValueError("samples must be >= 1")
    if warmups < 0:
        raise ValueError("warmups must be >= 0")
    if not command:
        raise ValueError("command must not be empty")

    for _ in range(warmups):
        _run_once(command, cwd=cwd)

    sample_seconds: list[float] = []
    for _ in range(samples):
        sample_seconds.append(_run_once(command, cwd=cwd))

    median_seconds = statistics.median(sample_seconds)
    stdev_seconds = statistics.stdev(sample_seconds) if len(sample_seconds) > 1 else 0.0
    result: dict[str, Any] = {
        "command": list(command),
        "cwd": cwd,
        "sample_count": samples,
        "warmup_count": warmups,
        "samples_seconds": sample_seconds,
        "min_seconds": min(sample_seconds),
        "median_seconds": median_seconds,
        "max_seconds": max(sample_seconds),
        "stdev_seconds": stdev_seconds,
    }
    if baseline_seconds is not None:
        result["baseline_seconds"] = baseline_seconds
        result["delta_percent"] = ((median_seconds - baseline_seconds) / baseline_seconds) * 100
    return result


def summarize_result(result: dict[str, Any]) -> str:
    median = result["median_seconds"]
    baseline = result.get("baseline_seconds")
    if baseline is None:
        return f"median {median:.4f}s across {result['sample_count']} samples; no baseline supplied"

    delta = result["delta_percent"]
    if delta < 0:
        status = "improved"
    elif delta > 0:
        status = "regressed"
    else:
        status = "unchanged"
    return f"{status}: median {median:.4f}s vs baseline {baseline:.4f}s ({delta:+.2f}%)"


def _run_once(command: Sequence[str], *, cwd: str | None) -> float:
    started = time.perf_counter()
    subprocess.run(command, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small repeatable performance guard.")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--baseline-seconds", type=float)
    parser.add_argument("--cwd")
    parser.add_argument("--json-out")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to measure after --")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    result = run_perf_guard(
        command,
        samples=args.samples,
        warmups=args.warmups,
        baseline_seconds=args.baseline_seconds,
        cwd=args.cwd,
    )
    print(summarize_result(result))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
