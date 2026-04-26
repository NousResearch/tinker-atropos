#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from tinker_atropos.environments.min_agentic_production_router_tinker import AGENTIC_PRODUCTION_ROUTER_ITEMS
ENV_ITEMS_BY_TASK_ID = {item["task_id"]: item for item in AGENTIC_PRODUCTION_ROUTER_ITEMS}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _join_terms(task: dict[str, Any], key: str) -> str:
    return ", ".join(task.get(key) or [])


def _enrich_task(task: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(task)
    env_item = ENV_ITEMS_BY_TASK_ID.get(task.get("task_id"), {})
    for key in (
        "must_include_terms",
        "routing_terms",
        "prerequisite_terms",
        "execution_terms",
        "artifact_terms",
        "verification_terms",
        "learning_terms",
    ):
        if not enriched.get(key) and env_item.get(key):
            enriched[key] = env_item[key]
    if not enriched.get("must_include") and enriched.get("must_include_terms"):
        enriched["must_include"] = enriched["must_include_terms"]
    return enriched


def build_task_instruction(task: dict[str, Any]) -> str:
    task = _enrich_task(task)
    must_terms = ", ".join(task.get("must_include") or task.get("must_include_terms") or [])
    section_guidance = (
        f"작업분류에 넣을 말: {_join_terms(task, 'routing_terms')}\n"
        f"선행경로에 넣을 말: {_join_terms(task, 'prerequisite_terms')}\n"
        f"실행표면에 넣을 말: {_join_terms(task, 'execution_terms')}\n"
        f"산출물에 넣을 말: {_join_terms(task, 'artifact_terms')}\n"
        f"검증에 넣을 말: {_join_terms(task, 'verification_terms')}\n"
        f"기록에 넣을 말: {_join_terms(task, 'learning_terms')}\n"
    )
    return (
        "너는 민의 헤르메스 제작 라우터다. 아래 요청에 대해 계획만 말하지 말고, "
        "선행 도구, 실행 표면, 산출물, 검증, 기록까지 닫는 답변을 작성하라.\n\n"
        f"과제: {task.get('title', task['task_id'])}\n"
        f"요청: {task.get('prompt', '')}\n"
        f"반드시 넣을 말: {must_terms}\n"
        f"{section_guidance}\n"
        "아래 형식을 정확히 지켜라.\n"
        "작업분류:\n"
        "선행경로:\n"
        "실행표면:\n"
        "산출물:\n"
        "검증:\n"
        "기록:\n"
    )


def run_hermes_chat(prompt: str, hermes_command: str = "hermes", timeout: int = 300) -> str:
    command = [*shlex.split(hermes_command), "chat", "-q", prompt]
    result = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    output = result.stdout.strip()
    if result.returncode != 0:
        error = result.stderr.strip()
        raise RuntimeError(f"hermes command failed with exit {result.returncode}: {error or output}")
    return output


def render_sample_file(task: dict[str, Any], answer: str, lane_name: str, instruction: str) -> str:
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        "---\n"
        f"task_id: {task['task_id']}\n"
        f"title: {task.get('title', '')}\n"
        f"lane: {lane_name}\n"
        f"created_at: {created_at}\n"
        "source: hermes chat -q\n"
        "---\n\n"
        f"# {task.get('title', task['task_id'])}\n\n"
        "## 요청\n\n"
        f"{task.get('prompt', '')}\n\n"
        "## 실행 지시\n\n"
        "```text\n"
        f"{instruction.strip()}\n"
        "```\n\n"
        "## 답변\n\n"
        f"{answer.strip()}\n"
    )


def collect_samples(
    benchmark_path: Path,
    answer_dir: Path,
    runner: Callable[[str], str],
    lane_name: str,
    skip_existing: bool = False,
    max_tasks: int | None = None,
    keep_going: bool = False,
) -> dict[str, Any]:
    benchmark = load_json(benchmark_path)
    answer_dir.mkdir(parents=True, exist_ok=True)
    written = []
    skipped = []
    failed = []
    tasks = benchmark.get("tasks", [])
    if max_tasks is not None:
        tasks = tasks[:max_tasks]
    for task in tasks:
        task_id = task["task_id"]
        out_path = answer_dir / f"{task_id}.md"
        if skip_existing and out_path.exists():
            skipped.append(task_id)
            continue
        instruction = build_task_instruction(task)
        try:
            answer = runner(instruction)
        except Exception as exc:
            if not keep_going:
                raise
            failed.append(task_id)
            answer = f"수집오류: {type(exc).__name__}: {exc}"
        out_path.write_text(render_sample_file(task, answer, lane_name, instruction), encoding="utf-8")
        written.append(str(out_path))
    manifest = {
        "version": benchmark.get("version", "unknown"),
        "lane": lane_name,
        "benchmark_path": str(benchmark_path),
        "answer_dir": str(answer_dir),
        "written_count": len(written),
        "written_paths": written,
        "skipped_task_ids": skipped,
        "failed_task_ids": failed,
        "task_count_requested": len(tasks),
    }
    (answer_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="헤르메스 chat 실행으로 제작 라우터 실제 답변 샘플을 수집한다.")
    parser.add_argument("--benchmark", required=True, help="평가 세트 제이슨 경로")
    parser.add_argument("--answer-dir", required=True, help="샘플 마크다운 저장 폴더")
    parser.add_argument("--lane-name", default="actual_hermes_sample", help="샘플 레인 이름")
    parser.add_argument("--hermes-command", default="hermes", help="헤르메스 실행 명령. 예: hermes 또는 /path/to/hermes")
    parser.add_argument("--timeout", type=int, default=300, help="과제별 제한 초")
    parser.add_argument("--skip-existing", action="store_true", help="이미 있는 task_id.md는 건너뛰기")
    parser.add_argument("--max-tasks", type=int, help="앞에서부터 지정 수만 수집")
    parser.add_argument("--keep-going", action="store_true", help="과제 실패나 제한 시간 초과가 있어도 오류 샘플을 쓰고 계속 진행")
    args = parser.parse_args()

    def runner(prompt: str) -> str:
        return run_hermes_chat(prompt, hermes_command=args.hermes_command, timeout=args.timeout)

    manifest = collect_samples(
        Path(args.benchmark),
        Path(args.answer_dir),
        runner,
        lane_name=args.lane_name,
        skip_existing=args.skip_existing,
        max_tasks=args.max_tasks,
        keep_going=args.keep_going,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
