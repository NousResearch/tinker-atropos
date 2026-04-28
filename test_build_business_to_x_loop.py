from build_business_to_x_loop import business_to_x_variants, score_variant


SAMPLE = """문제: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.
제안: Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청 수를 본다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.
"""


def test_variants_are_ranked_by_total_score_desc():
    variants = business_to_x_variants(SAMPLE, count=3)

    totals = [item["scores"]["total"] for item in variants]
    assert totals == sorted(totals, reverse=True)
    assert [item["rank"] for item in variants] == [1, 2, 3]


def test_score_variant_rewards_beginner_friendly_and_brief_body():
    variant = {
        "후크": "지금 막히는 이유는 도구가 아니라 흐름이 없기 때문이다.",
        "본문": "핵심은 한 가지 제안을 먼저 보여주는 것이다. 쉬운 말로 바로 이해되게 만든다.",
        "댓글유도": "지금 가장 막힌 한 지점을 댓글로 남겨달라.",
        "행동유도": "오늘 설명란 첫 문장 하나만 바꿔보자.",
        "금지": "과장 없이 오늘 할 한 가지 행동만 말한다.",
    }
    result = score_variant(variant)

    assert result["beginner_friendliness"] > 0.5
    assert result["body_brevity"] > 0.5
    assert result["total"] > 0.58


def test_score_variant_penalizes_jargon_and_long_body():
    variant = {
        "후크": "혁신적인 시대라서 무조건 바꿔야 한다.",
        "본문": "퍼널과 레버리지와 파이프라인을 고도화해야 하며 이것저것 모두 동시에 최적화해야 한다는 긴 설명을 계속 이어가며 핵심 없이 장황하게 쓴다.",
        "댓글유도": "의견 부탁드립니다.",
        "행동유도": "추후 더 검토해보자.",
        "금지": "없음.",
    }
    result = score_variant(variant)

    assert result["beginner_friendliness"] < 0.5
    assert result["body_brevity"] <= 1.0
    assert result["hype_penalty"] < 0.0
    assert result["total"] < 0.35


def test_top_x_variant_avoids_awkward_offer_particle_chain():
    strategy = """문제: 입문 장벽은 낮지만 신뢰 근거가 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""
    top = business_to_x_variants(strategy, count=3)[0]

    assert "보여준다. 로" not in top["본문"]
    assert "제안 제안" not in top["본문"]
    assert "제안 로" not in top["본문"]
    assert "제안이고" in top["본문"] or "초점을 모으는" in top["본문"]


def test_youtube_preset_body_keeps_action_link_visible():
    top = business_to_x_variants(SAMPLE, count=3, preset="youtube")[0]

    assert "설명란" in top["본문"] or "오늘 할 일은" in top["본문"]


def test_bootcamp_preset_top_variant_passes_reward_threshold_for_paid_conversion():
    strategy = """문제: 부트캠프 결제 뒤 첫 주에 무엇부터 해야 할지 몰라 과제 진입 전에 멈춘다.
고객: 결제는 했지만 아직 첫 체험 과제와 체크인 습관이 없는 신규 부트캠프 멤버
제안: 부트캠프 체험 과제와 멤버십 업그레이드를 같은 문장으로 묶은 단일 제안을 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 부트캠프 체험과 업그레이드 이유를 같은 문장으로 반복한다.
실험: 오늘 체험 과제 제안 한 줄만 바꾸고 일주일 동안 체험 신청과 결제 전환율을 본다.
지표: 체험 신청, 결제 전환율, 첫 주 유지율을 함께 본다.
한줄결론: 지금은 무료에서 유료로 넘어가는 설명란 한 줄과 체험 과제 한 가지를 먼저 선명하게 붙이는 것이 우선이다.
"""
    from tinker_atropos.environments.min_x_strategy_tinker import X_STRATEGY_ITEMS, score_x_answer

    top = business_to_x_variants(strategy, count=3, preset="bootcamp")[0]
    result = score_x_answer("\n".join([
        f"후크: {top['후크']}",
        f"본문: {top['본문']}",
        f"댓글유도: {top['댓글유도']}",
        f"행동유도: {top['행동유도']}",
        f"금지: {top['금지']}",
    ]), X_STRATEGY_ITEMS[1])

    assert "부트캠프" in top["본문"]
    assert "체험" in top["본문"]
    assert "설명란" in top["본문"] or "설명란" in top["행동유도"]
    assert result["engagement"] >= 0.6
    assert result["single_action_clarity"] >= 0.6
    assert result["body_alignment"] >= 0.75
    assert result["total"] >= 0.8


def test_ailit_preset_top_variant_passes_reward_threshold_for_entry_product_click():
    strategy = """문제: Ailit 상담 전환에서 지금 가장 약한 지점은 상담 신청 이유가 첫 화면에서 바로 안 보이는 것이다.
고객: 상담은 부담스럽지만 작은 결제는 시도할 수 있는 잠재 고객
제안: Ailit 입문 상품으로 먼저 반응을 확인하고 상담 업셀로 이어지는 단일 제안을 먼저 보여준다.
채널: 유튜브 설명란과 랜딩 첫 화면에서 Ailit 상담 이유를 같은 한 문장으로 반복한다.
실험: 오늘 상담 헤드라인과 CTA 한 줄만 바꾸고 일주일 동안 클릭률과 상담 신청을 본다.
지표: 입문 상품 구매, 상담 전환, 업셀 전환율을 함께 본다.
한줄결론: 지금은 상담보다 쉬운 첫 행동을 먼저 보여주는 것이 우선이다.
"""
    from tinker_atropos.environments.min_x_strategy_tinker import X_STRATEGY_ITEMS, score_x_answer

    top = business_to_x_variants(strategy, count=3, preset="ailit")[0]
    result = score_x_answer("\n".join([
        f"후크: {top['후크']}",
        f"본문: {top['본문']}",
        f"댓글유도: {top['댓글유도']}",
        f"행동유도: {top['행동유도']}",
        f"금지: {top['금지']}",
    ]), X_STRATEGY_ITEMS[3])

    assert "Ailit" in top["본문"]
    assert "입문 상품" in top["본문"]
    assert "링크" in (top["본문"] + ' ' + top["행동유도"])
    assert "상담" in top["본문"]
    assert "무엇인지" in top["댓글유도"] or "?" in top["댓글유도"]
    assert result["actionability"] >= 0.8
    assert result["single_action_clarity"] >= 0.8
    assert result["body_alignment"] >= 1.0
    assert result["total"] >= 0.9


def test_vip_preset_top_variant_passes_reward_threshold_for_reengagement_checkin():
    strategy = """문제: VIP 멤버가 첫 주 이후 점점 조용해지고 운영자가 먼저 말을 걸 타이밍을 놓친다.
고객: 커뮤니티를 운영하지만 조용한 유료 멤버가 늘어나는 운영자
제안: VIP 재참여 체크인 문장 하나를 먼저 정하고 운영자가 바로 보내게 만든다.
채널: 텔레그램 공지와 체크인 스레드에서 같은 재참여 문장을 반복한다.
실험: 오늘 VIP 체크인 문장 한 줄만 바꾸고 일주일 동안 재참여율과 답장 수를 본다.
지표: 재참여율, 체크인 응답률, 이탈률을 함께 본다.
한줄결론: 지금은 운영자가 보낼 체크인 한 줄을 먼저 선명하게 만드는 것이 우선이다.
"""
    from tinker_atropos.environments.min_x_strategy_tinker import X_STRATEGY_ITEMS, score_x_answer

    top = business_to_x_variants(strategy, count=3, preset="vip")[0]
    result = score_x_answer("\n".join([
        f"후크: {top['후크']}",
        f"본문: {top['본문']}",
        f"댓글유도: {top['댓글유도']}",
        f"행동유도: {top['행동유도']}",
        f"금지: {top['금지']}",
    ]), X_STRATEGY_ITEMS[8])

    assert "VIP" in top["본문"]
    assert "재참여" in (top["후크"] + ' ' + top["본문"] + ' ' + top["행동유도"])
    assert "체크인" in (top["본문"] + ' ' + top["행동유도"])
    assert "운영자" in (top["본문"] + ' ' + top["댓글유도"])
    assert "오늘" in top["행동유도"] and "한 줄" in top["행동유도"]
    assert result["actionability"] >= 0.8
    assert result["single_action_clarity"] >= 0.8
    assert result["body_alignment"] >= 1.0
    assert result["total"] >= 0.9


def test_x_article_preset_builds_longform_specific_x_copy():
    strategy = """문제: 긴 글은 한 문장 문제 정의와 한 개 사례, 그리고 마지막 한 가지 행동이 같은 흐름으로 붙을 때 더 강하게 작동할 가능성이 크다.
고객: 긴 글을 읽지만 아직 저장과 다음 행동까지 이어지지 않는 독자
제안: 첫 단락 한 줄과 사례 한 개, 마지막 행동 한 가지를 같은 흐름으로 붙인 아티클 제안을 먼저 보여준다.
채널: X 아티클 첫 단락과 랜딩 첫 화면을 같은 논리로 맞춘다.
실험: 오늘 첫 단락 한 줄과 사례 한 개를 바꾸고 저장 수와 클릭률 차이를 본다.
지표: 저장 수, 클릭률, 댓글 수, 전환율을 함께 본다.
한줄결론: 지금은 긴 글 첫 단락과 사례 한 개를 먼저 선명하게 만드는 것이 우선이다.
"""
    top = business_to_x_variants(strategy, count=3, preset="x-article")[0]

    assert "아티클" in (top["후크"] + ' ' + top["본문"])
    assert "첫 단락" in (top["본문"] + ' ' + top["행동유도"])
    assert "사례" in top["본문"]
    assert "저장" in (top["후크"] + ' ' + top["본문"] + ' ' + top["금지"])
    assert "오늘 지금" in top["행동유도"]
    assert "사례 한 개" in top["행동유도"]
