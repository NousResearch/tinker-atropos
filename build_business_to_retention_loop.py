import argparse
import json
import re
from datetime import datetime
from pathlib import Path

SECTION_NAMES = ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]

CHECKIN_PATTERNS = [
    "오늘은 이 한 가지만 끝내면 됩니다: {mission}",
    "지금 멈추지 않게 먼저 이것부터 해봅시다: {mission}",
    "부담 없이 오늘 체크할 한 가지는 이것입니다: {mission}",
]

MISSION_PATTERNS = [
    "첫 주에는 {mission}, 하나만 완료한다.",
    "오늘 첫 행동은 {mission}, 여기서 끝낸다.",
    "먼저 {mission}, 그리고 결과를 남긴다.",
]

RETENTION_PATTERNS = [
    "텔레그램 체크인 스레드에 진행 상황 한 줄을 남기게 한다.",
    "공지 뒤에 짧은 리마인드 메시지로 재방문 타이밍을 한 번 더 잡는다.",
    "하루 뒤 짧은 확인 메시지로 다시 돌아오게 만든다.",
]

PRINCIPLE_PATTERNS = [
    "과장보다 부담 완화와 반복을 우선한다.",
    "한 번에 많이 시키지 말고 한 가지 행동만 요청한다.",
    "초보자도 바로 이해할 쉬운 말로 안내한다.",
]

CHECKIN_TERMS = ["오늘", "한 가지", "먼저", "부담", "체크"]
RETENTION_TERMS = ["텔레그램", "체크인", "리마인드", "재방문", "공지"]
BEGINNER_TERMS = ["쉬운", "바로", "한 가지", "먼저", "부담", "짧은"]
METRIC_TERMS = ["참여율", "재방문율", "이탈률", "전환율", "퍼센트", "%", "건"]
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


def normalize_strategy_fields(sections: dict[str, str]) -> dict[str, str]:
    problem = sections.get("문제", "문제가 아직 정리되지 않았다")
    customer = sections.get("고객", "고객이 아직 정리되지 않았다")
    offer = sections.get("제안", "제안이 아직 정리되지 않았다")
    channel = sections.get("채널", "채널이 아직 정리되지 않았다")
    experiment = sections.get("실험", "오늘 바꿔볼 한 가지를 아직 정하지 못했다")
    metrics = sections.get("지표", "참여율과 재방문율을 아직 정하지 못했다")
    summary = sections.get("한줄결론", "지금 한 가지 행동을 먼저 하게 만든다").removeprefix("지금은 ").strip()
    mission = experiment.removeprefix("오늘은 ").removeprefix("오늘 ").strip().removesuffix(".")
    context_text = " ".join([problem, customer, offer, channel, summary])
    if "부트캠프" in context_text and ("체험" in context_text or "과제" in context_text):
        context = "bootcamp_first_week"
    elif "VIP" in context_text:
        context = "vip_first_week"
    elif "Ailit" in context_text:
        context = "ailit_followup"
    else:
        context = "generic"
    return {
        "problem": problem,
        "customer": customer,
        "offer": offer,
        "channel": channel,
        "mission": mission,
        "metrics": metrics,
        "summary": summary,
        "context": context,
    }


def build_context_retention_variant(fields: dict[str, str], idx: int) -> dict[str, str] | None:
    if fields["context"] == "bootcamp_first_week":
        variants = [
            {
                "체크인메시지": "실전 부트캠프 체크인: 오늘은 체험 미션 한 가지만 끝내면 됩니다.",
                "첫주미션": "첫날 체험 미션 한 가지를 끝내고 둘째 날 체크인에 바로 답한다.",
                "재참여장치": "고정 공지와 체크인 스레드에 미션 안내를 두고 완료 인증에 바로 반응해 다음 행동으로 잇는다.",
                "운영원칙": "쉬운 말로 한 가지 미션만 먼저 주고 텔레그램에서 바로 반응한다.",
            },
            {
                "체크인메시지": "실전 부트캠프 체크인: 오늘은 이 체험 하나만 해보고 결과를 남겨달라.",
                "첫주미션": "첫날 체험 과제 하나를 하고 둘째 날 체크인 알림에 진행 상황을 남긴다.",
                "재참여장치": "체크인 스레드와 다음 날 알림으로 재방문을 만들고 운영자가 미션 인증에 바로 반응한다.",
                "운영원칙": "부담을 낮추는 쉬운 말과 한 가지 행동 기준을 끝까지 유지한다.",
            },
            {
                "체크인메시지": "실전 부트캠프 체크인: 먼저 체험 과제 한 가지부터 시작하면 된다.",
                "첫주미션": "첫날 체험 한 가지를 끝내고 둘째 날 체크인 메시지에 짧게 인증한다.",
                "재참여장치": "텔레그램 고정 공지, 체크인 스레드, 재방문 알림을 같이 써서 첫 주 습관을 만든다.",
                "운영원칙": "초보자도 바로 따라 할 짧은 문장으로 안내하고 미션을 잘게 나눈다.",
            },
        ]
    else:
        return None

    picked = variants[idx % len(variants)]
    return {
        "variant": idx + 1,
        "체크인메시지": picked["체크인메시지"],
        "첫주미션": picked["첫주미션"],
        "재참여장치": picked["재참여장치"],
        "운영원칙": picked["운영원칙"],
        "지표": fields["metrics"],
    }


def score_variant(variant: dict[str, str], preset: str | None = None) -> dict[str, float]:
    checkin = variant["체크인메시지"]
    mechanism = variant["재참여장치"]
    principle = variant["운영원칙"]
    mission = variant["첫주미션"]
    full = " ".join([checkin, mechanism, principle, mission, variant["지표"]])

    checkin_strength = min(1.0, 0.18 * sum(1 for term in CHECKIN_TERMS if term in checkin))
    retention_strength = min(1.0, 0.18 * sum(1 for term in RETENTION_TERMS if term in mechanism))
    beginner_friendliness = min(1.0, 0.16 * sum(1 for term in BEGINNER_TERMS if term in full))
    metric_strength = min(1.0, 0.18 * sum(1 for term in METRIC_TERMS if term in variant["지표"]))
    brevity = 1.0 if len(checkin) <= 72 else 0.45 if len(checkin) <= 120 else 0.1
    hype_penalty = min(0.3, 0.1 * sum(1 for term in HYPE_TERMS if term in full))

    weights = {
        "checkin_strength": 0.27,
        "retention_strength": 0.29,
        "beginner_friendliness": 0.18,
        "metric_strength": 0.14,
        "brevity": 0.12,
    }
    if preset == "bootcamp":
        weights.update({"checkin_strength": 0.34, "retention_strength": 0.24, "beginner_friendliness": 0.18, "metric_strength": 0.14, "brevity": 0.1})
    elif preset == "vip":
        weights.update({"checkin_strength": 0.31, "retention_strength": 0.27, "beginner_friendliness": 0.17, "metric_strength": 0.15, "brevity": 0.1})
    elif preset == "ailit":
        weights.update({"checkin_strength": 0.19, "retention_strength": 0.38, "beginner_friendliness": 0.14, "metric_strength": 0.2, "brevity": 0.09})
    elif preset == "youtube":
        weights.update({"checkin_strength": 0.24, "retention_strength": 0.28, "beginner_friendliness": 0.23, "metric_strength": 0.15, "brevity": 0.1})
    elif preset == "x-article":
        weights.update({"checkin_strength": 0.22, "retention_strength": 0.28, "beginner_friendliness": 0.16, "metric_strength": 0.14, "brevity": 0.2})

    total = max(
        0.0,
        min(
            1.0,
            weights["checkin_strength"] * checkin_strength
            + weights["retention_strength"] * retention_strength
            + weights["beginner_friendliness"] * beginner_friendliness
            + weights["metric_strength"] * metric_strength
            + weights["brevity"] * brevity
            - hype_penalty,
        ),
    )
    return {
        "total": total,
        "checkin_strength": checkin_strength,
        "retention_strength": retention_strength,
        "beginner_friendliness": beginner_friendliness,
        "metric_strength": metric_strength,
        "brevity": brevity,
        "hype_penalty": -hype_penalty,
    }


def build_retention_variant(strategy_text: str, variant_index: int) -> dict[str, str]:
    fields = normalize_strategy_fields(parse_sections(strategy_text, SECTION_NAMES))
    idx = variant_index % 3
    context_variant = build_context_retention_variant(fields, idx)
    if context_variant is not None:
        context_variant["scores"] = score_variant(context_variant)
        return context_variant
    checkin = CHECKIN_PATTERNS[idx].format(mission=fields["mission"])
    mission = MISSION_PATTERNS[idx].format(mission=fields["mission"])
    mechanism = RETENTION_PATTERNS[idx]
    principle = PRINCIPLE_PATTERNS[idx]
    variant = {
        "variant": idx + 1,
        "체크인메시지": checkin,
        "첫주미션": mission,
        "재참여장치": mechanism,
        "운영원칙": principle,
        "지표": fields["metrics"],
    }
    variant["scores"] = score_variant(variant)
    return variant


def apply_preset_to_retention_variants(variants: list[dict[str, str]], preset: str | None) -> list[dict[str, str]]:
    if not preset or preset == "ordinarybiz":
        return variants
    for item in variants:
        if preset == "bootcamp":
            if not item["체크인메시지"].startswith("실전 부트캠프 체크인: "):
                item["체크인메시지"] = "실전 부트캠프 체크인: " + item["체크인메시지"]
            item["지표"] = "첫 주 참여율 60퍼센트, 재방문율 35퍼센트, 이탈률 15퍼센트, 참여 20건을 본다."
        elif preset == "vip":
            if not item["체크인메시지"].startswith("VIP 체크인: "):
                item["체크인메시지"] = "VIP 체크인: " + item["체크인메시지"]
            if item["variant"] == 1:
                item["체크인메시지"] = "VIP 체크인: 오늘은 체크인 한 가지와 온보딩 한 가지만 끝내면 됩니다."
                item["첫주미션"] = "첫 칠 일에는 체크인 한 가지를 끝내고 온보딩 답장에 바로 남긴다."
                item["재참여장치"] = "체크인 스레드, 재방문 알림, 온보딩 반응을 같이 두고 답장이 오면 바로 다음 행동으로 잇는다."
                item["운영원칙"] = "부담 없이 체크인 한 가지와 다음 행동 한 가지만 먼저 안내한다."
            item["지표"] = "첫 칠 일 참여율 60퍼센트, 재방문율 35퍼센트, 이탈률 15퍼센트, 참여 20건을 본다."
        elif preset == "ailit":
            if not item["체크인메시지"].startswith("Ailit 체크인: "):
                item["체크인메시지"] = "Ailit 체크인: " + item["체크인메시지"]
            if item["variant"] == 1:
                item["체크인메시지"] = "Ailit 체크인: 오늘은 첫 칠 일 체크인 한 가지와 입문 상품 다음 단계 한 가지만 끝내면 됩니다."
                item["첫주미션"] = "첫 칠 일에는 텔레그램 체크인 한 가지를 끝내고 입문 상품 다음 단계 미션에 바로 답한다."
                item["재참여장치"] = "텔레그램 고정 공지, 체크인 스레드, 재방문 알림, 업셀 안내를 같이 두고 반응이 오면 바로 다음 단계로 잇는다."
                item["운영원칙"] = "부담 없이 체크인 한 가지와 다음 단계 미션 한 가지만 먼저 안내한다."
            item["지표"] = "후속 클릭률 60퍼센트, 재방문율 35퍼센트, 업셀 전환율 15퍼센트, 이탈률 15퍼센트, 참여 20건을 본다."
        elif preset == "youtube":
            if not item["체크인메시지"].startswith("유튜브 유입 체크인: "):
                item["체크인메시지"] = "유튜브 유입 체크인: " + item["체크인메시지"]
            if item["variant"] == 1:
                item["체크인메시지"] = "유튜브 유입 체크인: 오늘은 첫 주 체크인 한 가지와 자기소개 한 줄만 남기면 됩니다."
                item["첫주미션"] = "첫날에는 텔레그램 고정 공지 아래 자기소개 한 줄과 체크인 한 가지를 남기고 둘째 날에는 참여 미션 하나에 바로 반응한다."
                item["재참여장치"] = "텔레그램 체크인 스레드, 첫 주 참여 미션, 운영자 반응, 재방문 알림으로 첫 발화 경험을 만들고 참여 습관을 붙인다."
                item["운영원칙"] = "쉬운 말로 부담 없이 먼저 참여하게 만들고 오늘 할 한 가지부터 바로 안내한다."
            elif item["variant"] == 2:
                item["체크인메시지"] = "유튜브 유입 체크인: 오늘은 텔레그램 첫 주 체크인 한 가지와 자기소개 한 줄만 남겨보면 됩니다."
                item["첫주미션"] = "첫날에는 텔레그램 체크인 스레드에 자기소개 한 줄을 남기고 둘째 날에는 첫 참여 미션에 바로 답한다."
                item["재참여장치"] = "텔레그램 체크인 스레드와 재방문 알림으로 첫 주 참여 흐름을 붙이고 운영자 반응으로 다시 말을 꺼내게 만든다."
                item["운영원칙"] = "부담 없는 쉬운 문장으로 먼저 참여 한 번을 만들고 바로 반응한다."
            item["지표"] = "첫 주 발화율 40퍼센트, 재방문율 35퍼센트, 이탈률 15퍼센트, 참여 20건을 본다."
        elif preset == "x-article":
            if not item["체크인메시지"].startswith("아티클 후속 체크인: "):
                item["체크인메시지"] = "아티클 후속 체크인: " + item["체크인메시지"]
            if item["variant"] == 1:
                item["체크인메시지"] = "아티클 후속 체크인: 오늘은 첫 단락 한 줄과 사례 한 개만 정리하면 됩니다."
                item["첫주미션"] = "첫날에는 첫 단락 한 줄과 사례 한 개를 저장하고 둘째 날에는 댓글 질문 한 줄과 다음 행동 한 가지를 붙인다."
                item["재참여장치"] = "저장한 독자 체크인, 댓글 질문, 재방문 알림으로 아티클 후속 흐름을 이어가고 다음 글 사례를 다시 꺼내게 만든다."
                item["운영원칙"] = "쉬운 말로 첫 단락과 사례 한 개, 다음 행동 한 가지만 먼저 안내한다."
                item["지표"] = "댓글 참여율 20퍼센트, 재방문율 35퍼센트, 이탈률 15퍼센트, 저장 20건을 본다."
            elif item["variant"] == 2:
                item["체크인메시지"] = "아티클 후속 체크인: 오늘은 저장을 부를 사례 한 개와 댓글 질문 한 줄만 남기면 됩니다."
                item["첫주미션"] = "첫날에는 사례 한 개를 저장하고 둘째 날에는 댓글 질문 한 줄과 다음 행동 한 가지를 붙인다."
                item["재참여장치"] = "저장 독자 체크인과 댓글 리마인드로 다시 돌아오게 만들고 아티클 다음 편 예고를 같이 남긴다."
                item["운영원칙"] = "부담 없이 사례 한 개와 질문 한 줄만 먼저 남기게 만든다."
                item["지표"] = "댓글 참여율 20퍼센트, 재방문율 35퍼센트, 이탈률 15퍼센트, 저장 20건을 본다."
        item["scores"] = score_variant(item, preset=preset)
    return variants


def business_to_retention_variants(strategy_text: str, count: int = 3, preset: str | None = None) -> list[dict[str, str]]:
    variants = [build_retention_variant(strategy_text, i) for i in range(count)]
    variants = apply_preset_to_retention_variants(variants, preset)
    variants.sort(key=lambda item: item["scores"]["total"], reverse=True)
    for rank, item in enumerate(variants, start=1):
        item["rank"] = rank
    return variants


def render_variants(variants: list[dict[str, str]]) -> str:
    blocks = []
    for item in variants:
        lines = [f"=== RANK {item['rank']} | VARIANT {item['variant']} | SCORE {item['scores']['total']:.2f} ==="]
        lines.append(
            f"scores: checkin={item['scores']['checkin_strength']:.2f}, retention={item['scores']['retention_strength']:.2f}, beginner={item['scores']['beginner_friendliness']:.2f}, brevity={item['scores']['brevity']:.2f}, hype={item['scores']['hype_penalty']:.2f}"
        )
        for key in ["체크인메시지", "첫주미션", "재참여장치", "운영원칙", "지표"]:
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
    parser = argparse.ArgumentParser(description="Convert a business strategy draft into ranked retention variants.")
    parser.add_argument("input", help="Path to a text file containing strategy sections")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of section text")
    parser.add_argument("--count", type=int, default=3, help="Number of retention variants to generate")
    parser.add_argument("--preset", choices=["ordinarybiz", "bootcamp", "vip", "ailit", "youtube", "x-article"], default="ordinarybiz")
    parser.add_argument("--project", help="Optional project slug for dated output folders")
    parser.add_argument("--save", action="store_true", help="Save outputs under outputs/retention/ or outputs/YYYY-MM-DD/project/retention/")
    args = parser.parse_args()

    strategy_text = Path(args.input).read_text(encoding="utf-8")
    variants = business_to_retention_variants(strategy_text, count=args.count, preset=args.preset)
    if args.save:
        if args.project:
            output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d") / args.project / "retention"
        else:
            output_dir = Path("outputs/retention")
        text_path, json_path = save_variants(variants, output_dir, Path(args.input).stem)
        print(f"saved_text={text_path}")
        print(f"saved_json={json_path}")
    if args.json:
        print(json.dumps(variants, ensure_ascii=False, indent=2))
    else:
        print(render_variants(variants))


if __name__ == "__main__":
    main()
