#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from tinker_atropos.environments.min_agentic_research_tinker import (  # noqa: E402
    AGENTIC_RESEARCH_ITEMS,
    score_research_answer,
)
from tinker_atropos.environments.min_business_strategy_tinker import (  # noqa: E402
    BUSINESS_STRATEGY_ITEMS,
    score_business_answer,
)
from tinker_atropos.environments.min_landing_cro_tinker import (  # noqa: E402
    LANDING_CRO_ITEMS,
    score_landing_answer,
)
from tinker_atropos.environments.min_membership_retention_tinker import (  # noqa: E402
    MEMBERSHIP_RETENTION_ITEMS,
    score_retention_answer,
)
from tinker_atropos.environments.min_x_strategy_tinker import (  # noqa: E402
    X_STRATEGY_ITEMS,
    score_x_answer,
)

ENV_REGISTRY = {
    "min_business_strategy": {
        "items": BUSINESS_STRATEGY_ITEMS,
        "score_fn": score_business_answer,
    },
    "min_x_strategy": {
        "items": X_STRATEGY_ITEMS,
        "score_fn": score_x_answer,
    },
    "min_landing_cro": {
        "items": LANDING_CRO_ITEMS,
        "score_fn": score_landing_answer,
    },
    "min_membership_retention": {
        "items": MEMBERSHIP_RETENTION_ITEMS,
        "score_fn": score_retention_answer,
    },
    "min_agentic_research": {
        "items": AGENTIC_RESEARCH_ITEMS,
        "score_fn": score_research_answer,
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_answer_map(bundle: dict[str, Any]) -> dict[str, str]:
    answers = bundle.get("answers", [])
    answer_map: dict[str, str] = {}
    for entry in answers:
        if not isinstance(entry, dict):
            continue
        task_id = entry.get("task_id")
        answer = entry.get("answer", "")
        if isinstance(task_id, str):
            answer_map[task_id] = answer if isinstance(answer, str) else ""
    return answer_map


def evaluate_task(task: dict[str, Any], answer: str, task_pass_threshold: float) -> dict[str, Any]:
    env_name = task["env"]
    registry = ENV_REGISTRY[env_name]
    item = registry["items"][task["item_index"]]
    metrics = registry["score_fn"](answer, item)
    must_pass_metrics = task.get("must_pass_metrics", [])
    gate_results = []
    for gate in must_pass_metrics:
        metric_name = gate["metric"]
        minimum = float(gate["min"])
        actual = float(metrics.get(metric_name, 0.0))
        gate_results.append(
            {
                "metric": metric_name,
                "min": minimum,
                "actual": actual,
                "passed": actual >= minimum,
            }
        )
    passed = float(metrics.get("total", 0.0)) >= task_pass_threshold and all(g["passed"] for g in gate_results)
    return {
        "task_id": task["task_id"],
        "title": task["title"],
        "env": env_name,
        "answer_present": bool(answer.strip()),
        "score": metrics,
        "task_passed": passed,
        "gate_results": gate_results,
    }


def summarize_envs(task_results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task_result in task_results:
        grouped[task_result["env"]].append(task_result)

    summary: dict[str, dict[str, Any]] = {}
    for env_name, env_results in grouped.items():
        scores = [float(result["score"]["total"]) for result in env_results]
        passes = [result["task_passed"] for result in env_results]
        summary[env_name] = {
            "task_count": len(env_results),
            "mean_total": round(sum(scores) / len(scores), 4) if scores else 0.0,
            "pass_rate": round(sum(1 for passed in passes if passed) / len(passes), 4) if passes else 0.0,
        }
    return dict(sorted(summary.items()))


def evaluate_lane(
    benchmark: dict[str, Any],
    lane_name: str,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    task_pass_threshold = float(benchmark.get("task_pass_threshold", 0.8))
    answer_map = load_answer_map(bundle)
    task_results = [evaluate_task(task, answer_map.get(task["task_id"], ""), task_pass_threshold) for task in benchmark["tasks"]]
    mean_total = sum(float(result["score"]["total"]) for result in task_results) / len(task_results)
    pass_count = sum(1 for result in task_results if result["task_passed"])
    env_summary = summarize_envs(task_results)
    lane_thresholds = benchmark.get("lane_pass_thresholds", {})
    lane_passed = (
        mean_total >= float(lane_thresholds.get("mean_total", 0.0))
        and (pass_count / len(task_results)) >= float(lane_thresholds.get("pass_rate", 0.0))
        and min((env["mean_total"] for env in env_summary.values()), default=0.0) >= float(lane_thresholds.get("min_env_mean", 0.0))
    )
    weakest = sorted(task_results, key=lambda result: float(result["score"]["total"]))[:3]
    return {
        "lane": lane_name,
        "bundle_path": bundle.get("_path"),
        "mean_total": round(mean_total, 4),
        "pass_rate": round(pass_count / len(task_results), 4),
        "task_pass_count": pass_count,
        "task_count": len(task_results),
        "lane_passed": lane_passed,
        "env_summary": env_summary,
        "weakest_tasks": [
            {
                "task_id": result["task_id"],
                "title": result["title"],
                "total": round(float(result["score"]["total"]), 4),
            }
            for result in weakest
        ],
        "task_results": task_results,
    }


def evaluate_benchmark(benchmark: dict[str, Any], lane_bundles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    lanes = {lane_name: evaluate_lane(benchmark, lane_name, bundle) for lane_name, bundle in lane_bundles.items()}
    return {
        "benchmark_version": benchmark.get("version", "unknown"),
        "primary_bottleneck": benchmark.get("primary_bottleneck"),
        "task_count": len(benchmark.get("tasks", [])),
        "lanes": lanes,
    }


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# 민 전용 Hermes 오프라인 평가 결과",
        "",
        f"- benchmark_version: {result['benchmark_version']}",
        f"- primary_bottleneck: {result['primary_bottleneck']}",
        f"- task_count: {result['task_count']}",
        "",
        "## Lane summary",
        "",
        "| lane | mean_total | pass_rate | task_pass_count | lane_passed |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for lane_name, lane in result["lanes"].items():
        lines.append(
            f"| {lane_name} | {lane['mean_total']:.4f} | {lane['pass_rate']:.4f} | {lane['task_pass_count']}/{lane['task_count']} | {'yes' if lane['lane_passed'] else 'no'} |"
        )

    for lane_name, lane in result["lanes"].items():
        lines.extend(
            [
                "",
                f"## {lane_name}",
                "",
                "### Env summary",
                "",
                "| env | mean_total | pass_rate |",
                "| --- | ---: | ---: |",
            ]
        )
        for env_name, env_summary in lane["env_summary"].items():
            lines.append(
                f"| {env_name} | {env_summary['mean_total']:.4f} | {env_summary['pass_rate']:.4f} |"
            )
        lines.extend([
            "",
            "### Weakest tasks",
            "",
            "| task_id | title | total |",
            "| --- | --- | ---: |",
        ])
        for task in lane["weakest_tasks"]:
            lines.append(f"| {task['task_id']} | {task['title']} | {task['total']:.4f} |")

    return "\n".join(lines) + "\n"


def parse_lane_argument(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise ValueError(f"lane argument must look like name=path, got: {raw}")
    lane_name, path_text = raw.split("=", 1)
    lane_name = lane_name.strip()
    path = Path(path_text.strip())
    if not lane_name:
        raise ValueError(f"lane name is empty: {raw}")
    return lane_name, path


def main() -> None:
    parser = argparse.ArgumentParser(description="민 전용 Hermes 오프라인 평가 세트를 채점한다.")
    parser.add_argument(
        "--benchmark",
        default=str(REPO_ROOT / "research" / "min_hermes_offline_eval_v1.json"),
        help="평가 세트 JSON 경로",
    )
    parser.add_argument(
        "--lane",
        action="append",
        default=[],
        help="lane_name=path 형식의 답안 번들. 예: human_baseline=research/min_hermes_offline_eval_v1_human_baseline.json",
    )
    parser.add_argument("--json-out", help="JSON 결과 저장 경로")
    parser.add_argument("--markdown-out", help="Markdown 결과 저장 경로")
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark)
    benchmark = load_json(benchmark_path)

    lane_bundles: dict[str, dict[str, Any]] = {}
    for raw_lane in args.lane:
        lane_name, lane_path = parse_lane_argument(raw_lane)
        bundle = load_json(lane_path)
        bundle["_path"] = str(lane_path)
        lane_bundles[lane_name] = bundle

    if not lane_bundles:
        raise SystemExit("at least one --lane name=path argument is required")

    result = evaluate_benchmark(benchmark, lane_bundles)
    markdown = build_markdown_report(result)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        Path(args.markdown_out).write_text(markdown, encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
