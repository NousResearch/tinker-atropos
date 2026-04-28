from __future__ import annotations

import json
from pathlib import Path

from scripts.collect_production_router_hermes_samples import build_task_instruction, collect_samples


def test_build_task_instruction_requires_production_router_sections() -> None:
    task = {
        "task_id": "production-router-landing-build",
        "title": "웹사이트 제작 요청 라우팅",
        "prompt": "새 랜딩페이지를 만들어줘.",
        "must_include": ["알피 씨엘아이", "브라우저 검증"],
    }

    instruction = build_task_instruction(task)

    assert "새 랜딩페이지를 만들어줘." in instruction
    assert "알피 씨엘아이" in instruction
    assert "브라우저 검증" in instruction
    assert "작업분류:" in instruction
    assert "선행경로:" in instruction
    assert "실행표면:" in instruction
    assert "산출물:" in instruction
    assert "검증:" in instruction
    assert "기록:" in instruction
    assert "산출물에 넣을 말" in instruction
    assert "검증에 넣을 말" in instruction
    assert "변경 파일" in instruction
    assert "드리프트" in instruction
    assert "티커 아트로포스" in instruction


def test_collect_samples_writes_one_markdown_per_task_with_runner_output(tmp_path: Path) -> None:
    benchmark = {
        "version": "v4_production_workflow",
        "tasks": [
            {
                "task_id": "production-router-landing-build",
                "title": "웹사이트 제작 요청 라우팅",
                "prompt": "새 랜딩페이지를 만들어줘.",
                "must_include": ["알피 씨엘아이"],
            },
            {
                "task_id": "production-router-image-to-video",
                "title": "이미지 영상 요청 라우팅",
                "prompt": "이미지를 영상으로 만들어줘.",
                "must_include": ["시댄스"],
            },
        ],
    }
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False), encoding="utf-8")
    answer_dir = tmp_path / "answers"
    seen_prompts: list[str] = []

    def fake_runner(prompt: str) -> str:
        seen_prompts.append(prompt)
        return "작업분류: 테스트\n선행경로: 알피 씨엘아이\n실행표면: 헤르메스\n산출물: 파일\n검증: 테스트\n기록: 옵시디언"

    manifest = collect_samples(benchmark_path, answer_dir, fake_runner, lane_name="test_lane")

    assert len(seen_prompts) == 2
    assert manifest["lane"] == "test_lane"
    assert manifest["written_count"] == 2
    first = answer_dir / "production-router-landing-build.md"
    second = answer_dir / "production-router-image-to-video.md"
    assert first.exists()
    assert second.exists()
    assert "task_id: production-router-landing-build" in first.read_text(encoding="utf-8")
    assert "작업분류: 테스트" in first.read_text(encoding="utf-8")


def test_collect_samples_keep_going_writes_error_sample(tmp_path: Path) -> None:
    benchmark = {
        "version": "v4",
        "tasks": [
            {"task_id": "ok", "title": "성공", "prompt": "요청", "must_include": []},
            {"task_id": "bad", "title": "실패", "prompt": "요청", "must_include": []},
        ],
    }
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False), encoding="utf-8")
    answer_dir = tmp_path / "answers"

    def mixed_runner(prompt: str) -> str:
        if "실패" in prompt:
            raise TimeoutError("timeout")
        return "작업분류: 성공\n선행경로: 알피 씨엘아이\n실행표면: 헤르메스\n산출물: 파일\n검증: 테스트\n기록: 옵시디언"

    manifest = collect_samples(benchmark_path, answer_dir, mixed_runner, lane_name="keep", keep_going=True)

    assert manifest["written_count"] == 2
    assert manifest["failed_task_ids"] == ["bad"]
    failed_text = (answer_dir / "bad.md").read_text(encoding="utf-8")
    assert "수집오류: TimeoutError: timeout" in failed_text


def test_collect_samples_skip_existing_does_not_call_runner(tmp_path: Path) -> None:
    benchmark = {
        "version": "v4",
        "tasks": [{"task_id": "already", "title": "기존", "prompt": "요청", "must_include": []}],
    }
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False), encoding="utf-8")
    answer_dir = tmp_path / "answers"
    answer_dir.mkdir()
    existing = answer_dir / "already.md"
    existing.write_text("기존 답변", encoding="utf-8")

    def fail_runner(prompt: str) -> str:
        raise AssertionError("runner should not be called")

    manifest = collect_samples(benchmark_path, answer_dir, fail_runner, lane_name="skip", skip_existing=True)

    assert manifest["written_count"] == 0
    assert manifest["skipped_task_ids"] == ["already"]
    assert existing.read_text(encoding="utf-8") == "기존 답변"
