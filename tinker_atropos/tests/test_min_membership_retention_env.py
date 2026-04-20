import pytest

from tinker_atropos.environments.min_membership_retention_tinker import (
    MEMBERSHIP_RETENTION_ITEMS,
    format_retention_prompt,
    is_ultra_smoke_mode,
    score_retention_answer,
)


def test_prompt_includes_required_retention_sections():
    item = MEMBERSHIP_RETENTION_ITEMS[0]

    prompt = format_retention_prompt(item)

    assert item["membership"] in prompt
    assert "이탈원인:" in prompt
    assert "온보딩수정:" in prompt
    assert "리텐션장치:" in prompt
    assert "운영메시지:" in prompt
    assert "지표:" in prompt


def test_ultra_smoke_retention_prompt_is_shorter_but_keeps_required_sections(monkeypatch):
    item = MEMBERSHIP_RETENTION_ITEMS[0]
    monkeypatch.setenv("MIN_RETENTION_ULTRA_SMOKE", "1")

    prompt = format_retention_prompt(item)

    assert is_ultra_smoke_mode() is True
    assert len(prompt) < 190
    assert "이탈원인:" in prompt
    assert "온보딩수정:" in prompt
    assert "리텐션장치:" in prompt
    assert "운영메시지:" in prompt
    assert "지표:" in prompt


def test_score_retention_answer_rewards_specific_onboarding_and_checkin_loop():
    item = MEMBERSHIP_RETENTION_ITEMS[0]
    answer = """
이탈원인: 결제 직후 무엇부터 해야 하는지 몰라 첫 이틀 안에 조용히 이탈한다.
온보딩수정: 첫날 해야 할 한 가지 미션과 둘째 날 체크인 메시지를 고정 공지로 바로 보여준다.
리텐션장치: 텔레그램 체크인 스레드에서 매일 짧게 진행 상황을 남기게 하고 운영자가 이틀 안에 반응한다.
운영메시지: '오늘은 이 한 가지만 끝내면 됩니다' 같은 쉬운 말로 부담을 낮춘다.
지표: 첫 칠 일 참여율 70퍼센트, 재방문율 50퍼센트, 이탈률 20퍼센트를 본다.
""".strip()

    result = score_retention_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["specificity"] > 0.5
    assert result["retention_mechanism"] > 0.5
    assert result["metric_quality"] > 0.5
    assert result["total"] >= 0.85


def test_score_retention_answer_penalizes_generic_motivation_copy():
    item = MEMBERSHIP_RETENTION_ITEMS[0]
    answer = """
이탈원인: 동기부여가 약하다.
온보딩수정: 더 좋게 바꾼다.
리텐션장치: 자주 소통한다.
운영메시지: 최고가 될 수 있다고 격려한다.
지표: 성과를 본다.
""".strip()

    result = score_retention_answer(answer, item)

    assert result["specificity"] < 0.5
    assert result["retention_mechanism"] < 0.5
    assert result["metric_quality"] < 0.5
    assert result["hype_penalty"] < 0.0
    assert result["total"] < 0.55
