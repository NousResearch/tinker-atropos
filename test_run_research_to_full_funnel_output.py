from run_research_to_full_funnel import (
    apply_preset_to_best,
    build_best_summary,
    build_reward_replay_aggregate,
    choose_best_stage_variants,
    render_best_summary,
    render_execution_report,
    render_final_output,
    render_one_line_summary,
    render_quality_comparison_report,
    select_best_reward_item,
)


def test_render_final_output_is_brief_and_action_oriented():
    best = {
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
    text = render_final_output(best)

    assert "## Today" in text
    assert "## Assets" in text
    assert "## Retention" in text
    assert "행동:" in text
    assert "CTA:" in text


def test_render_one_line_summary_is_short_and_action_based():
    best = {
        "x": {"행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."},
        "landing": {"헤드라인": "예비 고객이 바로 이해하는 신뢰 근거 제안"},
        "retention": {"첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."},
    }
    text = render_one_line_summary(best)

    assert "오늘 할 일" in text
    assert "X:" in text
    assert "랜딩:" in text
    assert "유지:" in text
    assert len(text) < 220


def test_render_one_line_summary_changes_with_preset_label():
    best = {
        "x": {"행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."},
        "landing": {"헤드라인": "예비 고객이 바로 이해하는 신뢰 근거 제안"},
        "retention": {"첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."},
    }
    text = render_one_line_summary(best, preset="bootcamp")

    assert "부트캠프 오늘 할 일" in text


def test_render_one_line_summary_exposes_selection_mode():
    best = {
        "selection_mode": "reward",
        "x": {"행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."},
        "landing": {"헤드라인": "예비 고객이 바로 이해하는 신뢰 근거 제안"},
        "retention": {"첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."},
    }
    text = render_one_line_summary(best, preset="bootcamp")

    assert "선택기준: reward" in text


def test_render_execution_report_includes_preset_operator_note():
    business = [{"scores": {"total": 0.5}}]
    funnel = [{
        "x_variants": [{"scores": {"total": 0.7}, "행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."}],
        "landing_variants": [{"scores": {"total": 0.6}, "헤드라인": "유튜브 시청자가 바로 이해하는 제안"}],
        "retention_variants": [{"scores": {"total": 0.4}, "첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."}],
    }]
    text = render_execution_report("sample", business, funnel, preset="youtube")

    assert "preset: youtube" in text
    assert "operator_note:" in text
    assert "유튜브" in text
    assert "operator_checklist:" in text


def test_render_execution_report_exposes_selection_mode():
    best = {"selection_mode": "reward"}
    business = [{"scores": {"total": 0.5}}]
    funnel = [{
        "x_variants": [{"scores": {"total": 0.7}, "행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."}],
        "landing_variants": [{"scores": {"total": 0.6}, "헤드라인": "유튜브 시청자가 바로 이해하는 제안"}],
        "retention_variants": [{"scores": {"total": 0.4}, "첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."}],
    }]
    text = render_execution_report("sample", business, funnel, preset="youtube", best=best)

    assert "selection_mode: reward" in text


def test_render_execution_report_uses_best_selection_when_provided():
    best = {
        "selection_mode": "reward",
        "business": {"scores": {"total": 0.5}},
        "x": {"scores": {"total": 0.69}, "행동유도": "보상 기준으로 고른 엑스 행동"},
        "landing": {"scores": {"total": 0.51}, "헤드라인": "보상 기준으로 고른 랜딩 헤드라인"},
        "retention": {"scores": {"total": 0.40}, "첫주미션": "보상 기준으로 고른 유지 미션"},
    }
    business = [{"scores": {"total": 0.5}}]
    funnel = [{
        "x_variants": [{"scores": {"total": 0.7}, "행동유도": "생성기 기준 엑스 행동"}],
        "landing_variants": [{"scores": {"total": 0.6}, "헤드라인": "생성기 기준 랜딩 헤드라인"}],
        "retention_variants": [{"scores": {"total": 0.4}, "첫주미션": "생성기 기준 유지 미션"}],
    }]
    text = render_execution_report("sample", business, funnel, preset="ordinarybiz", best=best)

    assert "1. X 실행: 보상 기준으로 고른 엑스 행동" in text
    assert "2. 랜딩 적용: 보상 기준으로 고른 랜딩 헤드라인" in text
    assert "3. 유지 시작: 보상 기준으로 고른 유지 미션" in text
    assert "best_landing_score: 0.51" in text


def test_select_best_reward_item_prefers_matching_ailit_context():
    reference = "Ailit 상담 전환을 높이려면 유튜브 외부 유입과 상담 신청 전환을 같이 봐야 한다."

    selected = select_best_reward_item("business", reference, preset="ailit")

    assert "Ailit" in selected["item_summary"]
    assert selected["confidence"] > 0


def test_build_best_summary_attaches_reward_replay_to_all_stages():
    research_text = "가설: Ailit 상담 전환이 약하다.\n찾을정보: 유튜브 설명란과 랜딩 첫 화면을 본다.\n비교기준: 클릭률, 상담 신청, 전환율을 본다.\n결론: 상담 이유가 약하다.\n다음행동: 오늘 설명란 첫 문장과 랜딩 헤드라인을 바꾼다."
    business_variants = [{
        "rank": 1,
        "variant": 1,
        "문제": "유튜브 유입은 오지만 상담 신청 이유가 약하다.",
        "고객": "AI 도구에는 관심이 높지만 세팅 시간이 부족한 일인 사업가",
        "제안": "Ailit 진단 세션 한 가지를 먼저 보여준다.",
        "채널": "유튜브 설명란과 랜딩 첫 화면에서 바로 연결한다.",
        "실험": "오늘 설명란 첫 문장과 랜딩 헤드라인 하나만 바꾼다.",
        "지표": "클릭률, 상담 신청, 전환율을 본다.",
        "한줄결론": "지금은 Ailit 상담 이유를 한 줄로 선명하게 붙이는 것이 우선이다.",
        "scores": {"total": 0.91},
    }]
    funnel_results = [{
        "x_variants": [{
            "rank": 1,
            "variant": 1,
            "후크": "AI 도구를 많이 써도 상담 전환이 약한 이유는 설명란 첫 문장이 약하기 때문이다.",
            "본문": "Ailit 상담 이유를 유튜브 설명란 첫 문장에서 바로 말해야 클릭률과 상담 신청이 오른다.",
            "댓글유도": "지금 가장 약한 설명란 한 줄이 무엇인지 댓글로 남겨달라.",
            "행동유도": "오늘 설명란 첫 문장 하나만 바꿔보자.",
            "금지": "허풍 없이 한 가지 행동만 제안한다.",
            "scores": {"total": 0.88},
        }],
        "landing_variants": [{
            "rank": 1,
            "variant": 1,
            "헤드라인": "Ailit 상담으로 이어지는 진단 세션",
            "서브카피": "유튜브에서 들어온 일인 사업가가 왜 지금 상담해야 하는지 한 줄로 바로 이해하게 만든다.",
            "핵심불릿": "상담 이유 선명화 | 진단 흐름 단순화",
            "CTA": "지금 진단 신청하기",
            "실험": "오늘 헤드라인 한 줄만 바꾸고 상담 신청 전환율을 본다.",
            "지표": "클릭률, 상담 신청, 전환율",
            "scores": {"total": 0.86},
        }],
        "retention_variants": [{
            "rank": 1,
            "variant": 1,
            "체크인메시지": "Ailit 체크인: 오늘 한 가지는 설명란 첫 문장을 바꾸는 것이다.",
            "첫주미션": "오늘 설명란 첫 문장 하나만 바꾸고 결과를 기록한다.",
            "재참여장치": "하루 뒤 체크인 메시지로 다시 참여하게 만든다.",
            "운영원칙": "한 번에 하나만 바꾸고 텔레그램에서 확인한다.",
            "지표": "재방문율, 체크인 참여율, 이탈률",
            "scores": {"total": 0.79},
        }],
    }]

    best = build_best_summary(research_text, business_variants, funnel_results, preset="ailit")

    assert "reward_eval" in best["business"]
    assert "reward_eval" in best["x"]
    assert "reward_eval" in best["landing"]
    assert "reward_eval" in best["retention"]
    assert best["landing"]["reward_eval"]["scores"]["total"] > 0
    assert "Ailit" in best["landing"]["reward_eval"]["matched_item_summary"]


def test_render_execution_report_includes_reward_replay_section():
    best = {
        "business": {"reward_eval": {"scores": {"total": 0.82}, "matched_item_summary": "Ailit 상담 전환", "confidence": 0.75}},
        "x": {"reward_eval": {"scores": {"total": 0.78}, "matched_item_summary": "X 글 매출 전환", "confidence": 0.6}},
        "landing": {"reward_eval": {"scores": {"total": 0.81}, "matched_item_summary": "Ailit 상담 랜딩", "confidence": 0.8}},
        "retention": {"reward_eval": {"scores": {"total": 0.74}, "matched_item_summary": "VIP 첫 칠 일 리텐션", "confidence": 0.65}},
    }
    business = [{"scores": {"total": 0.5}}]
    funnel = [{
        "x_variants": [{"scores": {"total": 0.7}, "행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다."}],
        "landing_variants": [{"scores": {"total": 0.6}, "헤드라인": "유튜브 시청자가 바로 이해하는 제안"}],
        "retention_variants": [{"scores": {"total": 0.4}, "첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다."}],
    }]

    text = render_execution_report("sample", business, funnel, preset="ailit", best=best)

    assert "reward_replay:" in text
    assert "match=Ailit 상담 랜딩" in text


def test_render_best_summary_includes_reward_replay_lines():
    best = {
        "business": {
            "rank": 1,
            "variant": 1,
            "문제": "문제",
            "고객": "고객",
            "제안": "제안",
            "채널": "채널",
            "실험": "실험",
            "지표": "지표",
            "한줄결론": "한줄결론",
            "scores": {"total": 1.0},
            "reward_eval": {"scores": {"total": 0.84}, "matched_item_summary": "Ailit 상담 전환", "confidence": 0.9},
        }
    }

    text = render_best_summary(best)

    assert "reward_total: 0.84" in text


def test_build_reward_replay_aggregate_summarizes_stage_alignment():
    funnel_results = [{
        "source_business_rank": 1,
        "x_variants": [
            {"rank": 1, "scores": {"total": 0.91}, "reward_eval": {"scores": {"total": 0.72}}},
            {"rank": 2, "scores": {"total": 0.83}, "reward_eval": {"scores": {"total": 0.88}}},
        ],
        "landing_variants": [
            {"rank": 1, "scores": {"total": 0.87}, "reward_eval": {"scores": {"total": 0.81}}},
        ],
        "retention_variants": [
            {"rank": 1, "scores": {"total": 0.76}, "reward_eval": {"scores": {"total": 0.69}}},
            {"rank": 2, "scores": {"total": 0.74}, "reward_eval": {"scores": {"total": 0.73}}},
        ],
    }]
    best = {
        "business": {"rank": 1, "scores": {"total": 0.93}, "reward_eval": {"scores": {"total": 0.9}}},
        "x": funnel_results[0]["x_variants"][0],
        "landing": funnel_results[0]["landing_variants"][0],
        "retention": funnel_results[0]["retention_variants"][0],
    }

    aggregate = build_reward_replay_aggregate(best, funnel_results)

    assert aggregate["business"]["variant_count"] == 1
    assert aggregate["x"]["variant_count"] == 2
    assert aggregate["x"]["best_reward_rank"] == 2
    assert aggregate["retention"]["reward_max"] == 0.73
    assert aggregate["landing"]["top_generator_reward"] == 0.81


def test_render_execution_report_includes_reward_replay_aggregate_section():
    best = {
        "business": {"reward_eval": {"scores": {"total": 0.82}, "matched_item_summary": "Ailit 상담 전환", "confidence": 0.75}},
        "x": {"reward_eval": {"scores": {"total": 0.78}, "matched_item_summary": "X 글 매출 전환", "confidence": 0.6}},
        "landing": {"reward_eval": {"scores": {"total": 0.81}, "matched_item_summary": "Ailit 상담 랜딩", "confidence": 0.8}},
        "retention": {"reward_eval": {"scores": {"total": 0.74}, "matched_item_summary": "VIP 첫 칠 일 리텐션", "confidence": 0.65}},
    }
    business = [{"scores": {"total": 0.5}}]
    funnel = [{
        "x_variants": [
            {"rank": 1, "scores": {"total": 0.7}, "행동유도": "오늘 후기 블록 위치 하나만 바꾸고 전환율을 본다.", "reward_eval": {"scores": {"total": 0.64}}},
            {"rank": 2, "scores": {"total": 0.69}, "행동유도": "오늘 제목 한 줄만 바꾼다.", "reward_eval": {"scores": {"total": 0.81}}},
        ],
        "landing_variants": [{"rank": 1, "scores": {"total": 0.6}, "헤드라인": "유튜브 시청자가 바로 이해하는 제안", "reward_eval": {"scores": {"total": 0.77}}}],
        "retention_variants": [{"rank": 1, "scores": {"total": 0.4}, "첫주미션": "먼저 후기 블록 위치 하나만 바꾸고 결과를 남긴다.", "reward_eval": {"scores": {"total": 0.71}}}],
    }]

    text = render_execution_report("sample", business, funnel, preset="ailit", best=best)

    assert "reward_replay_aggregate:" in text
    assert "x: variants=2" in text
    assert "best_reward_rank=2" in text


def test_render_quality_comparison_report_highlights_reward_preferred_stages():
    generator_best = {
        "selection_mode": "generator",
        "business": {"rank": 1, "variant": 1, "scores": {"total": 0.9}, "reward_eval": {"scores": {"total": 0.82}}},
        "x": {"rank": 1, "variant": 1, "scores": {"total": 0.91}, "reward_eval": {"scores": {"total": 0.72}}},
        "landing": {"rank": 1, "variant": 1, "scores": {"total": 0.8}, "reward_eval": {"scores": {"total": 0.75}}},
        "retention": {"rank": 1, "variant": 1, "scores": {"total": 0.74}, "reward_eval": {"scores": {"total": 0.49}}},
        "reward_replay_aggregate": {
            "business": {"variant_count": 1},
            "x": {"variant_count": 2},
            "landing": {"variant_count": 2},
            "retention": {"variant_count": 2},
        },
    }
    reward_best = {
        "selection_mode": "reward",
        "business": {"rank": 1, "variant": 1, "scores": {"total": 0.9}, "reward_eval": {"scores": {"total": 0.82}}},
        "x": {"rank": 2, "variant": 2, "scores": {"total": 0.83}, "reward_eval": {"scores": {"total": 0.88}}},
        "landing": {"rank": 2, "variant": 2, "scores": {"total": 0.78}, "reward_eval": {"scores": {"total": 0.82}}},
        "retention": {"rank": 3, "variant": 3, "scores": {"total": 0.69}, "reward_eval": {"scores": {"total": 0.55}}},
        "reward_replay_aggregate": {
            "business": {"variant_count": 1},
            "x": {"variant_count": 2},
            "landing": {"variant_count": 2},
            "retention": {"variant_count": 2},
        },
    }

    text = render_quality_comparison_report("sample", generator_best, reward_best, preset="ordinarybiz")

    assert "권장 선택기준: reward" in text
    assert "landing" in text
    assert "retention" in text
    assert "보상 선택이 더 적합" in text
    assert "동일" in text


def test_choose_best_stage_variants_uses_reward_mode_when_requested():
    funnel = [{
        "x_variants": [
            {"rank": 1, "variant": 1, "scores": {"total": 0.9}, "reward_eval": {"scores": {"total": 0.71}}},
            {"rank": 2, "variant": 2, "scores": {"total": 0.84}, "reward_eval": {"scores": {"total": 0.86}}},
        ],
        "landing_variants": [
            {"rank": 1, "variant": 1, "scores": {"total": 0.8}, "reward_eval": {"scores": {"total": 0.75}}},
            {"rank": 2, "variant": 2, "scores": {"total": 0.78}, "reward_eval": {"scores": {"total": 0.82}}},
        ],
        "retention_variants": [
            {"rank": 1, "variant": 1, "scores": {"total": 0.74}, "reward_eval": {"scores": {"total": 0.49}}},
            {"rank": 3, "variant": 3, "scores": {"total": 0.69}, "reward_eval": {"scores": {"total": 0.55}}},
        ],
    }]

    chosen = choose_best_stage_variants(funnel, selection_mode="reward")

    assert chosen["x"]["variant"] == 2
    assert chosen["landing"]["variant"] == 2
    assert chosen["retention"]["variant"] == 3


def test_choose_best_stage_variants_defaults_to_generator_mode():
    funnel = [{
        "x_variants": [
            {"rank": 1, "variant": 1, "scores": {"total": 0.9}, "reward_eval": {"scores": {"total": 0.71}}},
            {"rank": 2, "variant": 2, "scores": {"total": 0.84}, "reward_eval": {"scores": {"total": 0.86}}},
        ],
        "landing_variants": [{"rank": 1, "variant": 1, "scores": {"total": 0.8}, "reward_eval": {"scores": {"total": 0.75}}}],
        "retention_variants": [{"rank": 1, "variant": 1, "scores": {"total": 0.74}, "reward_eval": {"scores": {"total": 0.49}}}],
    }]

    chosen = choose_best_stage_variants(funnel, selection_mode="generator")

    assert chosen["x"]["variant"] == 1


def test_full_funnel_reward_selection_mode_changes_best_summary_choice(tmp_path, monkeypatch, capsys):
    import sys
    import run_research_to_full_funnel as module

    input_path = tmp_path / "sample.txt"
    input_path.write_text("가설: 테스트\n찾을정보: 테스트\n비교기준: 테스트\n결론: 테스트\n다음행동: 테스트", encoding="utf-8")

    monkeypatch.setattr(module, "research_to_business_variants", lambda *args, **kwargs: [{
        "rank": 1,
        "variant": 1,
        "문제": "문제",
        "고객": "고객",
        "제안": "제안",
        "채널": "채널",
        "실험": "실험",
        "지표": "지표",
        "한줄결론": "한줄결론",
        "scores": {"total": 1.0},
    }])
    monkeypatch.setattr(module, "business_to_x_variants", lambda *args, **kwargs: [
        {"rank": 1, "variant": 1, "후크": "가", "본문": "나", "댓글유도": "다", "행동유도": "라", "금지": "마", "scores": {"total": 0.9}},
        {"rank": 2, "variant": 2, "후크": "가2", "본문": "나2", "댓글유도": "다2", "행동유도": "라2", "금지": "마2", "scores": {"total": 0.8}},
    ])
    monkeypatch.setattr(module, "business_to_landing_variants", lambda *args, **kwargs: [{"rank": 1, "variant": 1, "헤드라인": "헤", "서브카피": "서", "핵심불릿": "불", "CTA": "씨", "실험": "실", "지표": "지", "scores": {"total": 1.0}}])
    monkeypatch.setattr(module, "business_to_retention_variants", lambda *args, **kwargs: [{"rank": 1, "variant": 1, "체크인메시지": "체", "첫주미션": "첫", "재참여장치": "재", "운영원칙": "운", "지표": "지", "scores": {"total": 1.0}}])

    def fake_attach(research_text, funnel_results, preset="ordinarybiz"):
        funnel_results[0]["x_variants"][0]["reward_eval"] = {"scores": {"total": 0.7}}
        funnel_results[0]["x_variants"][1]["reward_eval"] = {"scores": {"total": 0.91}}
        funnel_results[0]["landing_variants"][0]["reward_eval"] = {"scores": {"total": 0.8}}
        funnel_results[0]["retention_variants"][0]["reward_eval"] = {"scores": {"total": 0.8}}
        funnel_results[0]["strategy"]["reward_eval"] = {"scores": {"total": 0.8}}
        return funnel_results

    monkeypatch.setattr(module, "attach_reward_replay_to_funnel_results", fake_attach)

    monkeypatch.setattr(sys, "argv", [
        "run_research_to_full_funnel.py",
        str(input_path),
        "--json",
        "--selection-mode",
        "reward",
    ])

    module.main()
    out = capsys.readouterr().out

    assert '"variant": 2' in out


def test_apply_preset_to_best_keeps_downstream_copy_without_double_prefixing():
    best = {
        "business": {"한줄결론": "지금은 한 가지 제안으로 신뢰를 먼저 붙이는 것이 우선이다."},
        "x": {"본문": "Ailit 상담 제안으로 자연스럽게 이어지게 정리한다."},
        "landing": {"헤드라인": "Ailit 상담 신청으로 이어지는 진단 세션"},
        "retention": {"체크인메시지": "Ailit 체크인: 오늘은 이 한 가지만 끝내면 됩니다."},
    }

    updated = apply_preset_to_best(best, preset="ailit")

    assert updated["landing"]["헤드라인"] == "Ailit 상담 신청으로 이어지는 진단 세션"
    assert updated["x"]["본문"] == "Ailit 상담 제안으로 자연스럽게 이어지게 정리한다."
    assert updated["retention"]["체크인메시지"] == "Ailit 체크인: 오늘은 이 한 가지만 끝내면 됩니다."
    assert "Ailit 상담 전환 흐름" in updated["business"]["한줄결론"]


def test_render_final_output_changes_with_preset_context():
    best = {
        "business": {"한줄결론": "지금은 한 가지 제안으로 신뢰를 먼저 붙이는 것이 우선이다."},
        "x": {"후크": "후크", "본문": "본문", "행동유도": "오늘 한 가지 행동"},
        "landing": {"헤드라인": "헤드라인", "서브카피": "서브카피", "CTA": "CTA"},
        "retention": {"체크인메시지": "체크인", "첫주미션": "미션", "재참여장치": "재참여"},
    }
    ordinary = render_final_output(best)
    bootcamp = render_final_output(best, preset="bootcamp")
    vip = render_final_output(best, preset="vip")
    assert "## Today" in ordinary
    assert "## Assets" in ordinary
    assert "## Retention" in ordinary
    assert "Bootcamp Brief" in bootcamp
    assert "VIP Brief" in vip
    assert "초점: 실전 과제" in bootcamp
    assert "초점: 빠른 실행" in vip
    assert "## Checklist" in bootcamp
    assert "## Checklist" in vip


def test_full_funnel_passes_preset_to_business_generator(tmp_path, monkeypatch, capsys):
    import json
    import sys
    import run_research_to_full_funnel as module

    input_path = tmp_path / "sample.txt"
    input_path.write_text("가설: 테스트\n찾을정보: 테스트\n비교기준: 테스트\n결론: 테스트\n다음행동: 테스트", encoding="utf-8")

    seen = {}

    def fake_business(research_text, count=3, preset=None):
        seen["preset"] = preset
        return [{
            "rank": 1,
            "variant": 1,
            "문제": "문제",
            "고객": "고객",
            "제안": "제안",
            "채널": "채널",
            "실험": "실험",
            "지표": "지표",
            "한줄결론": "한줄결론",
            "scores": {"total": 1.0},
        }]

    monkeypatch.setattr(module, "research_to_business_variants", fake_business)
    monkeypatch.setattr(module, "business_to_x_variants", lambda *args, **kwargs: [{"rank": 1, "variant": 1, "scores": {"total": 1.0}}])
    monkeypatch.setattr(module, "business_to_landing_variants", lambda *args, **kwargs: [{"rank": 1, "variant": 1, "scores": {"total": 1.0}}])
    monkeypatch.setattr(module, "business_to_retention_variants", lambda *args, **kwargs: [{"rank": 1, "variant": 1, "scores": {"total": 1.0}}])

    monkeypatch.setattr(sys, "argv", [
        "run_research_to_full_funnel.py",
        str(input_path),
        "--json",
        "--preset",
        "ailit",
    ])

    module.main()
    capsys.readouterr()

    assert seen["preset"] == "ailit"
