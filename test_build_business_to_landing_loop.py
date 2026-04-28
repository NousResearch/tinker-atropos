from build_business_to_landing_loop import business_to_landing_variants, normalize_strategy_fields, postprocess_korean_copy, score_variant
from tinker_atropos.environments.min_landing_cro_tinker import LANDING_CRO_ITEMS, score_landing_answer


SAMPLE = """문제: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.
제안: Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청 수를 본다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.
"""


def test_variants_are_ranked_by_total_score_desc():
    variants = business_to_landing_variants(SAMPLE, count=3)

    totals = [item["scores"]["total"] for item in variants]
    assert totals == sorted(totals, reverse=True)
    assert [item["rank"] for item in variants] == [1, 2, 3]


def test_normalize_strategy_fields_makes_customer_and_offer_more_natural():
    fields = normalize_strategy_fields({
        "문제": "유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.",
        "고객": "AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.",
        "제안": "Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.",
        "실험": "오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률을 본다.",
        "지표": "클릭률 3퍼센트, 상담 신청 10건",
        "한줄결론": "지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.",
    })

    assert fields["customer_label"] == "일인 사업가"
    assert fields["offer_label"] == "Ailit 진단 세션"
    assert fields["problem_label"].startswith("상담 신청 이유")


def test_normalize_strategy_fields_handles_prospect_customer_phrase():
    fields = normalize_strategy_fields({
        "문제": "입문 장벽은 낮지만 신뢰 근거가 부족하다.",
        "고객": "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객",
        "제안": "신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.",
        "실험": "오늘 후기 블록 위치 하나만 바꾼다.",
        "지표": "클릭률, 신청 수, 전환율",
        "한줄결론": "지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.",
    })

    assert fields["customer_label"] == "예비 고객"
    assert fields["offer_label"] == "신뢰 근거 제안"
    assert fields["problem_label"] == "신뢰 근거가 약한 문제"


def test_score_variant_rewards_clear_headline_and_cta():
    variant = {
        "헤드라인": "일인 사업가를 위한 Ailit 진단 세션",
        "서브카피": "상담 신청 이유가 첫 화면에서 바로 보이게 한 가지 제안을 먼저 보여준다.",
        "핵심불릿": "문제 인식: 상담 신청 이유 약함 | 제안 초점: Ailit 진단 세션 | 바로 행동: 설명란 첫 문장 수정",
        "CTA": "지금 진단 신청하기",
        "실험": "설명란 첫 문장 하나만 바꾸기",
        "지표": "클릭률 3퍼센트, 상담 신청 10건",
    }
    result = score_variant(variant)

    assert result["headline_strength"] > 0.5
    assert result["cta_strength"] > 0.3
    assert result["beginner_friendliness"] > 0.3
    assert result["total"] > 0.55


def test_top_landing_variant_prefers_shorter_headline_and_subcopy():
    variants = business_to_landing_variants(SAMPLE, count=3)
    top = variants[0]

    assert len(top["헤드라인"]) <= 40
    assert len(top["서브카피"]) <= 70
    assert "제안을 먼저 보여준다를" not in top["서브카피"]


def test_landing_headline_avoids_long_problem_clause():
    strategy = """문제: 입문은 쉬우나 신뢰 근거는 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""
    variants = business_to_landing_variants(strategy, count=3)
    headline_text = "\n".join(v["헤드라인"] for v in variants)

    assert "입문은 쉬우나 신뢰 근거는 약하다를 줄이는" not in headline_text
    assert "신뢰 근거가 약한 문제를 줄이는" not in headline_text
    assert "신뢰를 먼저 확인하고 시작하는 신뢰 근거 제안" in headline_text or "지금 바로 비교하고 신청하는 신뢰 근거 제안" in headline_text or "예비 고객이 바로 이해하는" in headline_text


def test_top_landing_cta_is_action_oriented():
    variants = business_to_landing_variants(SAMPLE, count=3)
    top = variants[0]

    assert top["CTA"] in {
        "지금 진단 신청하기",
        "지금 핵심 제안 보기",
        "오늘 바로 시작하기",
        "바로 신청하기",
        "부담 없이 신청하기",
        "먼저 확인 후 신청하기",
    }


def test_lower_rank_headlines_are_still_marketing_friendly():
    strategy = """문제: 입문은 쉬우나 신뢰 근거는 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""
    variants = business_to_landing_variants(strategy, count=3)
    headline_text = "\n".join(v["헤드라인"] for v in variants)
    subcopy_text = "\n".join(v["서브카피"] for v in variants)

    assert "예비 고객을 위한 신뢰 근거 제안" in headline_text or "신뢰를 먼저 확인하고 시작하는" in headline_text
    assert "신뢰를 먼저 확인하고 시작하는 신뢰 근거 제안" in headline_text or "예비 고객을 위한 신뢰 근거 제안" in headline_text
    assert "지금 바로 비교하고 신청하는 신뢰 근거 제안" in headline_text or "부담 없이 신청으로 이어지는 신뢰 근거 제안" in headline_text
    assert "지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다" not in subcopy_text
    assert "신청 이유를 빠르게 납득하게 만든다" in subcopy_text or "바로 비교와 신청 흐름을 짧게 만든다" in subcopy_text
    ctas = "\n".join(v["CTA"] for v in variants)
    assert "지금 혜택 먼저 확인하기" in ctas or "부담 없이 신청하기" in ctas
    assert "지금 바로 신청하기" in ctas or "부담 없이 신청하기" in ctas


def test_landing_bullets_are_not_split_into_characters():
    variants = business_to_landing_variants(SAMPLE, count=3)

    assert "문 | 제 |" not in variants[0]["핵심불릿"]
    assert "문제 인식:" in variants[0]["핵심불릿"]


def test_vip_and_youtube_presets_avoid_awkward_prefixed_secondary_headlines():
    vip = "\n".join(v["헤드라인"] for v in business_to_landing_variants(SAMPLE, count=3, preset="vip"))
    youtube = "\n".join(v["헤드라인"] for v in business_to_landing_variants(SAMPLE, count=3, preset="youtube"))

    assert "VIP를 위한 신뢰를 먼저 보여주는" not in vip
    assert "VIP를 위한 예비 고객을 위한" not in vip
    assert "유튜브 시청자를 위한 신뢰를 먼저 보여주는" not in youtube


def test_ailit_preset_prefers_consulting_or_application_headline():
    variants = business_to_landing_variants(SAMPLE, count=3, preset="ailit")
    top = variants[0]
    headline_text = "\n".join(v["헤드라인"] for v in variants)

    assert top["헤드라인"].startswith("Ailit 상담 신청으로 이어지는") or top["헤드라인"].startswith("Ailit 상담으로 이어지는")
    assert top["CTA"] in {"지금 진단 신청하기", "부담 없이 신청하기", "먼저 확인 후 신청하기"}
    assert "Ailit 상담으로 이어지는 Ailit 진단 세션" not in headline_text


def test_ailit_preset_outranks_ordinarybiz_on_sample_landing():
    ordinary = business_to_landing_variants(SAMPLE, count=3, preset="ordinarybiz")[0]["scores"]["total"]
    ailit = business_to_landing_variants(SAMPLE, count=3, preset="ailit")[0]["scores"]["total"]

    assert ailit > ordinary


def test_ailit_preset_rewrites_secondary_and_tertiary_headlines_into_consulting_actions():
    variants = business_to_landing_variants(SAMPLE, count=3, preset="ailit")
    headline_text = "\n".join(v["헤드라인"] for v in variants)
    ctas = {v["CTA"] for v in variants}

    assert "Ailit 상담으로 이어지는 신뢰를 먼저 확인하고 시작하는 Ailit 진단 세션" not in headline_text
    assert "Ailit 상담으로 이어지는 지금 바로 비교하고 신청하는 Ailit 진단 세션" not in headline_text
    assert any(v["헤드라인"].startswith("Ailit 상담 전에 먼저 확인하는") for v in variants)
    assert any(v["헤드라인"].startswith("Ailit 상담 신청으로 이어지는") for v in variants)
    assert "먼저 확인 후 신청하기" in ctas
    assert "부담 없이 신청하기" in ctas


def test_ailit_consult_home_top_variant_scores_well_on_reward_eval():
    strategy = """문제: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.
제안: Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청 수를 본다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="ailit")[0]
    answer = "\n".join([
        "병목: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[0])

    assert top["헤드라인"].startswith("Ailit 상담 신청으로 이어지는") or top["헤드라인"].startswith("Ailit 상담 전에 먼저 확인하는")
    assert "퍼센트" in top["지표"]
    assert "건" in top["지표"]
    assert result["metric_quality"] >= 0.6
    assert result["total"] >= 0.8


def test_postprocess_korean_copy_fixes_particles():
    text = "상담 신청 이유 약함를 줄이는 Ailit 진단 세션와 Ailit 진단 세션를 앞세운다."
    fixed = postprocess_korean_copy(text)

    assert "약함를" not in fixed
    assert "세션를" not in fixed
    assert "세션와" not in fixed
    assert "약함을" in fixed or "약한 문제를" in fixed
    assert "세션을" in fixed
    assert "세션과" in fixed


def test_postprocess_korean_copy_fixes_customer_particles():
    text = "예비 고객가 멈추지 않게 신뢰 근거 제안를 먼저 보여준다."
    fixed = postprocess_korean_copy(text)

    assert "예비 고객가" not in fixed
    assert "제안를" not in fixed
    assert "예비 고객이" in fixed
    assert "제안을" in fixed


def test_bootcamp_trial_top_variant_scores_well_on_reward_eval():
    strategy = """문제: 무료 콘텐츠는 보지만 아직 결제를 망설여 첫 신청으로 안 이어진다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 부트캠프 체험 과제와 업그레이드 안내를 한 줄로 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 같은 체험 문장을 반복한다.
실험: 오늘 첫 화면 헤드라인과 버튼 문구 하나만 바꾸고 일주일 동안 체험 신청을 본다.
지표: 체험 신청 30건, 결제 전환율 7퍼센트, 이탈률 35퍼센트를 본다.
한줄결론: 지금은 체험 한 가지를 먼저 보여 무료에서 유료로 넘어가게 만드는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="bootcamp")[0]
    answer = "\n".join([
        "병목: 무료 콘텐츠는 보지만 아직 결제를 망설여 첫 신청으로 안 이어진다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[1])

    assert "부트캠프용" not in top["헤드라인"]
    assert "체험" in top["헤드라인"]
    assert "퍼센트" in top["지표"]
    assert "건" in top["지표"]
    assert result["copy_quality"] >= 0.6
    assert result["experiment_quality"] >= 0.45
    assert result["metric_quality"] >= 0.75
    assert result["total"] >= 0.82


def test_telegram_join_top_variant_scores_well_on_reward_eval():
    strategy = """문제: 설명란을 본 사람은 많은데 왜 텔레그램에 들어와야 하는지 약해서 합류 전환이 낮다.
고객: 영상은 봤지만 아직 채널 합류 필요성을 못 느끼는 시청자
제안: 텔레그램 합류 보상과 체크리스트 한 가지 이익을 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 같은 합류 문장을 반복한다.
실험: 오늘 첫 화면 헤드라인과 체크리스트 버튼 문구 하나만 바꾸고 일주일 동안 링크 클릭과 합류 전환율을 본다.
지표: 채널 유입 50건, 링크 클릭률 4퍼센트, 합류 전환율 20퍼센트를 본다.
한줄결론: 지금은 텔레그램 합류 뒤 바로 얻는 이익 한 가지를 먼저 보여주는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3)[0]
    answer = "\n".join([
        "병목: 설명란을 본 사람은 많은데 왜 텔레그램에 들어와야 하는지 약해서 합류 전환이 낮다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[2])

    assert "텔레그램" in top["헤드라인"]
    assert "체크리스트" in (top["헤드라인"] + " " + top["서브카피"] + " " + top["핵심불릿"])
    assert result["copy_quality"] >= 0.8
    assert result["experiment_quality"] >= 0.45
    assert result["metric_quality"] >= 0.6
    assert result["total"] >= 0.8


def test_telegram_join_top_variant_enriches_metrics_even_from_generic_strategy_metrics():
    strategy = """문제: 텔레그램, 체크리스트, 합류 기준에서 먼저 바꿀 차이가 보일 가능성이 크다. 때문에 지금 한 가지 우선 제안이 더 필요하다.
고객: 영상은 봤지만 아직 채널 합류 필요성을 못 느끼는 시청자
제안: 텔레그램 합류 보상과 체크리스트 한 가지 이익을 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 같은 합류 문장을 반복한다.
실험: 오늘 첫 화면 헤드라인과 체크리스트 버튼 문구 하나만 바꾸고 일주일 동안 클릭률을 본다.
지표: 클릭률, 상담 신청, 전환율을 함께 본다.
한줄결론: 지금은 텔레그램 합류 뒤 바로 얻는 이익 한 가지를 먼저 보여주는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3)[0]
    answer = "\n".join([
        "병목: 텔레그램 채널 합류 랜딩 개선에서 합류 전환이 낮다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[2])

    assert "클릭률" in top["지표"]
    assert "합류 전환율" in top["지표"]
    assert "퍼센트" in top["지표"]
    assert "건" in top["지표"]
    assert result["metric_quality"] >= 0.6
    assert result["total"] >= 0.83


def test_youtube_preset_shortens_generic_offer_sentence_into_compact_headline():
    strategy = """문제: 유튜브 시청자가 설명란 클릭이나 상담 신청으로 잘 넘어가지 않는다.
고객: 영상은 봤지만 아직 상담 신청 이유를 못 느끼는 유튜브 시청자
제안: 유튜브 설명란 첫 문장과 상담 CTA를 같은 제안으로 묶은 단일 제안을 먼저 보여준다.
채널: 유튜브 설명란과 고정 댓글에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장과 고정 댓글 CTA를 같은 한 문장으로 맞춘다.
지표: 설명란 클릭률, 상담 신청, 링크 도달 전 이탈을 함께 본다.
한줄결론: 지금은 영상 약속과 설명란 첫 문장을 같은 제안으로 다시 묶는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="youtube")[0]

    assert top["헤드라인"] == "유튜브 시청자가 바로 이해하는 텔레그램 체크리스트 합류 제안"
    assert len(top["헤드라인"]) <= 33


def test_vip_preset_shortens_repetitive_offer_sentence_into_compact_headline():
    strategy = """문제: 신규 유료 멤버가 첫 주 안에 관망 모드로 들어간다.
고객: 첫 주에 무엇을 먼저 해야 할지 헷갈리는 VIP 신규 유료 멤버
제안: VIP 온보딩 체크인을 텔레그램에서 바로 시작하게 만드는 단일 제안을 먼저 보여준다.
채널: 텔레그램 고정 공지와 체크인 스레드에서 같은 한 문장 제안을 반복한다.
실험: 오늘 첫 주 체크인 문구와 첫 과제 안내를 한 가지 행동 중심으로 다시 쓴다.
지표: 체크인 참여율, 첫 주 과제 완료율, 유료 유지율을 함께 본다.
한줄결론: 지금은 첫 주에 딱 한 가지 행동과 재참여 리듬을 먼저 보이게 만드는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="vip")[0]

    assert top["헤드라인"] == "VIP가 바로 시작하는 라이브 참여 신청 제안"
    assert "VIP를 위한 VIP" not in top["헤드라인"]
    assert len(top["헤드라인"]) <= 25


def test_vip_landing_can_shift_to_live_participation_copy_for_reward_quality():
    strategy = """문제: 신규 유료 멤버가 첫 주 안에 관망 모드로 들어간다.
고객: 첫 주에 무엇을 먼저 해야 할지 헷갈리는 VIP 신규 유료 멤버
제안: VIP 온보딩 체크인을 텔레그램에서 바로 시작하게 만드는 단일 제안을 먼저 보여준다.
채널: 텔레그램 고정 공지와 체크인 스레드에서 같은 한 문장 제안을 반복한다.
실험: 오늘 첫 주 체크인 문구와 첫 과제 안내를 한 가지 행동 중심으로 다시 쓴다.
지표: 체크인 참여율, 첫 주 과제 완료율, 유료 유지율을 함께 본다.
한줄결론: 지금은 첫 주에 딱 한 가지 행동과 재참여 리듬을 먼저 보이게 만드는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="vip")[0]
    answer = "\n".join([
        "병목: 유료 멤버이지만 아직 라이브 신청까지는 하지 않는 기존 고객이라서 참여 이유와 리플레이 보장이 첫 화면에서 약하다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[5])

    assert top["헤드라인"] == "VIP가 바로 시작하는 라이브 참여 신청 제안"
    assert top["CTA"] == "지금 라이브 신청하기"
    assert "리플레이" in (top['서브카피'] + ' ' + top['핵심불릿'])
    assert "신청 전환율" in top["지표"]
    assert "참여율" in top["지표"]
    assert "리플레이 시청률" in top["지표"]
    assert "퍼센트" in top["지표"]
    assert result["metric_quality"] >= 0.6
    assert result["keyword_coverage"] >= 0.75
    assert result["total"] >= 0.82


def test_youtube_landing_can_shift_to_telegram_join_copy_for_reward_quality():
    strategy = """문제: 유튜브 시청자가 설명란 클릭이나 상담 신청으로 잘 넘어가지 않는다.
고객: 영상은 봤지만 아직 상담 신청 이유를 못 느끼는 유튜브 시청자
제안: 유튜브 설명란 첫 문장과 상담 CTA를 같은 제안으로 묶은 단일 제안을 먼저 보여준다.
채널: 유튜브 설명란과 고정 댓글에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장과 고정 댓글 CTA를 같은 한 문장으로 맞춘다.
지표: 설명란 클릭률, 상담 신청, 링크 도달 전 이탈을 함께 본다.
한줄결론: 지금은 영상 약속과 설명란 첫 문장을 같은 제안으로 다시 묶는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="youtube")[0]
    answer = "\n".join([
        "병목: 설명란만 보고 끝나는 문제를 줄여야 하는데 텔레그램 합류 이유와 체크리스트 보상이 첫 화면에서 약하다.",
        f"개선안: {top['서브카피']}",
        f"카피수정: 헤드라인 {top['헤드라인']} / CTA {top['CTA']} / 핵심불릿 {top['핵심불릿']}",
        f"실험: {top['실험']}",
        f"지표: {top['지표']}",
    ])
    result = score_landing_answer(answer, LANDING_CRO_ITEMS[2])

    assert top["헤드라인"] == "유튜브 시청자가 바로 이해하는 텔레그램 체크리스트 합류 제안"
    assert "텔레그램" in (top['헤드라인'] + ' ' + top['서브카피'] + ' ' + top['핵심불릿'])
    assert "체크리스트" in (top['헤드라인'] + ' ' + top['서브카피'] + ' ' + top['핵심불릿'])
    assert "합류" in (top['헤드라인'] + ' ' + top['CTA'] + ' ' + top['핵심불릿'])
    assert "채널 유입" in top["지표"]
    assert "링크 클릭" in top["지표"]
    assert "합류 전환율" in top["지표"]
    assert "퍼센트" in top["지표"]
    assert "건" in top["지표"]
    assert result["metric_quality"] >= 0.6
    assert result["keyword_coverage"] >= 0.75
    assert result["total"] >= 0.85


def test_x_article_landing_builds_longform_specific_headline_and_cta():
    strategy = """문제: 긴 글은 한 문장 문제 정의와 한 개 사례, 그리고 마지막 한 가지 행동이 같은 흐름으로 붙을 때 더 강하게 작동할 가능성이 크다.
고객: 긴 글을 읽지만 아직 저장과 다음 행동까지 이어지지 않는 독자
제안: 첫 단락 한 줄과 사례 한 개, 마지막 행동 한 가지를 같은 흐름으로 붙인 아티클 제안을 먼저 보여준다.
채널: X 아티클 첫 단락과 랜딩 첫 화면을 같은 논리로 맞춘다.
실험: 오늘 첫 단락 한 줄과 사례 한 개를 바꾸고 저장 수와 클릭률 차이를 본다.
지표: 저장 수, 클릭률, 댓글 수, 전환율을 함께 본다.
한줄결론: 지금은 긴 글 첫 단락과 사례 한 개를 먼저 선명하게 만드는 것이 우선이다.
"""
    top = business_to_landing_variants(strategy, count=3, preset="x-article")[0]

    assert "아티클 독자" in top["헤드라인"]
    assert "사례형" in top["헤드라인"] or "저장" in top["헤드라인"]
    assert top["CTA"] == "지금 바로 핵심 보기"
    assert "첫 단락" in (top["서브카피"] + ' ' + top["핵심불릿"])
    assert "사례" in (top["서브카피"] + ' ' + top["핵심불릿"])
    assert "저장" in (top["서브카피"] + ' ' + top["지표"])
