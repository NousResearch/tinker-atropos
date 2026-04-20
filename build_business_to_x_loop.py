import argparse
import json
import re
from datetime import datetime
from pathlib import Path


SECTION_NAMES = ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]

HOOK_PATTERNS = [
    "{problem} 그래서 대부분은 해결보다 멈춤부터 반복한다.",
    "{problem} 많은 사람이 도구보다 흐름을 먼저 고치지 못해 여기서 막힌다.",
    "{problem} 문제는 더 열심히가 아니라 먼저 한 가지를 안 정한 데 있다.",
]

BODY_PATTERNS = [
    "핵심은 {offer}이고, 지금은 {summary}",
    "지금 필요한 건 {offer} 같은 한 가지 제안이고, 이유는 {summary}",
    "여기서 중요한 건 {offer}에 초점을 모으는 것이고, 오늘 할 일은 {experiment}",
]

COMMENT_PATTERNS = [
    "지금 당신 비즈니스에서 가장 막힌 한 지점을 댓글로 남겨달라.",
    "당신이 오늘 가장 먼저 고치고 싶은 한 지점을 댓글로 적어달라.",
    "지금 제일 답답한 병목 하나를 댓글로 남겨달라.",
]

ACTION_PATTERNS = [
    "오늘은 {experiment}",
    "지금은 {experiment}",
    "오늘 바로 할 일은 {experiment}",
]

GUARDRAIL_PATTERNS = [
    "과장 없이 오늘 할 한 가지 행동만 말한다.",
    "허풍 없이 지금 바꿀 한 가지 행동만 제안한다.",
    "추상론 대신 오늘 실행할 한 가지로 끝낸다.",
]

HOOK_TERMS = ["문제", "이유", "막힌", "먼저", "반복", "흐름"]
COMMENT_TERMS = ["댓글", "남겨", "적어", "하나", "지금"]
ACTION_TERMS = ["오늘", "지금", "하나", "먼저", "바꾸", "확인"]
HYPE_TERMS = ["혁신", "최고", "압도", "무조건", "대박"]
BEGINNER_TERMS = ["쉬운", "바로", "한 가지", "먼저", "지금", "핵심"]
JARGON_TERMS = ["퍼널", "레버리지", "파이프라인", "고도화", "최적화"]


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


def _clean_prefixes(summary: str, experiment: str) -> tuple[str, str]:
    cleaned_summary = summary.removeprefix("지금은 ").strip()
    cleaned_experiment = experiment.removeprefix("오늘은 ").removeprefix("오늘 ").strip()
    return cleaned_summary, cleaned_experiment


def _clean_offer_for_body(offer: str) -> str:
    cleaned = offer.strip()
    for suffix in ["를 먼저 보여준다.", "을 먼저 보여준다.", "를 강조한다.", "을 강조한다.", "를 우선 노출한다.", "을 우선 노출한다."]:
        if cleaned.endswith(suffix):
            base = cleaned[: -len(suffix)].strip()
            return base if base.endswith("제안") else base + " 제안"
    return cleaned.removesuffix('.')


def score_variant(variant: dict[str, str], preset: str | None = None) -> dict[str, float]:
    hook = variant["후크"]
    body = variant["본문"]
    comment = variant["댓글유도"]
    action = variant["행동유도"]
    guardrail = variant["금지"]
    full = " ".join([hook, body, comment, action, guardrail])

    hook_strength = min(1.0, 0.18 * sum(1 for term in HOOK_TERMS if term in hook))
    if len(hook) >= 45:
        hook_strength = min(1.0, hook_strength + 0.2)

    comment_strength = min(1.0, 0.18 * sum(1 for term in COMMENT_TERMS if term in comment))
    if "?" in comment or "댓글" in comment:
        comment_strength = min(1.0, comment_strength + 0.15)

    action_clarity = min(1.0, 0.2 * sum(1 for term in ACTION_TERMS if term in action or term in guardrail))

    beginner_friendliness = min(1.0, 0.18 * sum(1 for term in BEGINNER_TERMS if term in full))
    jargon_hits = sum(1 for term in JARGON_TERMS if term in full)
    if jargon_hits:
        beginner_friendliness = max(0.0, beginner_friendliness - 0.18 * jargon_hits)

    body_brevity = 1.0 if 40 <= len(body) <= 96 else 0.4 if len(body) <= 135 else 0.1

    hype_penalty = min(0.3, 0.1 * sum(1 for term in HYPE_TERMS if term in full))

    weights = {
        "hook_strength": 0.27,
        "comment_strength": 0.16,
        "action_clarity": 0.32,
        "beginner_friendliness": 0.16,
        "body_brevity": 0.09,
    }
    if preset == "youtube":
        weights.update({"hook_strength": 0.27, "comment_strength": 0.16, "action_clarity": 0.31, "beginner_friendliness": 0.16, "body_brevity": 0.1})
    elif preset == "x-article":
        weights.update({"hook_strength": 0.34, "comment_strength": 0.15, "action_clarity": 0.2, "beginner_friendliness": 0.15, "body_brevity": 0.16})
    elif preset == "bootcamp":
        weights.update({"hook_strength": 0.26, "comment_strength": 0.16, "action_clarity": 0.31, "beginner_friendliness": 0.19, "body_brevity": 0.08})
    elif preset == "vip":
        weights.update({"hook_strength": 0.33, "comment_strength": 0.16, "action_clarity": 0.27, "beginner_friendliness": 0.14, "body_brevity": 0.1})
    elif preset == "ailit":
        weights.update({"hook_strength": 0.27, "comment_strength": 0.14, "action_clarity": 0.31, "beginner_friendliness": 0.16, "body_brevity": 0.12})

    total = max(
        0.0,
        min(
            1.0,
            weights["hook_strength"] * hook_strength
            + weights["comment_strength"] * comment_strength
            + weights["action_clarity"] * action_clarity
            + weights["beginner_friendliness"] * beginner_friendliness
            + weights["body_brevity"] * body_brevity
            - hype_penalty,
        ),
    )
    return {
        "total": total,
        "hook_strength": hook_strength,
        "comment_strength": comment_strength,
        "action_clarity": action_clarity,
        "beginner_friendliness": beginner_friendliness,
        "body_brevity": body_brevity,
        "hype_penalty": -hype_penalty,
    }


def build_x_variant(strategy_text: str, variant_index: int) -> dict[str, str]:
    sections = parse_sections(strategy_text, SECTION_NAMES)

    problem = sections.get("문제", "문제가 아직 선명하지 않다.")
    offer = sections.get("제안", "제안이 아직 정리되지 않았다.")
    experiment = sections.get("실험", "오늘 바꿔볼 한 가지를 아직 정하지 못했다.")
    summary = sections.get("한줄결론", offer)

    cleaned_summary, cleaned_experiment = _clean_prefixes(summary, experiment)
    cleaned_offer = _clean_offer_for_body(offer)

    idx = variant_index % 3
    hook = HOOK_PATTERNS[idx].format(problem=problem)
    body = BODY_PATTERNS[idx].format(offer=cleaned_offer, summary=cleaned_summary, experiment=cleaned_experiment)
    comment = COMMENT_PATTERNS[idx]
    action = ACTION_PATTERNS[idx].format(experiment=cleaned_experiment)
    guardrail = GUARDRAIL_PATTERNS[idx]

    variant = {
        "variant": idx + 1,
        "후크": hook,
        "본문": body,
        "댓글유도": comment,
        "행동유도": action,
        "금지": guardrail,
    }
    variant["scores"] = score_variant(variant)
    return variant


def apply_preset_to_x_variants(variants: list[dict[str, str]], preset: str | None) -> list[dict[str, str]]:
    if not preset or preset == "ordinarybiz":
        return variants
    for item in variants:
        if preset == "bootcamp":
            item["본문"] += " 부트캠프 무료에서 유료 전환은 설명란 한 줄과 체험 과제 한 가지를 같이 붙일 때 더 잘 보인다."
            item["댓글유도"] = "지금 무료에서 유료로 안 넘어가는 가장 막힌 한 지점이 무엇인지 댓글로 남겨달라."
            item["행동유도"] = item["행동유도"].rstrip(".") + " 그리고 설명란 첫 문장 하나만 같이 바꿔보자."
        elif preset == "vip":
            if item["variant"] == 1:
                item["후크"] = "왜 VIP 멤버는 조용해질까, 문제는 운영자가 재참여 체크인 한 줄을 먼저 안 보내는 데 있다."
                item["본문"] = "VIP 운영자는 재참여 체크인 한 줄을 먼저 보내야 한다. 체크인 문장 하나가 조용한 VIP 멤버를 다시 움직이게 만들고 운영자가 바로 반응할 이유를 만든다."
                item["댓글유도"] = "당신 운영자는 오늘 어떤 재참여 체크인 한 줄을 보낼지 무엇인지 댓글로 직접 남겨달라?"
                item["행동유도"] = "오늘 지금 VIP 재참여 체크인 한 줄만 바꿔서 보내고 답장 반응을 확인해보자."
                item["금지"] = "비난 없이 오늘 보낼 한 가지 체크인 문장만 말한다."
            elif item["variant"] == 2:
                item["후크"] = "왜 VIP 재참여는 늦어질수록 더 조용해질까, 문제는 운영자가 체크인 타이밍을 놓치는 데 있다."
                item["본문"] = "운영자는 VIP 멤버가 조용해지기 전에 재참여 체크인 한 줄을 먼저 보내야 한다. 체크인 문장 하나가 다음 답장을 열고 재참여 흐름을 다시 붙인다."
                item["댓글유도"] = "지금 당신 운영자가 바로 보낼 체크인 한 줄이 무엇인지 댓글로 직접 적어달라?"
                item["행동유도"] = "오늘 지금 VIP 체크인 한 줄만 다시 쓰고 재참여 답장 수를 확인해보자."
                item["금지"] = "감정 과잉 없이 오늘 보낼 한 가지 문장만 말한다."
            else:
                item["본문"] += " VIP 운영자가 재참여 체크인 한 줄을 먼저 보내야 흐름이 다시 움직인다."
                item["행동유도"] = "오늘 지금 VIP 체크인 한 줄만 다시 쓰고 재참여 답장 수를 확인해보자."
                item["댓글유도"] = "지금 당신 운영자가 바로 보낼 체크인 한 줄이 무엇인지 댓글로 직접 남겨달라?"
        elif preset == "ailit":
            if item["variant"] == 1:
                item["후크"] = "왜 Ailit 상담보다 입문 상품 링크가 먼저 눌려야 할까, 문제는 부담이 큰 상담부터 권해 첫 행동이 끊기는 데 있다."
                item["본문"] = "Ailit 입문 상품 링크 하나를 먼저 보여주면 상담 부담이 내려간다. 입문 상품으로 먼저 반응을 확인하고 상담은 그다음으로 잇자."
                item["댓글유도"] = "지금 당신은 상담이 먼저 부담인지, 입문 상품 링크가 더 쉬운지 무엇인지 댓글로 직접 남겨달라?"
                item["행동유도"] = "오늘 지금 입문 상품 링크 한 줄만 앞에 두고 클릭률을 확인하는 실험을 해보자."
                item["금지"] = "허풍 없이 오늘 할 한 가지 행동만 말한다."
            elif item["variant"] == 2:
                item["후크"] = "왜 Ailit는 상담보다 입문 상품 링크가 먼저 보여야 할까, 문제는 쉬운 첫 행동 없이 바로 상담을 권하는 데 있다."
                item["본문"] = "Ailit 입문 상품 링크를 먼저 두면 잠재 고객이 바로 눌러볼 이유가 생긴다. 입문 상품으로 반응을 확인하고 상담은 다음 단계로 이어지게 만들자."
                item["댓글유도"] = "당신은 지금 상담과 입문 상품 가운데 무엇이 더 쉬운 첫 행동인지 댓글로 직접 적어달라?"
                item["행동유도"] = "오늘 지금 Ailit 입문 상품 링크 한 줄만 앞에 두고 클릭률을 확인해보자."
                item["금지"] = "과장 없이 오늘 바꿀 한 가지 행동만 말한다."
            else:
                item["본문"] += " Ailit 입문 상품 링크부터 눌러보게 하고 상담은 다음 단계로 잇는다."
                item["행동유도"] = "오늘 지금 Ailit 입문 상품 링크 한 줄만 앞에 두고 클릭률을 확인해보자."
                item["댓글유도"] = "지금 당신에게 상담보다 쉬운 첫 행동이 무엇인지 댓글로 직접 남겨달라."
        elif preset == "youtube":
            item["본문"] += " 유튜브 설명란 첫 문장과 바로 이어지게 연결한다."
        elif preset == "x-article":
            if item["variant"] == 1:
                item["후크"] = "왜 X 아티클은 첫 단락 한 줄이 약하면 끝까지 안 읽히고 저장도 안 될까, 문제는 읽을 이유와 사례 흐름을 먼저 못 보여주기 때문이다."
                item["본문"] = "X 아티클은 첫 단락 한 줄로 문제를 정의하고 사례 한 개로 저장 이유를 만든다. 중간에는 사례 흐름을 짧게 압축하고 끝에서는 다음 행동 한 가지를 바로 보여준다."
                item["댓글유도"] = "지금 이 아티클에 먼저 넣을 사례 한 개가 무엇인지 댓글로 직접 남겨달라?"
                item["행동유도"] = "오늘 지금 첫 단락 한 줄과 사례 한 개를 바꿔보고 저장 수와 클릭률을 확인하는 실험을 해보자."
                item["금지"] = "과장 대신 저장할 가치가 느껴지는 한 가지 통찰만 남긴다."
            elif item["variant"] == 2:
                item["후크"] = "왜 긴 글은 정보가 많아도 저장되지 않을까, 문제는 첫 단락과 사례와 마지막 행동이 같은 흐름으로 안 묶이기 때문이다."
                item["본문"] = "아티클 독자는 사례 한 개와 다음 행동 한 가지가 같이 보일 때 저장한다. 첫 단락에서 문제를 짚고 중간에는 사례를 압축하고 끝에서는 한 가지 행동을 남기자."
                item["댓글유도"] = "당신이 저장하고 싶은 긴 글 사례 한 개가 무엇인지 댓글로 직접 적어달라?"
                item["행동유도"] = "오늘 지금 첫 단락 한 줄과 저장을 부르는 사례 한 개만 먼저 정리하자."
                item["금지"] = "뜬구름 대신 저장과 다음 행동으로 이어질 한 가지 구조만 남긴다."
            else:
                item["후크"] += " 아티클은 저장 이유가 첫 단락에서 바로 보여야 한다."
                item["본문"] += " 첫 단락, 사례 한 개, 마지막 한 가지 행동을 긴 글 흐름으로 묶는다."
                item["댓글유도"] = "지금 이 긴 글에서 먼저 살릴 사례 한 개가 무엇인지 댓글로 직접 남겨달라?"
                item["행동유도"] = "오늘 지금 첫 단락 한 줄과 사례 한 개만 먼저 정리하자."
                item["금지"] = "과장 대신 저장할 가치가 느껴지는 한 가지 통찰만 남긴다."
        item["scores"] = score_variant(item, preset=preset)
    return variants


def business_to_x_variants(strategy_text: str, count: int = 3, preset: str | None = None) -> list[dict[str, str]]:
    variants = [build_x_variant(strategy_text, i) for i in range(count)]
    variants = apply_preset_to_x_variants(variants, preset)
    variants.sort(key=lambda item: item["scores"]["total"], reverse=True)
    for rank, item in enumerate(variants, start=1):
        item["rank"] = rank
    return variants


def render_variants(variants: list[dict[str, str]]) -> str:
    blocks = []
    for item in variants:
        lines = [f"=== RANK {item['rank']} | VARIANT {item['variant']} | SCORE {item['scores']['total']:.2f} ==="]
        lines.append(
            "scores: "
            f"hook={item['scores']['hook_strength']:.2f}, "
            f"comment={item['scores']['comment_strength']:.2f}, "
            f"action={item['scores']['action_clarity']:.2f}, "
            f"beginner={item['scores']['beginner_friendliness']:.2f}, "
            f"brevity={item['scores']['body_brevity']:.2f}, "
            f"hype={item['scores']['hype_penalty']:.2f}"
        )
        for key in ["후크", "본문", "댓글유도", "행동유도", "금지"]:
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
    parser = argparse.ArgumentParser(description="Convert a business strategy draft into one or more ranked X strategy drafts.")
    parser.add_argument("input", help="Path to a text file containing strategy sections")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of section text")
    parser.add_argument("--count", type=int, default=3, help="Number of X variants to generate")
    parser.add_argument("--preset", choices=["ordinarybiz", "bootcamp", "vip", "ailit", "youtube", "x-article"], default="ordinarybiz")
    parser.add_argument("--project", help="Optional project slug for dated output folders")
    parser.add_argument("--save", action="store_true", help="Save outputs under outputs/x/ or outputs/YYYY-MM-DD/project/x/")
    args = parser.parse_args()

    strategy_text = Path(args.input).read_text(encoding="utf-8")
    variants = business_to_x_variants(strategy_text, count=args.count, preset=args.preset)
    if args.save:
        if args.project:
            output_dir = Path("outputs") / datetime.now().strftime("%Y-%m-%d") / args.project / "x"
        else:
            output_dir = Path("outputs/x")
        text_path, json_path = save_variants(variants, output_dir, Path(args.input).stem)
        print(f"saved_text={text_path}")
        print(f"saved_json={json_path}")
    if args.json:
        print(json.dumps(variants, ensure_ascii=False, indent=2))
    else:
        print(render_variants(variants))


if __name__ == "__main__":
    main()
