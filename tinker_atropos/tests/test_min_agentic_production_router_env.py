import pytest

from tinker_atropos.environments.min_agentic_production_router_tinker import (
    AGENTIC_PRODUCTION_ROUTER_ITEMS,
    format_production_router_prompt,
    score_production_router_answer,
)


def test_prompt_includes_required_production_router_sections():
    item = AGENTIC_PRODUCTION_ROUTER_ITEMS[0]

    prompt = format_production_router_prompt(item)

    assert item["prompt"] in prompt
    assert "작업분류:" in prompt
    assert "선행경로:" in prompt
    assert "실행표면:" in prompt
    assert "산출물:" in prompt
    assert "검증:" in prompt
    assert "기록:" in prompt


def test_score_rewards_complete_hermes_production_routing_answer():
    item = AGENTIC_PRODUCTION_ROUTER_ITEMS[0]
    answer = """
작업분류: 웹사이트 랜딩페이지 제작과 코드 구현 작업이다.
선행경로: 먼저 알피 씨엘아이로 저장소 루트를 확인하고, DESIGN.md를 디자인 계약서로 읽은 뒤 figma-use로 피그마 디자인 문맥과 스크린샷을 확보한다.
실행표면: 헤르메스가 수락 기준을 만들고 코덱스 씨엘아이로 구현을 맡긴다. 지피티 이미지 투 이미지는 openai-codex-gpt-image-2-workflow로 생성한다.
산출물: 변경 파일, DESIGN.md 드리프트 메모, 이미지 파일 경로, 프롬프트 로그, 브라우저 스크린샷을 남긴다.
검증: 빌드, 테스트, 브라우저 검증, 이미지 파일 존재 확인을 실행하고 결과를 완료 보고에 적는다.
기록: 성공 규칙과 실패 패턴을 옵시디언 노트와 티커 아트로포스 평가 세트에 기록한다.
""".strip()

    result = score_production_router_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["routing_accuracy"] >= 0.9
    assert result["prerequisite_gate_compliance"] >= 0.9
    assert result["execution_surface_choice"] >= 0.8
    assert result["artifact_contract"] >= 0.8
    assert result["verification_strength"] >= 0.8
    assert result["learning_loop_capture"] >= 0.8
    assert result["total"] >= 0.9


def test_score_accepts_indented_sections_from_hermes_cli_output():
    item = AGENTIC_PRODUCTION_ROUTER_ITEMS[3]
    answer = """
╭─ ⚕ Hermes ─╮
    작업분류:
    저장소 버그 수정과 코드 검증 작업이다.
    선행경로:
    알피 씨엘아이로 저장소 문맥을 확인하고 수락 기준을 먼저 작성한다.
    실행표면:
    코덱스 씨엘아이로 패치 구현을 맡기고 헤르메스가 결과를 검토한다.
    산출물:
    변경 파일, 로그, diff, 테스트 결과를 남긴다.
    검증:
    테스트, 빌드, 변경 파일 확인, 헤르메스 최종 검토를 완료한다.
    기록:
    회귀 방지 테스트와 실패 패턴을 스킬과 옵시디언에 기록한다.
╰───────────╯
""".strip()

    result = score_production_router_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["total"] >= 0.9


def test_score_penalizes_plan_only_answer_without_verification_or_artifacts():
    item = AGENTIC_PRODUCTION_ROUTER_ITEMS[0]
    answer = """
작업분류: 웹사이트를 좋게 만든다.
선행경로: 필요한 것을 본다.
실행표면: 알아서 한다.
산출물: 결과를 만든다.
검증: 확인한다.
기록: 나중에 정리한다.
""".strip()

    result = score_production_router_answer(answer, item)

    assert result["prerequisite_gate_compliance"] < 0.5
    assert result["artifact_contract"] < 0.5
    assert result["verification_strength"] < 0.5
    assert result["learning_loop_capture"] < 0.5
    assert result["total"] < 0.55
