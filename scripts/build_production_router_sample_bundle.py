#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_frontmatter(text: str) -> str:
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return text
    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip()
    return text


def _extract_hermes_box(text: str) -> str | None:
    marker = "╭─ ⚕ Hermes"
    start = text.rfind(marker)
    if start < 0:
        return None
    after_marker = text[start:].splitlines()[1:]
    content_lines: list[str] = []
    for line in after_marker:
        if line.lstrip().startswith("╰"):
            break
        content_lines.append(line.strip())
    content = "\n".join(line for line in content_lines if line).strip()
    return content or None


def extract_answer_text(raw: str) -> str:
    text = strip_frontmatter(raw).strip()
    hermes_box = _extract_hermes_box(text)
    if hermes_box:
        return hermes_box
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and lines[0].lstrip().startswith("#"):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines).strip()


def answer_path_for_task(answer_dir: Path, task_id: str) -> Path | None:
    for suffix in (".md", ".txt"):
        candidate = answer_dir / f"{task_id}{suffix}"
        if candidate.exists():
            return candidate
    return None


def build_bundle_from_answer_dir(benchmark_path: Path, answer_dir: Path, lane_name: str) -> dict[str, Any]:
    benchmark = load_json(benchmark_path)
    answers = []
    missing_task_ids = []
    for task in benchmark.get("tasks", []):
        task_id = task["task_id"]
        source_path = answer_path_for_task(answer_dir, task_id)
        if source_path is None:
            missing_task_ids.append(task_id)
            answers.append({"task_id": task_id, "answer": "", "source_path": None})
            continue
        answer = extract_answer_text(source_path.read_text(encoding="utf-8"))
        answers.append({"task_id": task_id, "answer": answer, "source_path": str(source_path)})
    return {
        "version": benchmark.get("version", "unknown"),
        "lane": lane_name,
        "benchmark_path": str(benchmark_path),
        "answer_dir": str(answer_dir),
        "answers": answers,
        "missing_task_ids": missing_task_ids,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="제작 라우터 답변 폴더를 오프라인 평가 번들로 변환한다.")
    parser.add_argument("--benchmark", required=True, help="평가 세트 제이슨 경로")
    parser.add_argument("--answer-dir", required=True, help="task_id.md 또는 task_id.txt 파일이 들어 있는 폴더")
    parser.add_argument("--lane-name", default="actual_hermes_sample", help="생성할 레인 이름")
    parser.add_argument("--out", required=True, help="저장할 번들 제이슨 경로")
    args = parser.parse_args()

    bundle = build_bundle_from_answer_dir(Path(args.benchmark), Path(args.answer_dir), args.lane_name)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(bundle, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
