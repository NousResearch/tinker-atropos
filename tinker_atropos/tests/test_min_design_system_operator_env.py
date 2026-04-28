from tinker_atropos.environments.min_design_system_operator_tinker import (
    DESIGN_SYSTEM_OPERATOR_ITEMS,
    format_design_system_operator_prompt,
    generation_max_tokens,
    score_design_system_operator_answer,
)


def test_prompt_includes_design_system_contract_sections():
    prompt = format_design_system_operator_prompt(DESIGN_SYSTEM_OPERATOR_ITEMS[0])
    assert "DESIGN.md" in prompt
    for section in ["작업분류", "디자인계약", "토큰적용", "드리프트", "검증", "기록"]:
        assert section + ":" in prompt


def test_complete_answer_scores_high():
    item = DESIGN_SYSTEM_OPERATOR_ITEMS[0]
    answer = """
작업분류: Ailit 랜딩 첫 화면 디자인 개선이다. 알피 씨엘아이로 프로젝트 루트를 보고 브라우저 검증까지 닫는다.
디자인계약: DESIGN.md를 디자인 계약으로 먼저 확인하고 프로젝트 루트 기준 패치 후보만 제안한다.
토큰적용: 색상 글꼴 간격 모서리 버튼 카드 토큰을 적용한다.
드리프트: 피그마 테일윈드 코드 브라우저 화면 스크린샷 차이를 드리프트로 기록한다.
검증: lint 빌드 브라우저 검증 파일 존재 스크린샷 비교를 확인한다.
기록: 민이 바로 복붙할 수 있게 쉬운 말로 과장 없음 기준을 남긴다.
""".strip()
    assert score_design_system_operator_answer(answer, item)["total"] >= 0.95


def test_weak_answer_scores_low():
    item = DESIGN_SYSTEM_OPERATOR_ITEMS[0]
    answer = "예쁘게 모던하게 감각적으로 바꾸면 됩니다. 검증은 나중에 합니다."
    assert score_design_system_operator_answer(answer, item)["total"] < 0.35


def test_generation_max_tokens_caps_openrouter_smoke_length():
    assert generation_max_tokens(8192) == 768
    assert generation_max_tokens(128) == 128
