from generate_score_patch_file_draft import build_patch_text


def test_build_patch_text_includes_concrete_targets_and_replacements():
    data = {
        'top_strengthen_hints': [('브랜드 중복 없는 Ailit headline', 2), ('설명란과 이어지는 행동 문장', 1)],
        'top_penalize_hints': [('두 단계로 읽히는 CTA', 1), ('장황한 체크인 문구', 1)],
    }

    text = build_patch_text(data)

    assert '# Score Patch File Draft' in text
    assert 'suggested_changes:' in text
    assert 'file: "/Users/heomin/.hermes/hermes-agent/tinker-atropos/build_business_to_landing_loop.py"' in text
    assert 'file: "/Users/heomin/.hermes/hermes-agent/tinker-atropos/build_business_to_x_loop.py"' in text
    assert 'file: "/Users/heomin/.hermes/hermes-agent/tinker-atropos/build_business_to_retention_loop.py"' in text
    assert 'category: "headline"' in text
    assert 'category: "action"' in text
    assert 'category: "retention"' in text
    assert 'suggested_old:' in text
    assert 'suggested_new:' in text
    assert 'Ailit 상담 신청으로 이어지는' in text
    assert '유튜브 설명란과 함께 읽히게 연결한다.' in text
    assert 'len(checkin) <= 72' in text
