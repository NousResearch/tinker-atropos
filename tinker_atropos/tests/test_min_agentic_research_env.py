import pytest

from tinker_atropos.environments.min_agentic_research_tinker import (
    AGENTIC_RESEARCH_ITEMS,
    format_research_prompt,
    is_ultra_smoke_mode,
    score_research_answer,
)


def test_prompt_includes_required_research_sections():
    item = AGENTIC_RESEARCH_ITEMS[0]

    prompt = format_research_prompt(item)

    assert item["question"] in prompt
    assert "가설:" in prompt
    assert "찾을정보:" in prompt
    assert "비교기준:" in prompt
    assert "결론:" in prompt
    assert "다음행동:" in prompt


def test_ultra_smoke_research_prompt_is_shorter_but_keeps_required_sections(monkeypatch):
    item = AGENTIC_RESEARCH_ITEMS[0]
    monkeypatch.setenv("MIN_RESEARCH_ULTRA_SMOKE", "1")

    prompt = format_research_prompt(item)

    assert is_ultra_smoke_mode() is True
    assert len(prompt) < 180
    assert "가설:" in prompt
    assert "찾을정보:" in prompt
    assert "비교기준:" in prompt
    assert "결론:" in prompt
    assert "다음행동:" in prompt


def test_score_research_answer_rewards_clear_comparison_and_next_step():
    item = AGENTIC_RESEARCH_ITEMS[0]
    answer = """
가설: 경쟁사보다 우리 상품은 도입 장벽이 낮지만 신뢰 근거가 약할 가능성이 크다.
찾을정보: 가격, 핵심 제안, 후기, 무료 체험 여부를 먼저 비교해 본다.
비교기준: 가격 차이, 시작 장벽, 누구에게 맞는지, 바로 써볼 수 있는지 네 가지로 본다.
결론: 입문 장벽은 우리 쪽이 낮을 수 있지만 후기와 사례 노출은 경쟁사가 더 강할 수 있다.
다음행동: 오늘 경쟁사 셋의 랜딩 첫 화면과 가격 구간을 표로 정리한 뒤 우리 첫 화면 문구 하나를 바로 바꾼다.
""".strip()

    result = score_research_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["comparison_quality"] > 0.5
    assert result["actionability"] > 0.5
    assert result["specificity"] > 0.5
    assert result["total"] >= 0.85


def test_score_research_answer_penalizes_vague_summary_only():
    item = AGENTIC_RESEARCH_ITEMS[0]
    answer = """
가설: 여러 차이가 있을 수 있다.
찾을정보: 필요한 정보를 본다.
비교기준: 여러 요소를 본다.
결론: 추후 정리 가능하다.
다음행동: 나중에 확인한다.
""".strip()

    result = score_research_answer(answer, item)

    assert result["comparison_quality"] < 0.5
    assert result["actionability"] < 0.5
    assert result["specificity"] < 0.5
    assert result["total"] < 0.55
