from build_business_to_x_loop import business_to_x_variants
from build_business_to_landing_loop import business_to_landing_variants
from build_business_to_retention_loop import business_to_retention_variants


SAMPLE = """문제: 입문은 쉬우나 신뢰 근거는 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""


def test_x_bootcamp_preset_changes_body_or_hook():
    top = business_to_x_variants(SAMPLE, count=3, preset="bootcamp")[0]
    assert "부트캠프" in top["본문"] or "부트캠프" in top["후크"]


def test_landing_vip_preset_changes_headline():
    top = business_to_landing_variants(SAMPLE, count=3, preset="vip")[0]
    assert "VIP" in top["헤드라인"]
    assert "VIP를 위한 일인 사업가가 바로 이해하는" not in top["헤드라인"]
    assert "VIP를 위한 바로 신청으로 이어지는" not in top["헤드라인"]
    assert "VIP를 위한" in top["헤드라인"] or "VIP가 바로 이해하는" in top["헤드라인"] or "VIP가 안심하고 이해하는" in top["헤드라인"]


def test_retention_bootcamp_preset_changes_checkin():
    top = business_to_retention_variants(SAMPLE, count=3, preset="bootcamp")[0]
    assert "부트캠프" in top["체크인메시지"]


def test_x_article_preset_changes_x_copy():
    top = business_to_x_variants(SAMPLE, count=3, preset="x-article")[0]
    assert "아티클" in top["본문"] or "긴 글" in top["본문"]


def test_youtube_preset_changes_landing_headline():
    top = business_to_landing_variants(SAMPLE, count=3, preset="youtube")[0]
    assert "유튜브" in top["헤드라인"] or "채널" in top["헤드라인"]
    assert "유튜브 시청자가 바로 이해하는 바로 신청으로 이어지는" not in top["헤드라인"]


def test_ailit_preset_changes_retention_copy():
    top = business_to_retention_variants(SAMPLE, count=3, preset="ailit")[0]
    assert "Ailit" in top["체크인메시지"] or "Ailit" in top["첫주미션"]


def test_preset_specific_scoring_changes_totals():
    x_base = business_to_x_variants(SAMPLE, count=3, preset="ordinarybiz")[0]["scores"]["total"]
    x_youtube = business_to_x_variants(SAMPLE, count=3, preset="youtube")[0]["scores"]["total"]
    x_vip = business_to_x_variants(SAMPLE, count=3, preset="vip")[0]["scores"]["total"]
    landing_base = business_to_landing_variants(SAMPLE, count=3, preset="ordinarybiz")[0]["scores"]["total"]
    landing_vip = business_to_landing_variants(SAMPLE, count=3, preset="vip")[0]["scores"]["total"]
    landing_ailit = business_to_landing_variants(SAMPLE, count=3, preset="ailit")[0]["scores"]["total"]
    retention_base = business_to_retention_variants(SAMPLE, count=3, preset="ordinarybiz")[0]["scores"]["total"]
    retention_bootcamp = business_to_retention_variants(SAMPLE, count=3, preset="bootcamp")[0]["scores"]["total"]
    retention_ailit = business_to_retention_variants(SAMPLE, count=3, preset="ailit")[0]["scores"]["total"]

    assert len({x_base, x_youtube, x_vip}) > 1
    assert len({landing_base, landing_vip, landing_ailit}) > 1
    assert len({retention_base, retention_bootcamp, retention_ailit}) > 1
