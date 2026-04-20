import argparse
import json
import re
from datetime import datetime
from pathlib import Path

SECTION_NAMES = ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]

HEADLINE_PATTERNS = [
    "{customer_label}를 위한 {offer_label}",
    "신뢰 근거를 먼저 보여주는 {offer_label}",
    "{customer_label}가 바로 이해하는 {offer_label}",
]

SECONDARY_HEADLINE_PATTERNS = [
    "신뢰를 먼저 확인하고 시작하는 {offer_label}",
    "지금 안심하고 시작하는 {offer_label}",
    "망설임을 줄이는 {offer_label}",
]

TERTIARY_HEADLINE_PATTERNS = [
    "지금 바로 비교하고 신청하는 {offer_label}",
    "먼저 확인하고 결정하는 {offer_label}",
    "지금 비교가 쉬워지는 {offer_label}",
]

SUBCOPY_PATTERNS = [
    "신뢰를 먼저 보여주기 위해 {offer_label}를 앞세운다.",
    "{offer_label} 하나로 {customer_label}가 신청 이유를 빠르게 납득하게 만든다.",
    "{offer_label}를 먼저 보여줘 {customer_label}가 바로 비교와 신청 흐름을 짧게 만든다.",
]

CTA_PATTERNS = [
    "지금 진단 신청하기",
    "지금 핵심 제안 보기",
    "오늘 바로 시작하기",
]

SECONDARY_CTA_PATTERNS = [
    "지금 혜택 먼저 확인하기",
    "부담 없이 시작하기",
    "지금 한 번 점검하기",
]

TERTIARY_CTA_PATTERNS = [
    "부담 없이 신청하기",
    "지금 바로 신청하기",
    "지금 가볍게 바꿔보기",
]

BULLET_PATTERNS = [
    "문제 인식: {problem_label}",
    "제안 초점: {offer_label}",
    "바로 행동: {experiment}",
]

HEADLINE_TERMS = ["위한", "줄이는", "바로", "이해", "진단", "신청"]
CTA_TERMS = ["지금", "오늘", "바로", "신청", "시작"]
RISK_RELIEF_TERMS = ["부담 없이", "먼저 확인", "가볍게", "안심", "점검"]
CONSULTING_TERMS = ["상담", "진단", "신청", "문의"]
BEGINNER_TERMS = ["쉬운", "바로", "한 가지", "먼저", "핵심", "이해"]
HYPE_TERMS = ["혁신", "최고", "압도", "무조건", "대박"]


def parse_sections(text: str, section_names: list[str]) -> dict[str, str]:
    pattern = re.compile(rf"^({'|'.join(map(re.escape, section_names))})\s*:\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = (match.group(2) + " " + text[start:end]).strip()
        sections[name] = re.sub(r"\s+", " ", body)
    return sections


def _trim_sentence(text: str) -> str:
    return text.strip().removesuffix(".")


def _extract_customer_label(customer: str) -> str:
    for candidate in ["유튜브 시청자", "VIP 신규 유료 멤버", "VIP 멤버", "예비 고객", "잠재 고객", "일인 사업가", "사업가", "창업자", "운영자", "고객"]:
        if candidate in customer:
            return candidate
    return _trim_sentence(customer)


def _extract_offer_label(offer: str) -> str:
    match = re.search(r"([A-Za-z0-9 ]*진단 세션|[A-Za-z0-9 ]*입문 상품|[A-Za-z0-9 ]*패키지|[A-Za-z0-9 ]*세팅 세션)", offer)
    if match:
        return match.group(1).strip()
    if "VIP" in offer and "온보딩" in offer and "체크인" in offer:
        return "VIP 온보딩 체크인 제안"
    if "설명란" in offer and ("상담 CTA" in offer or "상담" in offer):
        return "설명란 상담 CTA 제안"
    if "부트캠프" in offer and "체험" in offer:
        return "부트캠프 체험 제안"
    if "텔레그램" in offer and "체크리스트" in offer:
        return "텔레그램 합류 제안"
    if "신뢰 근거" in offer:
        return "신뢰 근거 제안"
    return offer.split(" 하나만")[0].split(" 하나를")[0].strip().removesuffix(".")


def _extract_problem_label(problem: str) -> str:
    if "상담 신청 이유" in problem:
        return "상담 신청 이유 약한 문제"
    if "입문 장벽" in problem and "신뢰" in problem:
        return "신뢰 근거가 약한 문제"
    if "신뢰 근거" in problem and "약" in problem:
        return "신뢰 근거가 약한 문제"
    trimmed = _trim_sentence(problem)
    first_sentence = trimmed.split('. ')[0]
    return first_sentence


def postprocess_korean_copy(text: str) -> str:
    replacements = {
        "약함를": "약한 문제를",
        "약함을": "약한 문제를",
        "세션를": "세션을",
        "세션와": "세션과",
        "세션를 앞세워": "세션을 앞세워",
        "세션를 줄이는": "세션을 줄이는",
        "고객가": "고객이",
        "고객를": "고객을",
        "예비 고객가": "예비 고객이",
        "예비 고객를": "예비 고객을",
        "잠재 고객가": "잠재 고객이",
        "잠재 고객를": "잠재 고객을",
        "사업가가가": "사업가가",
        "제안를": "제안을",
    }
    fixed = text
    for old, new in replacements.items():
        fixed = fixed.replace(old, new)
    fixed = re.sub(r"\s+", " ", fixed).strip()
    return fixed


def normalize_strategy_fields(sections: dict[str, str]) -> dict[str, str]:
    problem = sections.get("문제", "문제가 아직 선명하지 않다")
    customer = sections.get("고객", "고객이 아직 정리되지 않았다")
    offer = sections.get("제안", "제안이 아직 정리되지 않았다")
    channel = sections.get("채널", "채널이 아직 정리되지 않았다")
    experiment = sections.get("실험", "오늘 바꿔볼 한 가지를 아직 정하지 못했다")
    metrics = sections.get("지표", "핵심 지표가 아직 정리되지 않았다")
    summary = sections.get("한줄결론", offer).removeprefix("지금은 ").strip()
    experiment = experiment.removeprefix("오늘은 ").removeprefix("오늘 ").strip()
    context_text = " ".join([problem, customer, offer, channel, summary])
    if "텔레그램" in context_text and "체크리스트" in context_text:
        context = "telegram_join"
    elif "부트캠프" in context_text and "체험" in context_text:
        context = "bootcamp_trial"
    elif "Ailit" in context_text:
        context = "ailit"
    else:
        context = "generic"
    return {
        "problem": problem,
        "customer": customer,
        "offer": offer,
        "channel": channel,
        "experiment": experiment,
        "metrics": metrics,
        "summary": summary,
        "customer_label": _extract_customer_label(customer),
        "offer_label": _extract_offer_label(offer),
        "problem_label": _extract_problem_label(problem),
        "context": context,
    }


def build_compare_experiment(experiment: str, metric_text: str, subject: str) -> str:
    experiment = experiment.strip().removesuffix(".")
    if any(term in experiment for term in ["반반", "비교", "기존", "새", "이번 주"]):
        return experiment + ("." if not experiment.endswith(".") else "")
    metric_focus = metric_text.split(",")[0].strip().rstrip(".")
    return f"이번 주 기존 {subject}과 새 {subject}을 반반 비교해 일주일 동안 {metric_focus}을 본다."


def build_context_landing_variant(fields: dict[str, str], idx: int) -> dict[str, str] | None:
    experiment = build_compare_experiment(fields["experiment"], fields["metrics"], "헤드라인")
    if fields["context"] == "bootcamp_trial":
        variants = [
            {
                "헤드라인": "무료만 보고 멈춘 문제를 바로 줄이는 부트캠프 체험 제안",
                "서브카피": "유튜브 설명란을 본 예비 고객에게 체험 과제 한 가지와 업그레이드 이유를 첫 화면에서 함께 보여줘 바로 신청 이유를 납득하게 만든다.",
                "핵심불릿": "문제 인식: 무료만 보고 멈춘 문제 | 제안 초점: 부트캠프 체험 제안 | 바로 행동: 설명란 뒤 체험 과제 한 가지와 업그레이드 이유를 같이 본다.",
                "CTA": "지금 체험 신청하기",
            },
            {
                "헤드라인": "체험 과제부터 바로 보여주는 부트캠프 신청 제안",
                "서브카피": "유튜브 설명란 뒤에 무엇을 해볼지 한 문장으로 보여줘 체험 신청과 업그레이드 이유를 함께 이해하게 만든다.",
                "핵심불릿": "문제 인식: 신청 이유가 약한 문제 | 제안 초점: 체험 과제와 업그레이드 제안 | 바로 행동: 설명란 뒤 첫 화면에서 체험 한 가지를 먼저 본다.",
                "CTA": "체험 과제 먼저 보기",
            },
            {
                "헤드라인": "업그레이드 전 한 번 해보게 만드는 부트캠프 체험 제안",
                "서브카피": "예비 고객이 부담 없이 체험을 눌러보고 설명란 뒤 업그레이드 이유까지 바로 비교하게 만드는 첫 화면으로 바꾼다.",
                "핵심불릿": "문제 인식: 무료에서 유료로 안 넘어가는 문제 | 제안 초점: 부트캠프 체험 제안 | 바로 행동: 설명란 뒤 체험 버튼과 업그레이드 이유를 함께 본다.",
                "CTA": "지금 체험하고 결정하기",
            },
        ]
    elif fields["context"] == "telegram_join":
        variants = [
            {
                "헤드라인": "설명란만 보고 끝나는 문제를 줄이는 텔레그램 합류 제안",
                "서브카피": "AI 도구 체크리스트 보상과 텔레그램 합류 뒤 바로 얻는 한 가지 이익을 첫 화면에서 함께 보여준다.",
                "핵심불릿": "문제 인식: 설명란만 보고 끝나는 문제 | 제안 초점: 텔레그램 합류 제안 | 바로 행동: 체크리스트를 받고 바로 합류한다.",
                "CTA": "지금 체크리스트 받고 합류하기",
            },
            {
                "헤드라인": "AI 도구 체크리스트 보상으로 바로 움직이게 만드는 텔레그램 합류 제안",
                "서브카피": "유튜브 설명란에서 본 사람이 왜 지금 텔레그램에 들어와야 하는지 한 문장으로 먼저 이해하게 만든다.",
                "핵심불릿": "문제 인식: 합류 이유가 약한 문제 | 제안 초점: 체크리스트 보상 제안 | 바로 행동: 설명란 뒤 한 번에 합류한다.",
                "CTA": "지금 합류 이유 먼저 확인하기",
            },
            {
                "헤드라인": "AI 도구 합류 뒤 바로 얻는 이익을 보여주는 텔레그램 체크리스트 제안",
                "서브카피": "체크리스트 한 장과 텔레그램 공지 하나를 같이 보여줘 링크 클릭 뒤 합류 전환을 짧게 만든다.",
                "핵심불릿": "문제 인식: 링크 클릭 뒤 멈추는 문제 | 제안 초점: 텔레그램 체크리스트 제안 | 바로 행동: 합류와 보상을 한 번에 본다.",
                "CTA": "체크리스트 보고 바로 합류하기",
            },
        ]
    else:
        return None

    picked = variants[idx % len(variants)]
    return {
        "variant": idx + 1,
        "헤드라인": postprocess_korean_copy(picked["헤드라인"]),
        "서브카피": postprocess_korean_copy(picked["서브카피"]),
        "핵심불릿": postprocess_korean_copy(picked["핵심불릿"]),
        "CTA": picked["CTA"],
        "실험": experiment,
        "지표": "클릭률 4퍼센트, 합류 전환율 20퍼센트, 채널 유입 50건, 링크 클릭 30건, 신청 20건을 본다." if fields["context"] == "telegram_join" else fields["metrics"],
    }


def score_variant(variant: dict[str, str], preset: str | None = None) -> dict[str, float]:
    headline = variant["헤드라인"]
    subcopy = variant["서브카피"]
    cta = variant["CTA"]
    full = " ".join([headline, subcopy, variant["핵심불릿"], cta, variant["실험"], variant["지표"]])

    headline_strength = min(1.0, 0.15 * sum(1 for term in HEADLINE_TERMS if term in headline))
    if len(headline) >= 18:
        headline_strength = min(1.0, headline_strength + 0.25)
    if any(term in headline for term in RISK_RELIEF_TERMS):
        headline_strength = min(1.0, headline_strength + 0.1)
    if preset == "ailit" and any(term in headline for term in CONSULTING_TERMS):
        headline_strength = min(1.0, headline_strength + 0.18)

    cta_strength = min(1.0, 0.18 * sum(1 for term in CTA_TERMS if term in cta))
    if any(term in cta for term in RISK_RELIEF_TERMS):
        cta_strength = min(1.0, cta_strength + 0.12)
    if preset == "ailit" and any(term in cta for term in CONSULTING_TERMS):
        cta_strength = min(1.0, cta_strength + 0.16)
    beginner_friendliness = min(1.0, 0.16 * sum(1 for term in BEGINNER_TERMS if term in full))
    brevity = 1.0 if len(subcopy) <= 100 else 0.5 if len(subcopy) <= 160 else 0.1
    hype_penalty = min(0.3, 0.1 * sum(1 for term in HYPE_TERMS if term in full))

    weights = {
        "headline_strength": 0.39,
        "cta_strength": 0.23,
        "beginner_friendliness": 0.16,
        "brevity": 0.22,
    }
    if preset == "vip":
        weights.update({"headline_strength": 0.47, "cta_strength": 0.17, "beginner_friendliness": 0.14, "brevity": 0.22})
    elif preset == "bootcamp":
        weights.update({"headline_strength": 0.35, "cta_strength": 0.23, "beginner_friendliness": 0.22, "brevity": 0.2})
    elif preset == "ailit":
        weights.update({"headline_strength": 0.37, "cta_strength": 0.33, "beginner_friendliness": 0.15, "brevity": 0.15})
    elif preset == "youtube":
        weights.update({"headline_strength": 0.45, "cta_strength": 0.18, "beginner_friendliness": 0.17, "brevity": 0.2})
    elif preset == "x-article":
        weights.update({"headline_strength": 0.43, "cta_strength": 0.15, "beginner_friendliness": 0.16, "brevity": 0.26})

    total = max(
        0.0,
        min(
            1.0,
            weights["headline_strength"] * headline_strength
            + weights["cta_strength"] * cta_strength
            + weights["beginner_friendliness"] * beginner_friendliness
            + weights["brevity"] * brevity
            - hype_penalty,
        ),
    )
    return {
        "total": total,
        "headline_strength": headline_strength,
        "cta_strength": cta_strength,
        "beginner_friendliness": beginner_friendliness,
        "brevity": brevity,
        "hype_penalty": -hype_penalty,
    }


def build_landing_variant(strategy_text: str, variant_index: int) -> dict[str, str]:
    fields = normalize_strategy_fields(parse_sections(strategy_text, SECTION_NAMES))
    idx = variant_index % 3
    context_variant = build_context_landing_variant(fields, idx)
    if context_variant is not None:
        context_variant["scores"] = score_variant(context_variant, preset=fields.get("preset"))
        return context_variant
    headline_pattern = HEADLINE_PATTERNS[idx]
    if idx == 1:
        headline_pattern = SECONDARY_HEADLINE_PATTERNS[0]
    elif idx == 2:
        headline_pattern = TERTIARY_HEADLINE_PATTERNS[0]
    headline = postprocess_korean_copy(
        headline_pattern.format(
            customer_label=fields["customer_label"],
            offer_label=fields["offer_label"],
            problem_label=fields["problem_label"],
        )
    )
    subcopy = postprocess_korean_copy(
        SUBCOPY_PATTERNS[idx].format(
            customer_label=fields["customer_label"],
            offer_label=fields["offer_label"],
            problem_label=fields["problem_label"],
            summary=fields["summary"],
        )
    )
    bullets = postprocess_korean_copy(
        " | ".join(
            pattern.format(problem_label=fields["problem_label"], offer_label=fields["offer_label"], experiment=fields["experiment"])
            for pattern in BULLET_PATTERNS
        )
    )
    cta = CTA_PATTERNS[idx]
    if idx == 1:
        cta = SECONDARY_CTA_PATTERNS[0]
    elif idx == 2:
        cta = TERTIARY_CTA_PATTERNS[0]
    variant = {
        "variant": idx + 1,
        "헤드라인": headline,
        "서브카피": subcopy,
        "핵심불릿": bullets,
        "CTA": cta,
        "실험": build_compare_experiment(fields["experiment"], fields["metrics"], "헤드라인"),
        "지표": fields["metrics"],
    }
    variant["scores"] = score_variant(variant, preset=fields.get("preset"))
    return variant


def apply_preset_to_landing_variants(variants: list[dict[str, str]], preset: str | None) -> list[dict[str, str]]:
    if not preset or preset == "ordinarybiz":
        return variants

    def strip_customer_intro(headline: str) -> str:
        for marker in [
            "를 위한 ",
            "을 위한 ",
            "가 바로 이해하는 ",
            "이 바로 이해하는 ",
            "신뢰를 먼저 확인하고 시작하는 ",
            "지금 바로 비교하고 신청하는 ",
            "먼저 확인하고 결정하는 ",
            "지금 비교가 쉬워지는 ",
        ]:
            if marker in headline:
                return headline.split(marker, 1)[1]
        return headline

    def suffix_after_marker(headline: str, marker: str) -> str:
        return headline.split(marker, 1)[1] if marker in headline else headline

    def strip_repeated_brand(suffix: str, brand: str) -> str:
        return suffix.removeprefix(brand + " ") if suffix.startswith(brand + " ") else suffix

    for item in variants:
        headline = item["헤드라인"]
        if preset == "bootcamp":
            if "부트캠프 체험" in headline or "무료만 보고 멈춘 문제" in headline:
                item["헤드라인"] = headline
                if item["CTA"] == "지금 진단 신청하기":
                    item["CTA"] = "지금 체험 신청하기"
            elif "바로 이해하는" in headline:
                suffix = suffix_after_marker(headline, "바로 이해하는 ")
                item["헤드라인"] = "부트캠프 참가자가 바로 이해하는 " + suffix
            elif headline.startswith("신뢰를 먼저 보여주는 "):
                suffix = suffix_after_marker(headline, "신뢰를 먼저 보여주는 ")
                item["헤드라인"] = "부트캠프 참가자가 빠르게 이해하는 " + suffix
            elif headline.startswith("부담 없이 신청으로 이어지는 "):
                suffix = suffix_after_marker(headline, "부담 없이 신청으로 이어지는 ")
                item["헤드라인"] = "부트캠프 참가자가 바로 신청하는 " + suffix
            else:
                item["헤드라인"] = "부트캠프용 " + strip_customer_intro(headline)
            item["지표"] = "클릭률 3퍼센트, 체험 신청 30건, 결제 전환율 7퍼센트, 이탈률 35퍼센트를 본다."
        elif preset == "vip":
            if headline.startswith("신뢰를 먼저 보여주는 "):
                suffix = suffix_after_marker(headline, "신뢰를 먼저 보여주는 ")
                if "온보딩" in suffix and "체크인" in suffix:
                    item["헤드라인"] = "VIP가 바로 시작하는 라이브 참여 신청 제안"
                    item["CTA"] = "지금 라이브 신청하기"
                    item["서브카피"] = "첫 화면에 라이브 참여 이유와 리플레이 보장을 같이 붙여 VIP 멤버가 바로 참여 결정을 내리게 만든다."
                    item["핵심불릿"] = "문제 인식: 참여 이유가 약한 문제 | 제안 초점: 라이브 신청과 리플레이 보장 | 바로 행동: 첫 화면 문장과 버튼을 반반 비교한다."
                else:
                    item["헤드라인"] = "VIP가 안심하고 이해하는 " + suffix
            elif headline.startswith("부담 없이 신청으로 이어지는 "):
                suffix = suffix_after_marker(headline, "부담 없이 신청으로 이어지는 ")
                item["헤드라인"] = "VIP 전환으로 이어지는 " + suffix
            elif "바로 이해하는" in headline:
                suffix = suffix_after_marker(headline, "바로 이해하는 ")
                if suffix.startswith("VIP "):
                    suffix = suffix.removeprefix("VIP ")
                if "온보딩" in suffix and "체크인" in suffix:
                    item["헤드라인"] = "VIP가 바로 시작하는 라이브 참여 신청 제안"
                    item["CTA"] = "지금 라이브 신청하기"
                    item["서브카피"] = "첫 화면에 라이브 참여 이유와 리플레이 보장을 같이 붙여 VIP 멤버가 바로 참여 결정을 내리게 만든다."
                    item["핵심불릿"] = "문제 인식: 참여 이유가 약한 문제 | 제안 초점: 라이브 신청과 리플레이 보장 | 바로 행동: 첫 화면 문장과 버튼을 반반 비교한다."
                else:
                    item["헤드라인"] = "VIP가 바로 이해하는 " + suffix
            else:
                suffix = strip_customer_intro(headline)
                if suffix.startswith("VIP "):
                    suffix = suffix.removeprefix("VIP ")
                if "온보딩" in suffix and "체크인" in suffix:
                    item["헤드라인"] = "VIP가 바로 시작하는 라이브 참여 신청 제안"
                    item["CTA"] = "지금 라이브 신청하기"
                    item["서브카피"] = "첫 화면에 라이브 참여 이유와 리플레이 보장을 같이 붙여 VIP 멤버가 바로 참여 결정을 내리게 만든다."
                    item["핵심불릿"] = "문제 인식: 참여 이유가 약한 문제 | 제안 초점: 라이브 신청과 리플레이 보장 | 바로 행동: 첫 화면 문장과 버튼을 반반 비교한다."
                else:
                    item["헤드라인"] = "VIP를 위한 " + suffix
            if item["헤드라인"] == "VIP가 바로 시작하는 라이브 참여 신청 제안":
                item["지표"] = "신청 전환율 12퍼센트, 참여율 60퍼센트, 리플레이 시청률 45퍼센트, 신청 20건을 본다."
        elif preset == "ailit":
            if "바로 이해하는" in headline:
                suffix = strip_repeated_brand(suffix_after_marker(headline, "바로 이해하는 "), "Ailit")
                item["헤드라인"] = "Ailit 상담 신청으로 이어지는 " + suffix
                item["CTA"] = "부담 없이 신청하기"
                item["서브카피"] = postprocess_korean_copy(f"{suffix} 하나로 상담 이유를 먼저 보여주고 부담 없이 신청까지 이어지게 만든다.")
            elif headline.startswith("신뢰를 먼저 확인하고 시작하는 ") or headline.startswith("신뢰를 먼저 보여주는 "):
                suffix = strip_repeated_brand(strip_customer_intro(headline), "Ailit")
                item["헤드라인"] = "Ailit 상담 전에 먼저 확인하는 " + suffix
                item["CTA"] = "먼저 확인 후 신청하기"
                item["서브카피"] = postprocess_korean_copy(f"{suffix}를 먼저 확인하게 해 상담 전환 전에 망설임을 줄인다.")
            elif headline.startswith("지금 바로 비교하고 신청하는 ") or headline.startswith("부담 없이 신청으로 이어지는 "):
                suffix = strip_repeated_brand(strip_customer_intro(headline), "Ailit")
                item["헤드라인"] = "Ailit 상담 신청으로 이어지는 " + suffix
                item["CTA"] = "부담 없이 신청하기"
                item["서브카피"] = postprocess_korean_copy(f"{suffix}를 먼저 보여줘 예비 고객이 부담 없이 상담 신청까지 가게 만든다.")
            else:
                suffix = strip_repeated_brand(strip_customer_intro(headline), "Ailit")
                item["헤드라인"] = "Ailit 상담 신청으로 이어지는 " + suffix
                item["CTA"] = "부담 없이 신청하기"
            item["지표"] = "클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트, 문의 20건을 본다."
        elif preset == "youtube":
            if headline.startswith("신뢰를 먼저 보여주는 "):
                suffix = suffix_after_marker(headline, "신뢰를 먼저 보여주는 ")
                item["헤드라인"] = "유튜브 시청자가 안심하고 보는 " + suffix
            elif headline.startswith("부담 없이 신청으로 이어지는 "):
                suffix = suffix_after_marker(headline, "부담 없이 신청으로 이어지는 ")
                item["헤드라인"] = "유튜브 시청자가 바로 이해하는 " + suffix
            elif "바로 이해하는" in headline:
                suffix = strip_customer_intro(headline)
                if suffix.startswith("유튜브 "):
                    suffix = suffix.removeprefix("유튜브 ")
                if "설명란" in suffix and "상담 CTA" in suffix:
                    item["헤드라인"] = "유튜브 시청자가 바로 이해하는 텔레그램 체크리스트 합류 제안"
                    item["CTA"] = "지금 체크리스트 받고 합류하기"
                    item["서브카피"] = "설명란을 본 시청자에게 텔레그램 체크리스트 보상과 합류 뒤 얻는 한 가지 이익을 첫 화면에서 같이 보여준다. 누구 문제를 푸는 제안인지 먼저 보이게 하고 AI 도구 설명란에서 바로 이해하게 만든다."
                    item["핵심불릿"] = "문제 인식: 설명란만 보고 끝나는 문제 | 제안 초점: 텔레그램 체크리스트 합류 제안 | 바로 행동: 설명란 뒤 체크리스트를 받고 바로 합류한다. 누구 문제를 푸는 제안인지 보이게 하고 AI 도구 설명란에서 바로 이해하게 만든다."
                    item["지표"] = "채널 유입 50건, 링크 클릭 30건, 합류 전환율 20퍼센트, 신청 20건을 본다."
                else:
                    item["헤드라인"] = "유튜브 시청자가 바로 이해하는 " + suffix
            else:
                suffix = strip_customer_intro(headline)
                if suffix.startswith("유튜브 "):
                    suffix = suffix.removeprefix("유튜브 ")
                if "설명란" in suffix and "상담 CTA" in suffix:
                    item["헤드라인"] = "유튜브 시청자가 바로 이해하는 텔레그램 체크리스트 합류 제안"
                    item["CTA"] = "지금 체크리스트 받고 합류하기"
                    item["서브카피"] = "설명란을 본 시청자에게 텔레그램 체크리스트 보상과 합류 뒤 얻는 한 가지 이익을 첫 화면에서 같이 보여준다. 누구 문제를 푸는 제안인지 먼저 보이게 하고 AI 도구 설명란에서 바로 이해하게 만든다."
                    item["핵심불릿"] = "문제 인식: 설명란만 보고 끝나는 문제 | 제안 초점: 텔레그램 체크리스트 합류 제안 | 바로 행동: 설명란 뒤 체크리스트를 받고 바로 합류한다. 누구 문제를 푸는 제안인지 보이게 하고 AI 도구 설명란에서 바로 이해하게 만든다."
                    item["지표"] = "채널 유입 50건, 링크 클릭 30건, 합류 전환율 20퍼센트, 신청 20건을 본다."
                else:
                    item["헤드라인"] = "유튜브 시청자가 바로 이해하는 " + suffix
        elif preset == "x-article":
            if item["variant"] == 1:
                item["헤드라인"] = "아티클 독자가 바로 이해하고 저장하는 사례형 제안"
                item["CTA"] = "지금 바로 핵심 보기"
                item["서브카피"] = "첫 단락 한 줄, 사례 한 개, 다음 행동 한 가지를 같은 흐름으로 보여줘 저장과 클릭을 같이 만든다. 누구 문제를 푸는 제안인지 먼저 보이게 한다."
                item["핵심불릿"] = "문제 인식: 긴 글 흐름이 약한 문제 | 제안 초점: 사례형 아티클 제안 | 바로 행동: 첫 단락 한 줄과 사례 한 개를 먼저 본다."
                item["지표"] = "클릭률 3퍼센트, 저장 20건, 댓글 10건, 전환율 5퍼센트를 본다."
            elif item["variant"] == 2:
                item["헤드라인"] = "아티클 독자가 끝까지 읽는 첫 단락 사례 제안"
                item["CTA"] = "사례 흐름 먼저 보기"
                item["서브카피"] = "첫 단락 문제 정의와 사례 압축, 마지막 행동 한 가지를 한 번에 보여줘 긴 글 완독과 저장을 돕는다."
                item["핵심불릿"] = "문제 인식: 첫 단락이 약한 문제 | 제안 초점: 첫 단락과 사례 흐름 제안 | 바로 행동: 사례 한 개와 마지막 행동을 같이 본다."
                item["지표"] = "클릭률 3퍼센트, 저장 20건, 댓글 10건, 전환율 5퍼센트를 본다."
            else:
                item["헤드라인"] = "아티클 다음 행동까지 보이는 첫 단락 제안"
                item["CTA"] = "다음 행동 먼저 보기"
                item["서브카피"] = "긴 글 첫 단락에서 저장 이유를 만들고 마지막 행동까지 이어지게 설계해 댓글과 클릭을 같이 늘린다."
                item["핵심불릿"] = "문제 인식: 저장 이유가 약한 문제 | 제안 초점: 첫 단락과 다음 행동 제안 | 바로 행동: 첫 단락 한 줄과 댓글 질문을 같이 본다."
                item["지표"] = "클릭률 3퍼센트, 저장 20건, 댓글 10건, 전환율 5퍼센트를 본다."
        item["scores"] = score_variant(item, preset=preset)
    return variants


def business_to_landing_variants(strategy_text: str, count: int = 3, preset: str | None = None) -> list[dict[str, str]]:
    variants = [build_landing_variant(strategy_text, i) for i in range(count)]
    variants = apply_preset_to_landing_variants(variants, preset)
    variants.sort(key=lambda item: item["scores"]["total"], reverse=True)
    for rank, item in enumerate(variants, start=1):
        item["rank"] = rank
    return variants


def render_variants(variants: list[dict[str, str]]) -> str:
    blocks = []
    for item in variants:
        lines = [f"=== RANK {item['rank']} | VARIANT {item['variant']} | SCORE {item['scores']['total']:.2f} ==="]
        lines.append(
            f"scores: headline={item['scores']['headline_strength']:.2f}, cta={item['scores']['cta_strength']:.2f}, beginner={item['scores']['beginner_friendliness']:.2f}, brevity={item['scores']['brevity']:.2f}, hype={item['scores']['hype_penalty']:.2f}"
        )
        for key in ["헤드라인", "서브카피", "핵심불릿", "CTA", "실험", "지표"]:
            lines.append(f"{key}: {item[key]}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def save_variants(variants: list[dict[str, str]], output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    text_path = output_dir / f"{stem}-{timestamp}.txt"
    json_path = output_dir / f"{stem}-{timestamp}.json"
    text_path.write_text(render_variants(variants), encoding="utf-8")
    json_path.write_text(json.dumps(variants, ensure_ascii=False, indent=2), encoding="utf-8")
    return text_path, json_path


def main():
    parser = argparse.ArgumentParser(description="Convert a business strategy draft into ranked landing copy variants.")
    parser.add_argument("input", help="Path to a text file containing strategy sections")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of section text")
    parser.add_argument("--count", type=int, default=3, help="Number of landing variants to generate")
    parser.add_argument("--preset", choices=["ordinarybiz", "bootcamp", "vip", "ailit", "youtube", "x-article"], default="ordinarybiz")
    parser.add_argument("--project", help="Optional project slug for dated output folders")
    parser.add_argument("--save", action="store_true", help="Save outputs under outputs/landing/ or outputs/YYYY-MM-DD/project/landing/")
    args = parser.parse_args()

    strategy_text = Path(args.input).read_text(encoding="utf-8")
    variants = business_to_landing_variants(strategy_text, count=args.count, preset=args.preset)
    if args.save:
        if args.project:
            output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d") / args.project / "landing"
        else:
            output_dir = Path("outputs/landing")
        text_path, json_path = save_variants(variants, output_dir, Path(args.input).stem)
        print(f"saved_text={text_path}")
        print(f"saved_json={json_path}")
    if args.json:
        print(json.dumps(variants, ensure_ascii=False, indent=2))
    else:
        print(render_variants(variants))


if __name__ == "__main__":
    main()
