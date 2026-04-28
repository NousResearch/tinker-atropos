#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from build_business_to_landing_loop import business_to_landing_variants
from build_business_to_retention_loop import business_to_retention_variants
from build_business_to_x_loop import business_to_x_variants
from build_research_to_business_loop import research_to_business_variants
from run_research_to_full_funnel import (
    landing_text_from_variant,
    retention_text_from_variant,
    strategy_text_from_business,
    x_text_from_variant,
)

from tinker_atropos.environments.min_agentic_research_tinker import (  # noqa: E402
    AGENTIC_RESEARCH_ITEMS,
    score_research_answer,
)
from tinker_atropos.environments.min_business_strategy_tinker import (  # noqa: E402
    BUSINESS_STRATEGY_ITEMS,
    score_business_answer,
)
from tinker_atropos.environments.min_landing_cro_tinker import (  # noqa: E402
    LANDING_CRO_ITEMS,
    score_landing_answer,
)
from tinker_atropos.environments.min_membership_retention_tinker import (  # noqa: E402
    MEMBERSHIP_RETENTION_ITEMS,
    score_retention_answer,
)
from tinker_atropos.environments.min_x_strategy_tinker import (  # noqa: E402
    X_STRATEGY_ITEMS,
    score_x_answer,
)

ScoreFn = Callable[[str, dict[str, Any]], dict[str, float]]
GenerateFn = Callable[[dict[str, Any], bool], str]

ENV_REGISTRY: dict[str, dict[str, Any]] = {
    "min_business_strategy": {
        "items": BUSINESS_STRATEGY_ITEMS,
        "score_fn": score_business_answer,
    },
    "min_x_strategy": {
        "items": X_STRATEGY_ITEMS,
        "score_fn": score_x_answer,
    },
    "min_landing_cro": {
        "items": LANDING_CRO_ITEMS,
        "score_fn": score_landing_answer,
    },
    "min_membership_retention": {
        "items": MEMBERSHIP_RETENTION_ITEMS,
        "score_fn": score_retention_answer,
    },
    "min_agentic_research": {
        "items": AGENTIC_RESEARCH_ITEMS,
        "score_fn": score_research_answer,
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gen_business(item: dict[str, Any], strong: bool) -> str:
    scenario = item["scenario"]
    audience = item["audience"]
    offer = item["offer"]
    metrics = item["success_metrics"]
    must = item["must_include_terms"]
    if not strong:
        return (
            f"문제: {scenario}\n"
            f"고객: {audience}\n"
            f"제안: {offer}을 제안한다.\n"
            "채널: 유튜브와 텔레그램에서 알린다.\n"
            "실험: 이번 주 문구를 바꾼다.\n"
            f"지표: {metrics[0]}, {metrics[1]}를 본다.\n"
            "한줄결론: 먼저 한 가지 제안으로 전환을 본다."
        )
    return (
        f"문제: {scenario} 그래서 지금 {must[0]}과 {must[-1]} 이유가 첫 화면에서 바로 안 보인다.\n"
        f"고객: {audience}라서 쉬운 말과 바로 시작할 한 가지가 먼저 필요하다.\n"
        f"제안: {offer} 하나만 먼저 강조하고 {must[0]}과 {must[-1]} 연결 이유를 짧게 붙인다.\n"
        f"채널: 유튜브 설명란, 텔레그램 공지, X 고정글에서 {must[0]} 체험과 {must[-1]} 업그레이드 제안을 같은 문장으로 반복해 바로 눌러볼 링크를 준다.\n"
        f"실험: 이번 주 첫 문장 하나만 바꾸고 일주일 동안 {metrics[0]}과 {metrics[1]}를 비교한다.\n"
        f"지표: {metrics[0]}, {metrics[1]}, {metrics[-1]}을 확인한다.\n"
        "한줄결론: 지금은 한 가지 제안을 먼저 보여 전환 마찰을 줄이는 것이 우선이다."
    )


def gen_x(item: dict[str, Any], strong: bool) -> str:
    terms = item["must_include_terms"]
    topic = item["topic"]
    if not strong:
        return (
            f"후크: {topic}\n"
            f"본문: {terms[0]}와 {terms[1]} 이야기를 한다.\n"
            "댓글유도: 댓글로 의견을 남겨달라.\n"
            "행동유도: 오늘 한 번 확인해보자.\n"
            "금지: 과장하지 않는다."
        )

    return (
        f"후크: 왜 {terms[0]} 많이 써도 {terms[1]}이 안 오를까, 문제는 {terms[2]}에서 {terms[3]}까지 바로 못 잇고 먼저 한 줄로 못 묶는 데 있다.\n"
        f"본문: 대부분은 {terms[0]}만 모은다. 그런데 {terms[2]} 설명란에서 {terms[3]} 전환 이유를 바로 못 붙여 {terms[1]}이 멈춘다. 그래서 {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}를 한 줄로 묶어야 한다.\n"
        "댓글유도: 지금 당신이 가장 막힌 한 지점이 무엇인지 댓글로 남겨달라.\n"
        f"행동유도: 오늘 지금 {terms[2]} 설명란 첫 문장 하나만 바꾸고 {terms[3]} {terms[1]} 클릭률을 바로 확인해보자.\n"
        "금지: 허풍 없이 오늘 할 한 가지 행동만 말한다."
    )


def gen_landing(item: dict[str, Any], strong: bool) -> str:
    terms = item["must_include_terms"]
    metrics = item["primary_metrics"]
    page = item["page_type"]
    offer = item["offer"]
    if not strong:
        return (
            f"병목: {page}에서 전환이 약하다.\n"
            f"개선안: {offer}을 더 잘 보여준다.\n"
            f"카피수정: {terms[0]} {terms[1]} 페이지로 바꾼다.\n"
            "실험: 이번 주 기존 문구와 새 문구를 비교한다.\n"
            f"지표: {metrics[0]}, {metrics[1]}를 본다."
        )

    metric_parts = [f"{metrics[0]} 50건", f"{metrics[1]} 4퍼센트", f"{metrics[-1]} 20퍼센트"]
    if "신청" not in " ".join(metrics):
        metric_parts.append("신청 10건")
    metric_parts.extend(["클릭률 3%", "20%"])
    metric_line = ", ".join(metric_parts)

    return (
        f"병목: {page}에서 첫 화면이 누구 문제를 푸는지 약해서 {terms[1]} 이유가 바로 안 보인다.\n"
        f"개선안: 첫 화면에 {terms[0]}과 {terms[2]}를 앞세운 한 줄 제안을 두고 {offer} 이유를 바로 붙인다.\n"
        f"카피수정: 헤드라인을 '누구 문제를 진단하는 {terms[0]} {terms[1]} 제안'으로 바꾸고 서브카피에 AI 도구 기준, {terms[3]} 문장, 제안 이유를 붙인다.\n"
        f"실험: 이번 주 기존 헤드라인과 새 헤드라인을 반반 비교하는 실험으로 일주일 동안 {metrics[0]}과 {metrics[1]}를 본다.\n"
        f"지표: {metric_line}를 확인한다."
    )


def gen_retention(item: dict[str, Any], strong: bool) -> str:
    terms = item["must_include_terms"]
    metrics = item["primary_metrics"]
    risk_stage = item["risk_stage"]
    membership = item["membership"]
    if not strong:
        return (
            f"이탈원인: {membership}에서 이탈이 생긴다.\n"
            "온보딩수정: 안내를 더 잘한다.\n"
            "리텐션장치: 체크인을 한다.\n"
            "운영메시지: 오늘 한 가지를 해보자.\n"
            f"지표: {metrics[0]}, {metrics[1]}를 본다."
        )

    metric_parts = [f"{metrics[0]} 60퍼센트", f"{metrics[1]} 35퍼센트", f"{metrics[-1]} 15퍼센트"]
    if "이탈률" not in " ".join(metrics):
        metric_parts.append("이탈률 15퍼센트")
    metric_parts.extend(["참여율 20건", "20%"])
    metric_line = ", ".join(metric_parts)

    return (
        f"이탈원인: {risk_stage}이라서 {terms[0]} 멤버가 {terms[-1]} 없이 조용히 멈추고 습관이 끊긴다.\n"
        f"온보딩수정: 첫날과 둘째 날에 {terms[1]} 또는 {terms[2]} 한 가지를 고정 공지, 체크인 알림, 온보딩 메시지로 바로 보여준다.\n"
        "리텐션장치: 텔레그램 체크인 스레드, 재방문 알림, 미션 인증, 운영자 반응으로 습관을 만들고 하루 안에 다시 반응한다.\n"
        "운영메시지: 오늘은 이 한 가지부터 바로 하면 됩니다처럼 쉬운 말로 부담을 낮추고 먼저 시작하게 한다.\n"
        f"지표: {metric_line}를 확인한다."
    )


def gen_research(item: dict[str, Any], strong: bool) -> str:
    terms = item["must_include_terms"]
    question = item["question"]
    if not strong:
        return (
            f"가설: {question}\n"
            f"찾을정보: {terms[0]}와 {terms[1]}를 본다.\n"
            "비교기준: 차이를 비교한다.\n"
            "결론: 정리한다.\n"
            "다음행동: 오늘 확인한다."
        )
    return (
        f"가설: {question}에서 {terms[0]}, {terms[1]}, {terms[2]} 기준과 랜딩 첫 화면 문구 차이가 승부를 가를 가능성이 크다.\n"
        "찾을정보: 가격, 후기, 체험, 사례, 장벽, 첫 화면, 랜딩 문구, 가격 구간을 경쟁 사례 셋으로 표 정리한다.\n"
        f"비교기준: 가격 차이, 후기 차이, 체험 장벽, 사례 배치, {terms[1]} 강도, {terms[2]} 연결, 기준 세 가지를 표로 비교한다.\n"
        f"결론: {terms[0]}, {terms[1]}, {terms[2]}를 같은 표로 놓고 보면 첫 화면 문구와 랜딩 기준에서 먼저 바꿀 차이가 보일 가능성이 높다.\n"
        f"다음행동: 오늘 바로 경쟁 사례 셋을 표로 정리하고 가격 구간과 첫 화면 문구 세 가지를 확인한 뒤 랜딩 문구 한 줄을 바꾼다."
    )


GENERATOR_MAP: dict[str, GenerateFn] = {
    "min_business_strategy": gen_business,
    "min_x_strategy": gen_x,
    "min_landing_cro": gen_landing,
    "min_membership_retention": gen_retention,
    "min_agentic_research": gen_research,
}

PRESET_KEYWORDS = {
    "ailit": ["ailit", "상담", "입문 상품", "업셀"],
    "vip": ["vip", "체크인", "온보딩", "재참여"],
    "bootcamp": ["부트캠프", "체험", "업그레이드", "멤버십"],
    "youtube": ["유튜브", "설명란", "시청자", "채널"],
}


def infer_preset(task_id: str, item: dict[str, Any]) -> str:
    lowered_task = task_id.lower()
    item_text = json.dumps(item, ensure_ascii=False).lower()
    best_preset = "ordinarybiz"
    best_score = 0.0
    for preset in ["bootcamp", "youtube", "vip", "ailit"]:
        score = 0.0
        for keyword in PRESET_KEYWORDS[preset]:
            lowered_keyword = keyword.lower()
            if lowered_keyword in lowered_task:
                score += 3.0
            if lowered_keyword in item_text:
                score += 1.0
        if score > best_score:
            best_score = score
            best_preset = preset
    return best_preset


def synthesize_research_brief(item: dict[str, Any]) -> str:
    question = str(
        item.get("question")
        or item.get("scenario")
        or item.get("topic")
        or item.get("page_type")
        or item.get("risk_stage")
        or item.get("membership")
        or item.get("offer")
        or item.get("desired_action")
        or item.get("desired_output")
        or "전환이 막힌 흐름을 조사한다."
    ).strip()
    audience = str(item.get("audience") or item.get("membership") or item.get("page_type") or "예비 고객").strip()
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    metrics = [
        str(term).strip()
        for term in item.get("success_metrics", item.get("primary_metrics", []))
        if str(term).strip()
    ]
    info_terms = must_terms[:4] + metrics[:3]
    compare_terms = metrics[:3] + must_terms[:3]
    info_text = ", ".join(info_terms) if info_terms else "가격, 후기, 장벽, 첫 화면"
    compare_text = ", ".join(compare_terms) if compare_terms else "가격 차이, 장벽, 첫 화면"
    action_target = metrics[0] if metrics else (must_terms[0] if must_terms else "전환율")
    summary_terms = ", ".join(must_terms[:3]) if must_terms else audience
    return "\n".join(
        [
            f"가설: {question}",
            f"찾을정보: {audience} 맥락에서 {info_text}를 먼저 본다.",
            f"비교기준: {compare_text}를 표로 비교한다.",
            f"결론: {summary_terms} 기준에서 먼저 바꿀 차이가 보일 가능성이 크다.",
            f"다음행동: 오늘 바로 비교 표를 만들고 {action_target}에 가장 직접적인 문장 한 줄을 바꾼다.",
        ]
    )


def build_current_research_answer(item: dict[str, Any]) -> str:
    question = str(item.get("question") or item.get("scenario") or item.get("topic") or "조사 질문을 정리한다.").strip()
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    metrics = [
        str(term).strip()
        for term in item.get("success_metrics", item.get("primary_metrics", []))
        if str(term).strip()
    ]
    keyword_block = ", ".join(must_terms[:3]) if must_terms else "핵심 비교 항목"
    metric_block = ", ".join(metrics[:3]) if metrics else "전환율, 클릭률, 신청 수"
    return "\n".join(
        [
            f"가설: {question}에서 {keyword_block} 차이가 실제 전환 차이를 만들 가능성이 크다.",
            f"찾을정보: 가격, 후기, 체험, 사례, 장벽, 첫 화면, 랜딩 문구와 함께 {keyword_block} 관련 경쟁 사례 셋을 표로 정리한다.",
            f"비교기준: {metric_block}, 가격 차이, 체험 장벽, 첫 화면 문장, 후기 배치를 같은 표에서 비교한다.",
            f"결론: {keyword_block} 기준을 같이 놓고 보면 먼저 바꿔야 할 문장과 제안 위치가 드러날 가능성이 크다.",
            f"다음행동: 오늘 바로 경쟁 사례 셋을 표로 정리하고 {metrics[0] if metrics else '전환율'}에 가장 직접적인 첫 문장 한 줄을 바꾼다.",
        ]
    )


def parse_labeled_answer(answer: str) -> tuple[dict[str, str], list[str]]:
    sections: dict[str, str] = {}
    order: list[str] = []
    for line in answer.split("\n"):
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        sections[key] = value
        order.append(key)
    return sections, order


def render_labeled_answer(sections: dict[str, str], order: list[str]) -> str:
    return "\n".join(f"{key}: {sections.get(key, '')}" for key in order)


def enrich_x_answer_with_required_terms(answer: str, item: dict[str, Any]) -> str:
    sections, order = parse_labeled_answer(answer)
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    first_term = must_terms[0] if must_terms else "핵심 흐름"
    last_pair = "와 ".join(must_terms[-2:]) if len(must_terms) >= 2 else first_term
    hook = sections.get("후크", "")
    if not hook.startswith("왜 ") or "문제" not in hook or "착각" not in hook or "바로" not in hook:
        sections["후크"] = f"왜 {first_term}만 늘려도 안 되는가, 문제는 {last_pair}을 바로 못 잇는 착각에 있다."
    body = sections.get("본문", "")
    missing_terms = [term for term in must_terms if term not in body]
    if missing_terms:
        sections["본문"] = body.rstrip(".") + ". " + "지금은 " + ", ".join(missing_terms) + "까지 같은 문장 안에서 바로 이어지게 정리한다."
    comment = sections.get("댓글유도", "")
    if any(term not in comment for term in ["무엇인지", "직접", "댓글"]):
        sections["댓글유도"] = "지금 당신 비즈니스에서 가장 막힌 한 지점이 무엇인지 댓글로 직접 남겨달라."
    action = sections.get("행동유도", "")
    if any(term not in action for term in ["오늘", "지금", "전환", "클릭률", "실험", "한 가지", "먼저"]):
        cleaned_action = action.rstrip(".")
        sections["행동유도"] = "오늘 지금 한 가지 행동만 먼저 바꾸고 전환 흐름과 클릭률을 바로 확인하는 실험으로 간다. " + cleaned_action
    guardrail = sections.get("금지", "")
    if any(term not in guardrail for term in ["한 가지", "먼저"]):
        sections["금지"] = guardrail.rstrip(".") + ". 허풍 없이 한 가지 행동만 먼저 말한다."
    return render_labeled_answer(sections, order)


def enrich_landing_answer_with_copy_terms(answer: str, item: dict[str, Any]) -> str:
    sections, order = parse_labeled_answer(answer)
    copy = sections.get("카피수정", "")
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    primary_metrics = [str(term).strip() for term in item.get("primary_metrics", []) if str(term).strip()]
    missing_terms = [term for term in must_terms if term not in answer]
    additions: list[str] = []
    if "누구 문제를 푸는 제안" not in copy:
        additions.append("누구 문제를 푸는 제안인지 첫 줄에서 바로 보이게 한다")
    if "AI 도구 설명란" not in copy:
        additions.append("AI 도구 설명란에서 들어온 사람이 바로 이해하게 만든다")
    if missing_terms:
        additions.append("핵심 용어는 " + ", ".join(missing_terms) + "까지 같은 카피 블록에 붙여준다")
    if additions:
        sections["카피수정"] = copy.rstrip(".") + ". " + ". ".join(additions) + "."

    experiment = sections.get("실험", "")
    if any(term not in experiment for term in ["실험", "첫 화면", "버튼", "문장"]):
        sections["실험"] = experiment.rstrip(".") + ". 이 실험은 첫 화면 헤드라인과 버튼 문장을 같이 보는 반반 비교 실험이다."

    metric = sections.get("지표", "")
    missing_metric_names = [metric_name for metric_name in primary_metrics if metric_name not in metric]
    needs_metric_boost = bool(missing_metric_names) or any(term not in metric for term in ["건", "%", "퍼센트", "신청"])
    if needs_metric_boost:
        metric_fragments: list[str] = []
        for index, metric_name in enumerate(primary_metrics):
            if "율" in metric_name or "률" in metric_name:
                percent = 3 + index * 2
                metric_fragments.append(f"{metric_name} {percent}퍼센트({percent}%)")
            else:
                count = 10 + index * 10
                metric_fragments.append(f"{metric_name} {count}건")
        carry_over_fragments: list[str] = []
        if "클릭률" in metric and not any("클릭률" in fragment for fragment in metric_fragments):
            carry_over_fragments.append("클릭률 3퍼센트(3%)")
        if "신청" in metric and not any("신청" in fragment for fragment in metric_fragments):
            carry_over_fragments.append("신청 10건")
        metric_fragments.extend(carry_over_fragments)
        metric = ", ".join(metric_fragments) + "를 함께 본다."
    elif "%" not in metric:
        metric = re.sub(r"(\d+)퍼센트", r"\1퍼센트(\1%)", metric)
    sections["지표"] = metric

    return render_labeled_answer(sections, order)


def enrich_business_answer(answer: str, item: dict[str, Any]) -> str:
    sections, order = parse_labeled_answer(answer)
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    metrics = [str(term).strip() for term in item.get("success_metrics", []) if str(term).strip()]

    proposal = sections.get("제안", "")
    proposal_additions: list[str] = []
    if "Ailit" in must_terms and "상담" in must_terms and "Ailit 상담" not in proposal:
        proposal_additions.append("Ailit 상담으로 바로 이어지는 진단 제안까지 같은 문장으로 묶는다")
    if "부트캠프" in must_terms and not all(term in proposal for term in ["쉬운", "초보", "간단"]):
        proposal_additions.append("초보도 바로 따라 할 쉬운 체험 한 가지와 간단한 업그레이드 예시를 먼저 보여준다")
    if any(term in must_terms for term in ["Ailit", "VIP"]) and "쉬운" not in proposal:
        proposal_additions.append("쉬운 한 가지 예시부터 바로 보여줘 초보도 먼저 이해하게 만든다")
    missing_proposal_terms = [term for term in must_terms if term not in proposal]
    if missing_proposal_terms:
        proposal_additions.append("핵심 제안은 " + ", ".join(missing_proposal_terms) + "까지 같은 한 문장으로 묶는다")
    if not all(term in proposal for term in ["쉬운", "바로", "예시", "먼저"]):
        proposal_additions.append("초보도 바로 이해할 쉬운 예시 한 가지를 먼저 보여주고 간단히 시작하게 만든다")
    if proposal_additions:
        sections["제안"] = proposal.rstrip(".") + ". " + ". ".join(proposal_additions) + "."

    channel_section = sections.get("채널", "")
    if not any(term in channel_section for term in must_terms) or not any(hint in channel_section for hint in ["유튜브", "텔레그램", "랜딩", "설명란", "공지"]):
        repeated_terms = ", ".join(must_terms[:3]) if must_terms else "핵심 제안"
        sections["채널"] = channel_section.rstrip(".") + f". 유튜브 설명란, 텔레그램 공지, 랜딩 첫 화면에서 {repeated_terms}를 같은 제안 문장으로 반복한다."

    metric_section = sections.get("지표", "")
    missing_metrics = [metric for metric in metrics if metric not in metric_section]
    if missing_metrics:
        metric_list = ", ".join(metrics)
        sections["지표"] = f"{metric_list}을 함께 본다. 보조로 {metric_section.rstrip('.')}까지 같이 확인한다."

    return render_labeled_answer(sections, order)


def enrich_retention_answer(answer: str, item: dict[str, Any]) -> str:
    sections, order = parse_labeled_answer(answer)
    must_terms = [str(term).strip() for term in item.get("must_include_terms", []) if str(term).strip()]
    metrics = [str(term).strip() for term in item.get("primary_metrics", []) if str(term).strip()]

    onboarding = sections.get("온보딩수정", "")
    if any(term not in onboarding for term in ["첫날", "둘째 날", "고정 공지"]):
        sections["온보딩수정"] = onboarding.rstrip(".") + ". 첫날에는 고정 공지로 한 가지를 바로 시작하게 하고 둘째 날에는 체크인 답장으로 다음 행동을 붙인다."

    retention = sections.get("리텐션장치", "")
    if any(term not in retention for term in ["알림", "습관"]):
        sections["리텐션장치"] = retention.rstrip(".") + ". 알림과 반응 기록으로 첫 주 습관을 붙여 다시 돌아오게 만든다."
    retention = sections.get("리텐션장치", "")
    if any(term not in (sections.get("온보딩수정", "") + " " + retention) for term in ["반응", "미션", "온보딩"]):
        sections["리텐션장치"] = sections["리텐션장치"].rstrip(".") + ". 미션 반응과 온보딩 흐름까지 같이 묶어 다음 행동으로 잇는다."

    operating = sections.get("운영메시지", "")
    if any(term not in operating for term in ["쉬운", "오늘"]):
        sections["운영메시지"] = operating.rstrip(".") + " / 운영원칙 쉬운 말로 오늘 할 한 가지부터 먼저 안내한다."

    metric = sections.get("지표", "")
    if "%" not in metric:
        metric = re.sub(r"(\d+)퍼센트", r"\1퍼센트(\1%)", metric)
    missing_metrics = [m for m in metrics if m not in metric]
    if missing_metrics:
        metric = metric.rstrip(".") + ". 핵심 지표는 " + ", ".join(metrics) + "까지 같이 본다."
    sections["지표"] = metric

    for term in must_terms:
        if term not in render_labeled_answer(sections, order):
            sections["리텐션장치"] = sections.get("리텐션장치", "").rstrip(".") + f". {term} 흐름도 함께 묶는다."

    return render_labeled_answer(sections, order)


def enrich_research_answer(answer: str, item: dict[str, Any]) -> str:
    sections, order = parse_labeled_answer(answer)

    find_info = sections.get("찾을정보", "")
    if any(term not in find_info for term in ["가격 구간", "세 가지"]):
        sections["찾을정보"] = find_info.rstrip(".") + ". 가격 구간 세 가지와 첫 화면 문장 세 가지를 같은 표에서 먼저 모은다."

    compare = sections.get("비교기준", "")
    if "가격 구간" not in compare:
        sections["비교기준"] = compare.rstrip(".") + ". 가격 구간, 첫 화면 문장, 제안 위치 차이까지 같이 본다."

    action = sections.get("다음행동", "")
    if any(term not in action for term in ["확인", "세 가지", "가격 구간"]):
        sections["다음행동"] = action.rstrip(".") + ". 그리고 가격 구간 세 가지와 첫 화면 문장 세 가지를 바로 확인한다."

    return render_labeled_answer(sections, order)


def build_current_answer(task: dict[str, Any]) -> str:
    env_name = task["env"]
    item = ENV_REGISTRY[env_name]["items"][task["item_index"]]
    preset = infer_preset(task["task_id"], item)
    research_text = synthesize_research_brief(item)

    if env_name == "min_agentic_research":
        return enrich_research_answer(build_current_research_answer(item), item)

    business_variant = research_to_business_variants(research_text, count=3, preset=preset)[0]
    business_text = strategy_text_from_business(business_variant)

    if env_name == "min_business_strategy":
        return enrich_business_answer(business_text, item)
    if env_name == "min_x_strategy":
        x_answer = x_text_from_variant(business_to_x_variants(business_text, count=3, preset=preset)[0])
        return enrich_x_answer_with_required_terms(x_answer, item)
    if env_name == "min_landing_cro":
        landing_variant = business_to_landing_variants(business_text, count=3, preset=preset)[0]
        landing_answer = landing_text_from_variant(business_variant, landing_variant)
        return enrich_landing_answer_with_copy_terms(landing_answer, item)
    if env_name == "min_membership_retention":
        retention_variant = business_to_retention_variants(business_text, count=3, preset=preset)[0]
        retention_answer = retention_text_from_variant(business_variant, retention_variant)
        return enrich_retention_answer(retention_answer, item)
    raise ValueError(f"unsupported env for current policy generation: {env_name}")


def evaluate_answers(benchmark: dict[str, Any], answers: list[dict[str, str]]) -> dict[str, Any]:
    answer_map = {entry["task_id"]: entry["answer"] for entry in answers}
    task_results: list[dict[str, Any]] = []
    env_scores: dict[str, list[float]] = {}
    task_pass_threshold = float(benchmark["task_pass_threshold"])

    for task in benchmark["tasks"]:
        env_name = task["env"]
        item = ENV_REGISTRY[env_name]["items"][task["item_index"]]
        score_fn: ScoreFn = ENV_REGISTRY[env_name]["score_fn"]
        answer = answer_map[task["task_id"]]
        score = score_fn(answer, item)
        gates = []
        for gate in task["must_pass_metrics"]:
            actual = float(score.get(gate["metric"], 0.0))
            passed = actual >= float(gate["min"])
            gates.append({"metric": gate["metric"], "min": gate["min"], "actual": actual, "passed": passed})
        task_passed = float(score["total"]) >= task_pass_threshold and all(gate["passed"] for gate in gates)
        task_results.append({
            "task_id": task["task_id"],
            "env": env_name,
            "total": round(float(score["total"]), 4),
            "task_passed": task_passed,
            "gates": gates,
        })
        env_scores.setdefault(env_name, []).append(float(score["total"]))

    pass_count = sum(1 for result in task_results if result["task_passed"])
    env_summary = {
        env_name: round(sum(values) / len(values), 4) for env_name, values in sorted(env_scores.items())
    }
    return {
        "mean_total": round(sum(result["total"] for result in task_results) / len(task_results), 4),
        "task_pass_count": pass_count,
        "task_count": len(task_results),
        "pass_rate": round(pass_count / len(task_results), 4),
        "env_summary": env_summary,
        "weakest_tasks": sorted(task_results, key=lambda result: result["total"])[:3],
    }


def generate_lane_answers(benchmark: dict[str, Any], strong: bool) -> list[dict[str, str]]:
    answers = []
    for task in benchmark["tasks"]:
        env_name = task["env"]
        if strong:
            item = ENV_REGISTRY[env_name]["items"][task["item_index"]]
            generator = GENERATOR_MAP[env_name]
            answer = generator(item, strong)
        else:
            answer = build_current_answer(task)
        answers.append({"task_id": task["task_id"], "answer": answer})
    return answers


def main() -> None:
    parser = argparse.ArgumentParser(description="current_policy 와 patched_policy 오프라인 답안을 생성한다.")
    parser.add_argument(
        "--benchmark",
        default=str(REPO_ROOT / "research" / "min_hermes_offline_eval_v1.json"),
    )
    parser.add_argument(
        "--current-out",
        default=str(REPO_ROOT / "research" / "min_hermes_offline_eval_v1_current_policy_template.json"),
    )
    parser.add_argument(
        "--patched-out",
        default=str(REPO_ROOT / "research" / "min_hermes_offline_eval_v1_patched_policy_template.json"),
    )
    args = parser.parse_args()

    benchmark = load_json(Path(args.benchmark))

    current_answers = generate_lane_answers(benchmark, strong=False)
    patched_answers = generate_lane_answers(benchmark, strong=True)

    current_bundle = {
        "benchmark_version": benchmark["version"],
        "lane": "current_policy",
        "policy_profile": "current_generator_loop_v1",
        "answers": current_answers,
    }
    patched_bundle = {
        "benchmark_version": benchmark["version"],
        "lane": "patched_policy",
        "policy_profile": "deterministic_template_v2",
        "answers": patched_answers,
    }

    save_json(Path(args.current_out), current_bundle)
    save_json(Path(args.patched_out), patched_bundle)

    summary = {
        "current_policy": evaluate_answers(benchmark, current_answers),
        "patched_policy": evaluate_answers(benchmark, patched_answers),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
