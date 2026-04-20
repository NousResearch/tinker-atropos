from build_research_to_business_loop import research_to_business_variants
from tinker_atropos.environments.min_business_strategy_tinker import (
    BUSINESS_STRATEGY_ITEMS,
    score_business_answer,
)


SAMPLE = """가설: 경쟁사보다 우리 상품은 도입 장벽이 낮지만 신뢰 근거가 약할 가능성이 크다.
찾을정보: 가격, 핵심 제안, 후기, 무료 체험 여부를 먼저 비교해 본다.
비교기준: 가격 차이, 시작 장벽, 누구에게 맞는지, 바로 써볼 수 있는지 네 가지로 본다.
결론: 입문 장벽은 우리 쪽이 낮을 수 있지만 후기와 사례 노출은 경쟁사가 더 강할 수 있다.
다음행동: 오늘 경쟁사 셋의 랜딩 첫 화면과 가격 구간을 표로 정리한 뒤 우리 첫 화면 문구 하나를 바로 바꾼다.
"""

AILIT_SAMPLE = """가설: Ailit 상담 전환에서 지금 가장 약한 지점은 상담 신청 이유가 첫 화면에서 바로 안 보이는 것이다.
찾을정보: 가격 문구, 신뢰 근거, 상담 진입 CTA, 경쟁 대안 비교, 후기 노출 순서를 본다.
비교기준: 상담 전환율, 신뢰 요소 선명도, 제안 명확성, 입문 장벽, 클릭 후 이탈률을 함께 본다.
결론: 저가 포지셔닝은 강하지만 왜 지금 상담해야 하는지와 어떤 결과를 얻는지가 첫 화면에서 약하게 보일 가능성이 크다.
다음행동: 오늘 첫 화면 헤드라인과 CTA 한 줄을 상담 신청 직접 연결형으로 바꾼다.
"""

VIP_SAMPLE = """가설: CMDSPACE VIP 신규 유료 멤버가 첫 주 안에 이탈하는 가장 큰 이유는 무엇을 먼저 끝내야 하는지와 왜 바로 참여해야 하는지가 충분히 선명하지 않기 때문이다.
찾을정보: 첫 주 체크인 문구, 첫 과제 안내, 텔레그램 참여 흐름, 재방문 장치, 성공 사례 노출 순서를 본다.
비교기준: 체크인 참여율, 첫 주 과제 완료율, 재방문 수, 질문 발생 수, 유료 유지율을 함께 본다.
결론: 정보는 많지만 첫 주에 딱 한 가지 행동과 재참여 리듬이 선명하지 않으면 유료 멤버도 빠르게 관망 모드로 들어갈 가능성이 크다.
다음행동: 오늘 첫 주 체크인 문구와 첫 과제 안내를 한 가지 행동 중심으로 다시 쓴다.
"""

BOOTCAMP_SAMPLE = """가설: 부트캠프 무료 콘텐츠 소비자는 많지만 체험 신청과 유료 업그레이드 연결 이유가 아직 약할 가능성이 크다.
찾을정보: 무료 콘텐츠 흐름, 체험 과제 제안, 멤버십 업그레이드 문장, 후기 배치, 결제 전환 장벽을 본다.
비교기준: 체험 신청률, 결제 전환율, 첫 주 유지율, 장벽 문장, 업그레이드 연결 강도를 함께 본다.
결론: 무료에서 유료로 넘어가는 다리 문장과 체험 과제 제안이 약하면 예비 수강생이 바로 결제까지 가지 못할 가능성이 크다.
다음행동: 오늘 무료 콘텐츠 끝부분 제안과 랜딩 첫 화면에서 체험 과제 한 가지를 먼저 보여주는 문장으로 바꾼다.
"""

YOUTUBE_SAMPLE = """가설: 유튜브 설명란에서 상담이나 다음 행동으로 이어지는 문장이 약해서 외부 유입이 매출 전환까지 이어지지 않을 가능성이 크다.
찾을정보: 설명란 첫 문장, 상담 링크 위치, 클릭 이유 문장, 시청자 질문 흐름, 랜딩 첫 화면 연결을 본다.
비교기준: 클릭률, 상담 신청, 설명란 전환율, 첫 화면 일치도, 시청자 이해도를 함께 본다.
결론: 설명란 첫 문장과 랜딩 제안이 끊기면 시청자는 관심이 있어도 바로 상담 신청까지 이어지지 않을 가능성이 크다.
다음행동: 오늘 유튜브 설명란 첫 문장과 상담 CTA 한 줄을 같은 제안으로 다시 쓴다.
"""


def _to_answer_text(variant: dict) -> str:
    return "\n".join(
        f"{key}: {variant[key]}" for key in ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]
    )


def test_business_variants_are_ranked():
    variants = research_to_business_variants(SAMPLE, count=3)
    totals = [item["scores"]["total"] for item in variants]
    assert totals == sorted(totals, reverse=True)


def test_top_variant_uses_specific_customer_and_single_offer():
    variant = research_to_business_variants(SAMPLE, count=3)[0]
    assert "예비 고객" in variant["고객"] or "잠재 고객" in variant["고객"]
    assert "한 가지" in variant["제안"] or "단일" in variant["제안"]
    assert "오늘" in variant["실험"]


def test_top_variant_prefers_concrete_customer_label_for_downstream_landing():
    variant = research_to_business_variants(SAMPLE, count=3)[0]
    assert variant["고객"] == "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객"
    assert variant["제안"] == "신뢰 근거를 앞세운 단일 제안을 먼저 보여준다."


def test_problem_copy_is_shorter_than_raw_conclusion():
    variant = research_to_business_variants(SAMPLE, count=3)[0]
    assert len(variant["문제"]) < 90
    assert "후기와 사례 노출은 경쟁사가 더 강할 수 있다" not in variant["문제"]


def test_ailit_preset_places_offer_and_metrics_into_matching_sections():
    variant = research_to_business_variants(AILIT_SAMPLE, count=3, preset="ailit")[0]
    result = score_business_answer(_to_answer_text(variant), BUSINESS_STRATEGY_ITEMS[4])

    assert "Ailit" in variant["제안"]
    assert result["proposal_alignment"] >= 0.5
    assert result["metric_alignment"] >= 0.66
    assert result["section_alignment"] >= 0.72


def test_vip_preset_places_checkin_terms_into_proposal_and_metrics():
    variant = research_to_business_variants(VIP_SAMPLE, count=3, preset="vip")[0]
    result = score_business_answer(_to_answer_text(variant), BUSINESS_STRATEGY_ITEMS[2])

    assert "VIP" in variant["제안"]
    assert "체크인" in variant["제안"] or "온보딩" in variant["제안"]
    assert result["proposal_alignment"] >= 0.5
    assert result["metric_alignment"] >= 0.66
    assert result["section_alignment"] >= 0.72


def test_bootcamp_preset_places_trial_and_upgrade_terms_into_business_sections():
    variant = research_to_business_variants(BOOTCAMP_SAMPLE, count=3, preset="bootcamp")[0]
    result = score_business_answer(_to_answer_text(variant), BUSINESS_STRATEGY_ITEMS[1])

    assert "부트캠프" in variant["제안"]
    assert "체험" in variant["제안"] or "업그레이드" in variant["제안"]
    assert "체험 신청" in variant["지표"]
    assert result["proposal_alignment"] >= 0.5
    assert result["metric_alignment"] >= 0.66
    assert result["section_alignment"] >= 0.72


def test_youtube_preset_keeps_description_and_consult_terms_for_ailit_conversion():
    variant = research_to_business_variants(YOUTUBE_SAMPLE, count=3, preset="youtube")[0]
    result = score_business_answer(_to_answer_text(variant), BUSINESS_STRATEGY_ITEMS[0])

    assert "유튜브" in variant["채널"]
    assert "설명란" in variant["채널"]
    assert "클릭률" in variant["지표"]
    assert result["channel_fit"] >= 0.5
    assert result["metric_alignment"] >= 0.66
    assert result["section_alignment"] >= 0.72
