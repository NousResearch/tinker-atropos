from build_business_to_retention_loop import business_to_retention_variants, score_variant
from tinker_atropos.environments.min_membership_retention_tinker import MEMBERSHIP_RETENTION_ITEMS, score_retention_answer


SAMPLE = """문제: 입문은 쉬우나 신뢰 근거는 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""


def test_retention_variants_are_ranked():
    variants = business_to_retention_variants(SAMPLE, count=3)
    totals = [item["scores"]["total"] for item in variants]
    assert totals == sorted(totals, reverse=True)


def test_top_retention_variant_uses_operator_friendly_tone():
    top = business_to_retention_variants(SAMPLE, count=3)[0]
    assert "운영자" not in top["체크인메시지"]
    assert "부담 없이" in top["체크인메시지"] or "오늘은" in top["체크인메시지"]
    assert "진행 상황" in top["재참여장치"] or "확인 메시지" in top["재참여장치"]


def test_score_variant_rewards_brief_checkin():
    variant = {
        "체크인메시지": "부담 없이 오늘 체크할 한 가지는 이것입니다: 첫 문장 하나만 고친다.",
        "첫주미션": "먼저 첫 문장 하나만 고치고 결과를 남긴다.",
        "재참여장치": "하루 뒤 짧은 확인 메시지로 다시 돌아오게 만든다.",
        "운영원칙": "초보자도 바로 이해할 쉬운 말만 쓴다.",
        "지표": "클릭률, 신청 수, 전환율",
    }
    result = score_variant(variant)
    assert result["brevity"] > 0.5
    assert result["beginner_friendliness"] > 0.5


def test_top_retention_mission_stays_brief_after_shortening():
    top = business_to_retention_variants(SAMPLE, count=3)[0]
    assert len(top["첫주미션"]) <= 60
    assert ". 하고" not in top["첫주미션"]


def test_bootcamp_first_week_top_variant_scores_well_on_reward_eval():
    strategy = """문제: 부트캠프 결제 뒤 첫 주에 무엇부터 해야 할지 몰라 과제 진입 전에 멈춘다.
고객: 결제는 했지만 아직 첫 체험 과제와 체크인 습관이 없는 신규 부트캠프 멤버
제안: 첫 주 체험 미션 한 가지와 체크인 루프를 먼저 보여준다.
채널: 텔레그램 고정 공지와 체크인 스레드에서 같은 시작 문장을 반복한다.
실험: 오늘 첫날 안내 문구와 둘째 날 체크인 문구 하나만 바꾸고 일주일 동안 참여율을 본다.
지표: 첫 주 참여율 65퍼센트, 과제 완료율 50퍼센트, 이탈률 25퍼센트를 본다.
한줄결론: 지금은 첫날 미션 한 가지와 둘째 날 체크인을 붙여 초반 이탈을 줄이는 것이 우선이다.
"""
    top = business_to_retention_variants(strategy, count=3, preset="bootcamp")[0]
    answer = "\n".join([
        "이탈원인: 부트캠프 결제 뒤 첫 주에 무엇부터 해야 할지 몰라 과제 진입 전에 멈춘다.",
        f"온보딩수정: {top['첫주미션']}",
        f"리텐션장치: {top['재참여장치']}",
        f"운영메시지: {top['체크인메시지']} / 운영원칙 {top['운영원칙']}",
        f"지표: {top['지표']}",
    ])
    result = score_retention_answer(answer, MEMBERSHIP_RETENTION_ITEMS[1])

    assert "체험" in (top['체크인메시지'] + ' ' + top['첫주미션'])
    assert "체크인" in (top['재참여장치'] + ' ' + top['체크인메시지'])
    assert "퍼센트" in top["지표"]
    assert "건" in top["지표"]
    assert result["retention_mechanism"] >= 0.45
    assert result["metric_quality"] >= 0.54
    assert result["beginner_friendliness"] >= 0.4
    assert result["total"] >= 0.8


def test_ailit_preset_reranks_retention_variant_toward_reward_best():
    strategy = """문제: 입문은 쉬우나 신뢰 근거는 약하다. 때문에 지금 한 가지 우선 제안이 더 필요하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: Ailit 입문 상품으로 먼저 반응을 확인하고 상담 업셀로 이어지는 단일 제안을 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 Ailit 상담 이유를 같은 한 문장으로 반복한다.
실험: 오늘 상담 헤드라인과 CTA 한 줄만 바꾸고 일주일 동안 클릭률과 상담 신청을 본다.
지표: 입문 상품 구매, 상담 전환, 업셀 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""
    top = business_to_retention_variants(strategy, count=3, preset="ailit")[0]
    answer = "\n".join([
        "이탈원인: 구매 직후 후속 행동 없이 조용히 이탈하는 구간이라서 Ailit 멤버가 업셀 없이 조용히 멈추고 습관이 끊긴다.",
        f"온보딩수정: {top['첫주미션']}",
        f"리텐션장치: {top['재참여장치']}",
        f"운영메시지: {top['체크인메시지']} / 운영원칙 {top['운영원칙']}",
        f"지표: {top['지표']}",
    ])
    result = score_retention_answer(answer, MEMBERSHIP_RETENTION_ITEMS[2])

    assert top["variant"] == 1
    assert "체크인" in top["재참여장치"]
    assert "재방문율" in top["지표"]
    assert "텔레그램" in (top["재참여장치"] + ' ' + top["첫주미션"] + ' ' + top["체크인메시지"])
    assert result["specificity"] >= 0.5
    assert result["retention_mechanism"] >= 0.5
    assert result["metric_quality"] >= 0.5
    assert result["total"] >= 0.8


def test_vip_preset_top_variant_passes_reward_threshold_for_first_week_retention():
    strategy = """문제: VIP 결제 뒤 첫 주에 무엇부터 해야 할지 몰라 조용히 멈추는 멤버가 생긴다.
고객: 결제는 했지만 아직 습관화되지 않은 신규 VIP 멤버
제안: 첫 칠 일 온보딩 미션과 체크인 루프 하나만 먼저 강조하고 VIP과 체크인 연결 이유를 짧게 붙인다.
채널: 텔레그램 공지와 고정 메시지에서 VIP 체크인 한 문장을 같은 말로 반복한다.
실험: 오늘 첫 주 체크인 문장 하나만 바꾸고 일주일 동안 참여율과 재방문율을 본다.
지표: 첫 칠 일 참여율, 이탈률, 재방문율을 함께 본다.
한줄결론: 지금은 한 가지 체크인과 온보딩 리듬을 먼저 붙이는 것이 우선이다.
"""
    top = business_to_retention_variants(strategy, count=3, preset="vip")[0]
    answer = "\n".join([
        "이탈원인: 결제 직후 이틀 안에 조용히 이탈하는 구간이라서 VIP 멤버가 온보딩 없이 조용히 멈추고 습관이 끊긴다.",
        f"온보딩수정: {top['첫주미션']}",
        f"리텐션장치: {top['재참여장치']}",
        f"운영메시지: {top['체크인메시지']} / 운영원칙 {top['운영원칙']}",
        f"지표: {top['지표']}",
    ])
    result = score_retention_answer(answer, MEMBERSHIP_RETENTION_ITEMS[0])

    assert top["variant"] == 1
    assert "체크인" in top["체크인메시지"]
    assert "체크인" in top["재참여장치"] or "온보딩" in top["재참여장치"]
    assert "재방문율" in top["지표"]
    assert result["retention_mechanism"] >= 0.5
    assert result["metric_quality"] >= 0.5
    assert result["total"] >= 0.8


def test_youtube_preset_top_variant_passes_reward_threshold_for_telegram_activation_retention():
    strategy = """문제: 유튜브 시청자는 들어오지만 텔레그램 채널에서 첫 주 안에 말 한마디 없이 조용히 사라진다.
고객: 영상은 봤지만 아직 채널 안에서 무엇을 먼저 해야 할지 모르는 신규 합류자
제안: 유튜브 설명란 뒤 텔레그램 체크인 한 가지와 첫 참여 경험을 먼저 보여준다.
채널: 유튜브 설명란과 텔레그램 고정 공지에서 같은 시작 문장을 반복한다.
실험: 오늘 첫 주 체크인 문구와 자기소개 유도 문장 하나만 바꾸고 일주일 동안 발화율을 본다.
지표: 첫 주 발화율, 재방문율, 이탈률을 함께 본다.
한줄결론: 지금은 첫 참여 한 번을 만들고 체크인 습관을 붙이는 것이 우선이다.
"""
    top = business_to_retention_variants(strategy, count=3, preset="youtube")[0]
    answer = "\n".join([
        "이탈원인: 텔레그램 신규 합류자가 첫 주 안에 발화 경험 없이 조용히 사라지는 구간이라서 참여 습관이 붙기 전에 눈팅 상태로 멈춘다.",
        f"온보딩수정: {top['첫주미션']}",
        f"리텐션장치: {top['재참여장치']}",
        f"운영메시지: {top['체크인메시지']} / 운영원칙 {top['운영원칙']}",
        f"지표: {top['지표']}",
    ])
    result = score_retention_answer(answer, MEMBERSHIP_RETENTION_ITEMS[4])

    assert top["variant"] == 1
    assert top["체크인메시지"].startswith("유튜브 유입 체크인:")
    assert "텔레그램" in (top["체크인메시지"] + ' ' + top["첫주미션"] + ' ' + top["재참여장치"])
    assert "첫 주" in (top["체크인메시지"] + ' ' + top["첫주미션"] + ' ' + top["재참여장치"])
    assert "참여" in (top["체크인메시지"] + ' ' + top["첫주미션"] + ' ' + top["재참여장치"])
    assert "첫 주 발화율" in top["지표"]
    assert "재방문율" in top["지표"]
    assert "이탈률" in top["지표"]
    assert result["specificity"] >= 0.75
    assert result["retention_mechanism"] >= 0.75
    assert result["metric_quality"] >= 0.5
    assert result["total"] >= 0.85


def test_x_article_retention_builds_followup_for_saved_readers():
    strategy = """문제: 긴 글은 한 문장 문제 정의와 한 개 사례, 그리고 마지막 한 가지 행동이 같은 흐름으로 붙을 때 더 강하게 작동할 가능성이 크다.
고객: 긴 글을 읽지만 아직 저장과 다음 행동까지 이어지지 않는 독자
제안: 첫 단락 한 줄과 사례 한 개, 마지막 행동 한 가지를 같은 흐름으로 붙인 아티클 제안을 먼저 보여준다.
채널: X 아티클 첫 단락과 랜딩 첫 화면을 같은 논리로 맞춘다.
실험: 오늘 첫 단락 한 줄과 사례 한 개를 바꾸고 저장 수와 클릭률 차이를 본다.
지표: 저장 수, 클릭률, 댓글 수, 전환율을 함께 본다.
한줄결론: 지금은 긴 글 첫 단락과 사례 한 개를 먼저 선명하게 만드는 것이 우선이다.
"""
    top = business_to_retention_variants(strategy, count=3, preset="x-article")[0]

    assert top["체크인메시지"].startswith("아티클 후속 체크인:")
    assert "첫 단락" in (top["체크인메시지"] + ' ' + top["첫주미션"])
    assert "사례" in (top["체크인메시지"] + ' ' + top["첫주미션"])
    assert "저장" in (top["체크인메시지"] + ' ' + top["재참여장치"] + ' ' + top["지표"])
    assert "댓글" in (top["재참여장치"] + ' ' + top["지표"])
