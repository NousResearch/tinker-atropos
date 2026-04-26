from __future__ import annotations

import json
from pathlib import Path

from scripts.build_production_router_sample_bundle import build_bundle_from_answer_dir, extract_answer_text


def test_extract_answer_text_supports_frontmatter_and_heading() -> None:
    raw = """---
task_id: production-router-landing-build
---
# 웹사이트 제작 요청

작업분류: 웹사이트 제작이다.
선행경로: 알피 씨엘아이를 먼저 쓴다.
"""

    assert extract_answer_text(raw).startswith("작업분류: 웹사이트 제작이다.")
    assert "선행경로: 알피 씨엘아이" in extract_answer_text(raw)
def test_extract_answer_text_prefers_final_hermes_block_over_prompt_echo() -> None:
    raw = """
# 샘플

작업분류에 넣을 말: 웹사이트, 랜딩, 코드, 피그마
산출물에 넣을 말: 변경 파일, 이미지 파일, 프롬프트, 스크린샷, 드리프트
아래 형식을 정확히 지켜라.
작업분류:
선행경로:

╭─ ⚕ Hermes ─────────────────────╮
    작업분류: 웹사이트 제작이다.
    선행경로: 알피 씨엘아이를 먼저 쓴다.
    실행표면: 코덱스 씨엘아이로 구현한다.
    산출물: 변경 파일과 스크린샷을 남긴다.
    검증: 빌드를 돌린다.
    기록: 옵시디언에 남긴다.
╰────────────────────────────────╯
Resume this session with:
  hermes --resume abc
"""

    answer = extract_answer_text(raw)

    assert answer.startswith("작업분류: 웹사이트 제작이다.")
    assert "산출물에 넣을 말" not in answer
    assert "Resume this session" not in answer


def test_build_bundle_from_answer_dir_maps_task_files(tmp_path: Path) -> None:
    benchmark = {
        "version": "v4_production_workflow",
        "tasks": [
            {"task_id": "production-router-landing-build", "title": "웹사이트 제작 요청 라우팅"},
            {"task_id": "production-router-image-to-video", "title": "이미지 영상 요청 라우팅"},
        ],
    }
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False), encoding="utf-8")
    answer_dir = tmp_path / "answers"
    answer_dir.mkdir()
    (answer_dir / "production-router-landing-build.md").write_text(
        "# 웹사이트 제작 요청\n\n작업분류: 웹사이트 제작이다.\n선행경로: 알피 씨엘아이를 먼저 쓴다.\n",
        encoding="utf-8",
    )
    (answer_dir / "production-router-image-to-video.txt").write_text(
        "작업분류: 이미지와 영상 제작이다.\n선행경로: 지피티 이미지 투를 먼저 쓴다.\n",
        encoding="utf-8",
    )

    bundle = build_bundle_from_answer_dir(benchmark_path, answer_dir, lane_name="actual_hermes_sample")

    assert bundle["version"] == "v4_production_workflow"
    assert bundle["lane"] == "actual_hermes_sample"
    assert [entry["task_id"] for entry in bundle["answers"]] == [
        "production-router-landing-build",
        "production-router-image-to-video",
    ]
    assert bundle["answers"][0]["answer"].startswith("작업분류: 웹사이트 제작이다.")


def test_build_bundle_from_answer_dir_marks_missing_answers(tmp_path: Path) -> None:
    benchmark = {"version": "v4", "tasks": [{"task_id": "missing-task", "title": "없음"}]}
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False), encoding="utf-8")
    answer_dir = tmp_path / "answers"
    answer_dir.mkdir()

    bundle = build_bundle_from_answer_dir(benchmark_path, answer_dir, lane_name="empty")

    assert bundle["answers"] == [{"task_id": "missing-task", "answer": "", "source_path": None}]
    assert bundle["missing_task_ids"] == ["missing-task"]
