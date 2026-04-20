from generate_score_patch_v4a import build_patch, classify_hint, suggest_rule


def test_classify_hint_routes_common_feedback():
    assert classify_hint('신뢰 근거를 먼저 보여주는 headline') == 'headline'
    assert classify_hint('추상적인 CTA') == 'cta'
    assert classify_hint('행동이 선명한 문장') == 'action'
    assert classify_hint('체크인 문구가 약하다') == 'retention'



def test_classify_hint_routes_latest_feedback_hints():
    assert classify_hint('설명란과 이어지는 행동 문장') == 'action'
    assert classify_hint('브랜드 중복 없는 Ailit headline') == 'headline'
    assert classify_hint('긴 설명형 본문') == 'body'
    assert classify_hint('두 단계로 읽히는 CTA') == 'cta'
    assert classify_hint('장황한 체크인 문구') == 'retention'



def test_suggest_rule_returns_specific_replacements_for_known_hints():
    headline_rule = suggest_rule('신뢰 근거를 먼저 보여주는 headline')
    cta_rule = suggest_rule('추상적인 CTA')
    action_rule = suggest_rule('설명란과 이어지는 행동 문장')
    ailit_headline_rule = suggest_rule('브랜드 중복 없는 Ailit headline')

    assert headline_rule is not None
    assert 'HEADLINE_PATTERNS' in headline_rule['old'] or 'HEADLINE_PATTERNS' in headline_rule['comment']
    assert '신뢰' in headline_rule['new']
    assert cta_rule is not None
    assert 'CTA' in cta_rule['comment']
    assert action_rule is not None
    assert '설명란' in action_rule['new']
    assert ailit_headline_rule is not None
    assert 'strip_repeated_brand' in ailit_headline_rule['old']
    assert 'Ailit 상담 신청으로 이어지는' in ailit_headline_rule['new']



def test_build_patch_contains_concrete_replacements():
    data = {
        'top_strengthen_hints': [('브랜드 중복 없는 Ailit headline', 2), ('설명란과 이어지는 행동 문장', 1)],
        'top_penalize_hints': [('두 단계로 읽히는 CTA', 1), ('장황한 체크인 문구', 1)],
    }
    text = build_patch(data)
    assert '*** Begin Patch' in text
    assert '*** Update File:' in text
    assert 'build_business_to_landing_loop.py' in text
    assert 'build_business_to_x_loop.py' in text
    assert 'build_business_to_retention_loop.py' in text
    assert 'Ailit 상담 신청으로 이어지는' in text
    assert '유튜브 설명란과 함께 읽히게 연결한다.' in text
    assert '부담 없이 신청하기' in text
    assert 'len(checkin) <= 72' in text
    assert '두 단계로 읽히는 CTA' in text
    assert '장황한 체크인 문구' in text
    assert '*** End Patch' in text
