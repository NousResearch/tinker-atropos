from __future__ import annotations

from pathlib import Path

from scripts.generate_min_hermes_policy_answers import evaluate_answers, generate_lane_answers, load_json

ROOT = Path(__file__).resolve().parent
BENCHMARK_PATH = ROOT / "research" / "min_hermes_offline_eval_v1.json"


def test_patched_policy_beats_current_policy() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = generate_lane_answers(benchmark, strong=False)
    patched_answers = generate_lane_answers(benchmark, strong=True)

    current_summary = evaluate_answers(benchmark, current_answers)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert current_summary["task_count"] == 15
    assert patched_summary["task_count"] == 15
    assert current_summary["task_pass_count"] == 15
    assert patched_summary["task_pass_count"] == 15
    assert patched_summary["mean_total"] >= current_summary["mean_total"]
    assert patched_summary["env_summary"]["min_landing_cro"] >= current_summary["env_summary"]["min_landing_cro"]
    assert patched_summary["env_summary"]["min_x_strategy"] >= current_summary["env_summary"]["min_x_strategy"]
    assert patched_summary["env_summary"]["min_membership_retention"] >= current_summary["env_summary"]["min_membership_retention"]


def test_patched_x_lane_surpasses_human_level() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_x_strategy"] >= 0.92


def test_patched_landing_lane_surpasses_nine_tenths() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_landing_cro"] >= 0.9


def test_patched_retention_lane_surpasses_nine_five() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_membership_retention"] >= 0.95


def test_patched_research_lane_surpasses_nine_nine() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_agentic_research"] >= 0.99


def test_patched_x_lane_surpasses_nine_nine() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_x_strategy"] >= 0.99


def test_patched_landing_lane_surpasses_nine_eight() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_landing_cro"] >= 0.98


def test_patched_business_lane_reaches_full_score() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    patched_answers = generate_lane_answers(benchmark, strong=True)
    patched_summary = evaluate_answers(benchmark, patched_answers)

    assert patched_summary["env_summary"]["min_business_strategy"] >= 1.0


def test_current_policy_template_reflects_current_generator_baseline() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = generate_lane_answers(benchmark, strong=False)
    current_summary = evaluate_answers(benchmark, current_answers)

    assert current_summary["mean_total"] >= 0.7
    assert current_summary["task_pass_count"] >= 4
    assert current_summary["env_summary"]["min_agentic_research"] >= 0.85
    assert current_summary["env_summary"]["min_x_strategy"] >= 0.7
    assert current_summary["env_summary"]["min_landing_cro"] >= 0.65


def test_current_policy_x_tasks_infer_bootcamp_and_youtube_presets_correctly() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    bootcamp_answer = current_answers["x-bootcamp-free-to-paid"]
    youtube_answer = current_answers["x-youtube-description-conversion"]

    assert "부트캠프" in bootcamp_answer
    assert "설명란" in bootcamp_answer
    assert "Ailit" not in bootcamp_answer
    assert "유튜브" in youtube_answer
    assert "설명란" in youtube_answer
    assert "Ailit" not in youtube_answer


def test_current_policy_x_answers_keep_all_must_terms_in_body_for_quality() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    ai_tools = current_answers["x-ai-tools-sales-structure"]
    youtube = current_answers["x-youtube-description-conversion"]

    assert "AI 도구" in ai_tools
    assert "매출" in ai_tools
    assert "유튜브" in ai_tools
    assert "상담" in ai_tools
    assert "유튜브" in youtube
    assert "설명란" in youtube
    assert "상담" in youtube
    assert "전환" in youtube


def test_current_policy_x_ai_tools_answer_strengthens_hook_and_action() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    ai_tools = current_answers["x-ai-tools-sales-structure"]

    assert "후크: 왜" in ai_tools
    assert "문제" in ai_tools
    assert "착각" in ai_tools
    assert "행동유도: 오늘 지금" in ai_tools
    assert "전환" in ai_tools
    assert "클릭률" in ai_tools
    assert "실험" in ai_tools


def test_current_policy_landing_answers_add_who_problem_and_ai_tool_copy_terms() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    bootcamp = current_answers["landing-bootcamp-trial"]
    telegram = current_answers["landing-telegram-join"]

    assert "누구 문제를 푸는 제안" in bootcamp
    assert "AI 도구 설명란" in bootcamp
    assert "누구 문제를 푸는 제안" in telegram
    assert "AI 도구 설명란" in telegram


def test_current_policy_ailit_landing_answer_keeps_all_required_terms() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    ailit = current_answers["landing-ailit-consult-home"]

    assert "Ailit" in ailit
    assert "상담" in ailit
    assert "일인 사업가" in ailit
    assert "진단" in ailit


def test_current_policy_ailit_business_answer_keeps_consulting_offer_and_success_metrics() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    ailit_business = current_answers["biz-ailit-youtube-conversion"]

    assert "Ailit 상담" in ailit_business
    assert "지표: 클릭률" in ailit_business
    assert "상담 신청" in ailit_business.split("지표: ", 1)[1]
    assert "전환율" in ailit_business.split("지표: ", 1)[1]


def test_current_policy_landing_weakest_answers_add_explicit_experiment_and_percent_metrics() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    for task_id in ["landing-ailit-consult-home", "landing-bootcamp-trial", "landing-telegram-join"]:
        answer = current_answers[task_id]
        experiment = answer.split("실험: ", 1)[1].split("\n", 1)[0]
        metric = answer.split("지표: ", 1)[1].split("\n", 1)[0]
        assert "실험" in experiment
        assert "%" in metric


def test_current_policy_retention_answers_add_first_day_second_day_and_easy_message_terms() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    for task_id in ["retention-vip-first-week", "retention-bootcamp-first-week"]:
        answer = current_answers[task_id]
        assert "첫날" in answer
        assert "둘째 날" in answer
        assert "고정 공지" in answer
        assert "알림" in answer
        assert "습관" in answer
        assert "쉬운" in answer
        assert "오늘" in answer
        assert "%" in answer


def test_current_policy_research_answers_add_price_band_three_points_and_check_step() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    for task_id in ["research-ailit-competitor-homepage", "research-bootcamp-free-paid-bridge", "research-youtube-description-benchmark"]:
        answer = current_answers[task_id]
        assert "가격 구간" in answer
        assert "세 가지" in answer
        assert "확인" in answer


def test_current_policy_bootcamp_retention_answer_adds_reaction_mission_onboarding_terms() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    answer = current_answers["retention-bootcamp-first-week"]
    assert "반응" in answer
    assert "미션" in answer
    assert "온보딩" in answer


def test_current_policy_bootcamp_business_answer_adds_beginner_friendly_phrase() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    bootcamp = current_answers["biz-bootcamp-paid-conversion"]

    assert "쉬운" in bootcamp
    assert "초보" in bootcamp or "간단" in bootcamp
    assert "바로" in bootcamp


def test_current_policy_ailit_and_vip_business_answers_add_easy_one_step_phrase() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    for task_id in ["biz-ailit-youtube-conversion", "biz-vip-first-week-onboarding"]:
        answer = current_answers[task_id]
        assert "쉬운" in answer
        assert "예시" in answer or "간단" in answer
        assert "한 가지" in answer
        assert "바로" in answer


def test_current_policy_x_answers_add_direct_question_and_direct_comment_prompt() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = {entry["task_id"]: entry["answer"] for entry in generate_lane_answers(benchmark, strong=False)}

    for task_id in ["x-ai-tools-sales-structure", "x-youtube-description-conversion"]:
        answer = current_answers[task_id]
        assert "무엇인지" in answer or "?" in answer
        assert "직접" in answer
        assert "댓글로" in answer


def test_current_policy_generator_pushes_landing_and_x_envs_over_nine_tenths() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = generate_lane_answers(benchmark, strong=False)
    current_summary = evaluate_answers(benchmark, current_answers)

    assert current_summary["env_summary"]["min_agentic_research"] >= 0.99
    assert current_summary["env_summary"]["min_business_strategy"] >= 0.965
    assert current_summary["env_summary"]["min_landing_cro"] >= 0.95
    assert current_summary["env_summary"]["min_membership_retention"] >= 0.999
    assert current_summary["env_summary"]["min_x_strategy"] >= 0.999


def test_generated_answers_fill_all_tasks() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    current_answers = generate_lane_answers(benchmark, strong=False)
    patched_answers = generate_lane_answers(benchmark, strong=True)

    benchmark_ids = [task["task_id"] for task in benchmark["tasks"]]
    assert [entry["task_id"] for entry in current_answers] == benchmark_ids
    assert [entry["task_id"] for entry in patched_answers] == benchmark_ids
    assert all(entry["answer"].strip() for entry in current_answers)
    assert all(entry["answer"].strip() for entry in patched_answers)
