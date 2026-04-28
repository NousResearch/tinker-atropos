import pytest

from tinker_atropos.environments.min_x_strategy_tinker import (
    X_STRATEGY_ITEMS,
    format_x_prompt,
    is_ultra_smoke_mode,
    score_x_answer,
)


def test_prompt_includes_required_x_sections():
    item = X_STRATEGY_ITEMS[0]

    prompt = format_x_prompt(item)

    assert item["topic"] in prompt
    assert "후크:" in prompt
    assert "본문:" in prompt
    assert "댓글유도:" in prompt
    assert "행동유도:" in prompt
    assert "금지:" in prompt


def test_ultra_smoke_x_prompt_is_shorter_but_keeps_required_sections(monkeypatch):
    item = X_STRATEGY_ITEMS[0]
    monkeypatch.setenv("MIN_X_ULTRA_SMOKE", "1")

    prompt = format_x_prompt(item)

    assert is_ultra_smoke_mode() is True
    assert len(prompt) < 180
    assert "후크:" in prompt
    assert "본문:" in prompt
    assert "댓글유도:" in prompt
    assert "행동유도:" in prompt
    assert "금지:" in prompt


def test_score_x_answer_rewards_clear_hook_and_engagement():
    item = X_STRATEGY_ITEMS[0]
    answer = """
후크: AI 도구 많이 써도 매출이 안 오르는 이유는 기능이 아니라 흐름이 없기 때문이다.
본문: 대부분은 도구를 모으지만 고객이 들어와서 상담, 결제, 재구매로 이어지는 구조를 안 만든다. 그래서 먼저 유튜브 설명란, 상담 제안, 후속 메시지 세 가지만 연결해야 한다.
댓글유도: 지금 당신 비즈니스에서 가장 막히는 한 지점은 어디인지 댓글로 남겨달라.
행동유도: 오늘 유튜브 설명란 첫 문장 하나만 바꾸고 클릭률을 확인해보자.
금지: 과장 없이 실제로 해본 것만 말한다.
""".strip()

    result = score_x_answer(answer, item)

    assert result["section_coverage"] == pytest.approx(1.0)
    assert result["hook_strength"] > 0.5
    assert result["engagement"] > 0.5
    assert result["actionability"] > 0.5
    assert result["total"] >= 0.85


def test_score_x_answer_penalizes_boring_and_hype_copy():
    item = X_STRATEGY_ITEMS[0]
    answer = """
후크: 혁신적인 시대입니다.
본문: 여러분 모두 최고가 될 수 있습니다.
댓글유도: 의견 부탁드립니다.
행동유도: 자세한 내용은 추후 공유합니다.
금지: 없음.
""".strip()

    result = score_x_answer(answer, item)

    assert result["hook_strength"] < 0.5
    assert result["engagement"] < 0.5
    assert result["single_action_clarity"] < 0.5
    assert result["hype_penalty"] < 0.0
    assert result["total"] < 0.55


def test_score_x_answer_rewards_one_clear_action():
    item = X_STRATEGY_ITEMS[0]
    answer = """
후크: AI 도구 많이 써도 매출이 안 오르는 이유는 기능이 아니라 흐름이 없기 때문이다.
본문: 대부분은 도구를 모으지만 유튜브 설명란, 상담 제안, 후속 메시지를 한 줄로 연결하지 못한다.
댓글유도: 지금 당신 비즈니스에서 가장 막힌 한 지점을 댓글로 남겨달라.
행동유도: 오늘 유튜브 설명란 첫 문장 하나만 바꾸고 클릭률을 확인해보자.
금지: 과장 없이 오늘 할 한 가지 행동만 말한다.
""".strip()

    result = score_x_answer(answer, item)

    assert result["single_action_clarity"] > 0.5
    assert result["actionability"] > 0.5
    assert result["total"] >= 0.84


def test_score_x_answer_rewards_section_aligned_body_comment_and_action():
    item = X_STRATEGY_ITEMS[0]
    answer = """
후크: AI 도구 많이 써도 매출이 안 오르는 이유는 기능이 아니라 흐름이 없기 때문이다.
본문: 유튜브에서 상담으로 이어지는 흐름이 없어서 매출이 막힌다. 그래서 AI 도구보다 유튜브 설명란과 상담 문장을 먼저 붙여야 한다.
댓글유도: 지금 당신 비즈니스에서 가장 막힌 한 지점을 댓글로 남겨달라.
행동유도: 오늘 유튜브 설명란 첫 문장 하나만 바꾸고 클릭률을 바로 확인해보자.
금지: 과장 없이 한 가지 행동만 말한다.
""".strip()

    result = score_x_answer(answer, item)

    assert result["section_alignment"] > 0.8
    assert result["body_alignment"] > 0.8
    assert result["comment_alignment"] > 0.8
    assert result["action_alignment"] > 0.8
    assert result["total"] >= 0.88
