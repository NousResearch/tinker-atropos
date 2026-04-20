import pytest

from tinker_atropos.environments.min_landing_cro_tinker import (
    LANDING_CRO_ITEMS,
    format_landing_prompt,
    is_ultra_smoke_mode,
    score_landing_answer,
)


def test_prompt_includes_required_cro_sections():
    item = LANDING_CRO_ITEMS[0]

    prompt = format_landing_prompt(item)

    assert item["page_type"] in prompt
    assert "병목:" in prompt
    assert "개선안:" in prompt
    assert "카피수정:" in prompt
    assert "실험:" in prompt
    assert "지표:" in prompt


def test_ultra_smoke_cro_prompt_is_shorter_but_keeps_required_sections(monkeypatch):
    item = LANDING_CRO_ITEMS[0]
    monkeypatch.setenv("MIN_LANDING_CRO_ULTRA_SMOKE", "1")

    prompt = format_landing_prompt(item)

    assert is_ultra_smoke_mode() is True
    assert len(prompt) < 180
    assert "병목:" in prompt
    assert "개선안:" in prompt
    assert "카피수정:" in prompt
    assert "실험:" in prompt
    assert "지표:" in prompt


def test_score_landing_answer_rewards_specific_copy_and_experiment_design():
    item = LANDING_CRO_ITEMS[0]
    answer = """
병목: 첫 화면에서 누구를 위한 페이지인지 바로 안 보여서 상담 신청 이유가 약하다.
개선안: 첫 화면에 AI 도구 세팅이 막힌 일인 사업가를 위한 진단 제안이라는 문장을 먼저 보여준다.
카피수정: 헤드라인을 'AI 도구는 많은데 매출 흐름이 없는 일인 사업가를 위한 Ailit 진단'으로 바꾼다.
실험: 이번 주 안에 기존 헤드라인과 새 헤드라인을 반반 노출해 일주일 동안 비교한다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 신청 전환율 5퍼센트를 본다.
""".strip()

    result = score_landing_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["specificity"] > 0.5
    assert result["copy_quality"] > 0.5
    assert result["experiment_quality"] > 0.5
    assert result["total"] >= 0.85


def test_score_landing_answer_penalizes_generic_copy_and_missing_metrics():
    item = LANDING_CRO_ITEMS[0]
    answer = """
병목: 전환이 낮다.
개선안: 더 좋아지게 바꾼다.
카피수정: 최고의 페이지로 만든다.
실험: 나중에 테스트한다.
지표: 성과를 본다.
""".strip()

    result = score_landing_answer(answer, item)

    assert result["specificity"] < 0.5
    assert result["copy_quality"] < 0.5
    assert result["experiment_quality"] < 0.5
    assert result["metric_quality"] < 0.5
    assert result["hype_penalty"] < 0.0
    assert result["total"] < 0.55


def test_score_landing_answer_allows_perfect_metric_quality_and_total():
    item = LANDING_CRO_ITEMS[0]
    answer = """
병목: 첫 화면 헤드라인 설명란 문장과 버튼에서 상담 신청 이유가 약해 일주일 동안 전환이 새지 못한다.
개선안: 첫 화면 헤드라인과 버튼 문장에서 Ailit 진단이 왜 필요한지 일인 사업가에게 바로 보이게 만든다.
카피수정: 헤드라인을 'AI 도구는 쓰지만 매출 흐름이 막힌 일인 사업가를 위한 Ailit 상담 진단'으로 바꾸고 설명란과 같은 제안 문장으로 버튼까지 잇는다.
실험: 이번 주 기존 헤드라인과 새 헤드라인을 반반 비교하는 실험으로 버튼 문장까지 같이 바꾸고 일주일 동안 차이를 본다.
지표: 클릭률 3퍼센트(3%), 상담 신청 10건, 신청 전환율 5퍼센트(5%)를 본다.
""".strip()

    result = score_landing_answer(answer, item)

    assert result["metric_quality"] == pytest.approx(1.0)
    assert result["total"] == pytest.approx(1.0)
