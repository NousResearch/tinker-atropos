import pytest

from tinker_atropos.environments.min_business_strategy_tinker import (
    BUSINESS_STRATEGY_ITEMS,
    format_business_prompt,
    is_ultra_smoke_mode,
    score_business_answer,
)


def test_prompt_includes_brand_context_and_required_sections():
    item = BUSINESS_STRATEGY_ITEMS[0]

    prompt = format_business_prompt(item)

    assert item["scenario"] in prompt
    assert "평범한사업가" in prompt
    assert "문제:" in prompt
    assert "고객:" in prompt
    assert "제안:" in prompt
    assert "채널:" in prompt
    assert "실험:" in prompt
    assert "지표:" in prompt
    assert "한줄결론:" in prompt


def test_ultra_smoke_prompt_is_shorter_but_keeps_required_sections(monkeypatch):
    item = BUSINESS_STRATEGY_ITEMS[0]
    monkeypatch.setenv("MIN_BUSINESS_ULTRA_SMOKE", "1")

    prompt = format_business_prompt(item)

    assert is_ultra_smoke_mode() is True
    assert len(prompt) < 220
    assert "문제:" in prompt
    assert "고객:" in prompt
    assert "제안:" in prompt
    assert "채널:" in prompt
    assert "실험:" in prompt
    assert "지표:" in prompt
    assert "한줄결론:" in prompt


def test_score_business_answer_rewards_complete_concrete_plan():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = """
문제: 유튜브 유입은 높은데 상담 전환 문구가 약하다.
고객: 이미 AI 도구에 관심이 있지만 세팅 시간이 부족한 일인 사업가.
제안: Ailit 진단 세션과 빠른 세팅 패키지를 묶어 첫 상담 장벽을 낮춘다.
채널: 유튜브 설명란, X 고정글, 텔레그램 공지에서 같은 제안을 반복 노출한다.
실험: 이번 주 안에 설명란 문구 둘을 바꿔 일주일 동안 클릭률을 비교한다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 본다.
한줄결론: 기존 트래픽을 새 상품 제안으로 바로 전환하는 실험이다.
""".strip()

    result = score_business_answer(answer, item)

    assert result["total"] >= 0.8
    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["keyword_coverage"] >= 0.6
    assert result["actionability"] == pytest.approx(1.0)
    assert result["buzzword_penalty"] == pytest.approx(0.0)


def test_score_business_answer_penalizes_missing_sections_and_buzzwords():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = "혁신적인 최고 솔루션으로 성장합니다. 곧 다양한 방법을 검토해보겠습니다."

    result = score_business_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(0.0)
    assert result["keyword_coverage"] < 0.3
    assert result["actionability"] == pytest.approx(0.0)
    assert result["buzzword_penalty"] < 0.0
    assert result["total"] < 0.25


def test_score_business_answer_rewards_beginner_friendly_language_and_channel_fit():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = """
문제: 유튜브 설명란을 본 사람이 바로 상담까지 가지 않는다.
고객: AI는 궁금하지만 아직 어렵게 느끼는 일인 사업가라서 쉬운 안내가 필요하다.
제안: Ailit 진단 세션을 먼저 제안하고 바로 적용할 한 가지 세팅 예시를 함께 보여준다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 제안을 반복해 바로 눌러볼 링크를 준다.
실험: 이번 주 안에 설명란 첫 문장을 바꾸고 일주일 동안 클릭률과 상담 신청 수를 비교한다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 어려운 말보다 쉬운 말과 바로 누를 링크로 전환 마찰을 줄인다.
""".strip()

    result = score_business_answer(answer, item)

    assert result["beginner_friendliness"] > 0.5
    assert result["channel_fit"] > 0.5
    assert result["total"] >= 0.9


def test_score_business_answer_penalizes_vague_channel_and_hard_jargon():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = """
문제: 전환 효율이 낮다.
고객: 퍼널 최적화 니즈가 있는 사용자다.
제안: Ailit 솔루션으로 레버리지를 만든다.
채널: 여러 채널에서 한다.
실험: 곧 테스트한다.
지표: 성과를 본다.
한줄결론: 파이프라인을 고도화한다.
""".strip()

    result = score_business_answer(answer, item)

    assert result["beginner_friendliness"] < 0.5
    assert result["channel_fit"] < 0.5
    assert result["priority_clarity"] < 0.5
    assert result["total"] < 0.75


def test_score_business_answer_rewards_single_priority_action():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = """
문제: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.
제안: Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청 수를 본다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.
""".strip()

    result = score_business_answer(answer, item)

    assert result["priority_clarity"] > 0.5
    assert result["actionability"] > 0.5
    assert result["total"] >= 0.95


def test_score_business_answer_rewards_section_aligned_offer_experiment_and_metrics():
    item = BUSINESS_STRATEGY_ITEMS[0]
    answer = """
문제: 유튜브 유입은 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: 세팅 시간이 부족해서 무엇부터 시작할지 모르는 일인 사업가다.
제안: Ailit 진단 세션 하나를 먼저 제안하고 상담 전환 이유를 짧게 붙인다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장을 반복한다.
실험: 이번 주 설명란 첫 문장 하나만 바꾸고 일주일 동안 상담 신청 전환율을 비교한다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 한 가지 제안과 한 가지 실험으로 전환 마찰을 줄인다.
""".strip()

    result = score_business_answer(answer, item)

    assert result["section_alignment"] > 0.8
    assert result["total"] >= 0.9
