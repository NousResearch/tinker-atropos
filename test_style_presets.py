from copy import deepcopy

from run_research_to_full_funnel import apply_preset_to_best


def sample_best():
    return {
        "business": {"한줄결론": "지금은 한 가지 제안으로 신뢰를 먼저 붙이는 것이 우선이다."},
        "x": {
            "후크": "입문은 쉬우나 신뢰 근거는 약하다.",
            "본문": "핵심은 신뢰 근거 제안에 초점을 모으는 것이다.",
            "행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다.",
        },
        "landing": {
            "헤드라인": "예비 고객이 바로 이해하는 신뢰 근거 제안",
            "서브카피": "핵심은 신뢰 근거 제안을 앞세워 신뢰 근거가 약한 문제를 바로 해결하게 만드는 것이다.",
            "CTA": "오늘 바로 시작하기",
        },
        "retention": {
            "체크인메시지": "부담 없이 오늘 체크할 한 가지는 이것입니다: 후기 블록 위치 하나만 바꾼다.",
            "첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다.",
            "재참여장치": "하루 뒤 짧은 확인 메시지로 다시 돌아오게 만든다.",
        },
    }


def test_bootcamp_preset_adds_learning_context():
    best = apply_preset_to_best(deepcopy(sample_best()), "bootcamp")
    assert "부트캠프" in best["landing"]["헤드라인"] or "부트캠프" in best["x"]["본문"]
    assert "실전" in best["retention"]["체크인메시지"] or "실전" in best["business"]["한줄결론"]


def test_vip_preset_adds_premium_context():
    best = apply_preset_to_best(deepcopy(sample_best()), "vip")
    assert "VIP" in best["landing"]["헤드라인"] or "VIP" in best["retention"]["체크인메시지"]


def test_ordinarybiz_preset_keeps_default_tone_without_errors():
    best = apply_preset_to_best(deepcopy(sample_best()), "ordinarybiz")
    assert "신뢰" in best["landing"]["헤드라인"]
    assert "오늘" in best["x"]["행동유도"]


def test_ailit_preset_adds_consulting_context():
    best = apply_preset_to_best(deepcopy(sample_best()), "ailit")
    assert "Ailit" in best["landing"]["헤드라인"] or "Ailit" in best["business"]["한줄결론"]


def test_youtube_preset_adds_channel_context():
    best = apply_preset_to_best(deepcopy(sample_best()), "youtube")
    assert "유튜브" in best["x"]["본문"] or "유튜브" in best["landing"]["헤드라인"]


def test_x_article_preset_adds_longform_context():
    best = apply_preset_to_best(deepcopy(sample_best()), "x-article")
    assert "아티클" in best["x"]["본문"] or "긴 글" in best["business"]["한줄결론"]
