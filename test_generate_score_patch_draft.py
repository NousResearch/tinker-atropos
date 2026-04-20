from generate_score_patch_draft import build_markdown_draft


def test_build_markdown_draft_summarizes_targets_and_replacements():
    data = {
        'chosen_ranks': {
            'chosen_x_rank': {'1': 3},
            'chosen_landing_rank': {'1': 2},
        },
        'top_strengthen_hints': [('브랜드 중복 없는 Ailit headline', 2), ('설명란과 이어지는 행동 문장', 1)],
        'top_penalize_hints': [('장황한 체크인 문구', 1)],
    }

    text = build_markdown_draft(data)

    assert '# Score Patch Draft' in text
    assert 'build_business_to_landing_loop.py' in text
    assert 'build_business_to_x_loop.py' in text
    assert 'build_business_to_retention_loop.py' in text
    assert '카테고리: headline' in text
    assert '카테고리: action' in text
    assert '카테고리: retention' in text
    assert 'Ailit 상담 신청으로 이어지는' in text
    assert '유튜브 설명란 첫 문장과 바로 이어지게 연결한다.' in text
    assert 'len(checkin) <= 72' in text
