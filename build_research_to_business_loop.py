import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

SECTION_NAMES = ["가설", "찾을정보", "비교기준", "결론", "다음행동"]

PROBLEM_PATTERNS = [
    "{conclusion} 그래서 지금 전략이 흐려질 수 있다.",
    "{conclusion} 때문에 지금 한 가지 우선 제안이 더 필요하다.",
    "{conclusion} 이 상태라서 실행 전에 포지셔닝을 먼저 정리해야 한다.",
]

CUSTOMER_PATTERNS = [
    "AI 도구에는 관심이 있지만 무엇부터 시작할지 고민하는 일인 사업가",
    "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객",
    "이미 관심은 있지만 신뢰 근거가 부족해 멈추는 잠재 고객",
]

OFFER_PATTERNS = [
    "입문 장벽이 낮은 제안을 한 가지 먼저 강조한다.",
    "신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.",
    "후기와 사례를 붙인 입문형 제안을 우선 노출한다.",
]

CHANNEL_PATTERNS = [
    "랜딩 첫 화면과 유튜브 설명란에서 같은 한 문장을 반복한다.",
    "X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.",
    "텔레그램 공지와 랜딩 첫 화면을 같은 메시지로 맞춘다.",
]

EXPERIMENT_PATTERNS = [
    "오늘 첫 화면 문구 하나만 바꾸고 일주일 동안 클릭률과 신청 수를 본다.",
    "오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.",
    "오늘 입문 제안 문장 하나만 바꾸고 클릭률 차이를 비교한다.",
]

SUMMARY_PATTERNS = [
    "지금은 한 가지 제안과 신뢰 요소를 먼저 붙이는 것이 우선이다.",
    "지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.",
    "지금은 낮은 장벽과 높은 신뢰를 같이 보여주는 것이 우선이다.",
]

PRESET_SECTION_OVERRIDES = {
    "ailit": {
        "제안": "Ailit 입문 상품으로 먼저 반응을 확인하고 상담 업셀로 이어지는 단일 제안을 먼저 보여준다.",
        "채널": "유튜브 설명란과 랜딩 첫 화면에서 Ailit 상담 이유를 같은 한 문장으로 반복한다.",
        "실험": "오늘 상담 헤드라인과 CTA 한 줄만 바꾸고 일주일 동안 클릭률과 상담 신청을 본다.",
        "지표": "입문 상품 구매, 상담 전환, 업셀 전환율을 함께 본다.",
    },
    "vip": {
        "제안": "VIP 온보딩 체크인을 텔레그램에서 바로 시작하게 만드는 단일 제안을 먼저 보여준다.",
        "채널": "텔레그램 공지와 고정 메시지에서 VIP 체크인 한 문장을 같은 말로 반복한다.",
        "실험": "오늘 첫 주 체크인 문장 하나만 바꾸고 일주일 동안 참여율과 재방문율을 본다.",
        "지표": "첫 칠 일 참여율, 이탈률, 재방문율을 함께 본다.",
    },
    "bootcamp": {
        "제안": "부트캠프 체험 과제와 멤버십 업그레이드를 같은 문장으로 묶은 단일 제안을 먼저 보여준다.",
        "채널": "유튜브 설명란과 랜딩 첫 화면에서 부트캠프 체험과 업그레이드 이유를 같은 문장으로 반복한다.",
        "실험": "오늘 체험 과제 제안 한 줄만 바꾸고 일주일 동안 체험 신청과 결제 전환율을 본다.",
        "지표": "체험 신청, 결제 전환율, 첫 주 유지율을 함께 본다.",
    },
    "youtube": {
        "제안": "유튜브 설명란 첫 문장과 상담 CTA를 같은 제안으로 묶은 단일 제안을 먼저 보여준다.",
        "채널": "유튜브 설명란, 댓글 고정, 랜딩 첫 화면에서 같은 상담 전환 문장을 반복한다.",
        "실험": "오늘 유튜브 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청을 본다.",
        "지표": "클릭률, 상담 신청, 전환율을 함께 본다.",
    },
}

PROBLEM_TERMS = ["문제", "부족", "장벽", "신뢰", "우선"]
ACTION_TERMS = ["오늘", "바꾸", "비교", "정리", "먼저"]
BEGINNER_TERMS = ["한 가지", "먼저", "바로", "입문", "쉽게"]
HYPE_TERMS = ["혁신", "최고", "압도", "무조건", "대박"]

BusinessVariant = dict[str, Any]


def _compress_conclusion(conclusion: str) -> str:
    if "입문 장벽" in conclusion and "후기와 사례" in conclusion:
        return "입문은 쉬우나 신뢰 근거는 약하다."
    return conclusion.split('. ')[0].strip()


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


def normalize_research_fields(sections: dict[str, str]) -> dict[str, str]:
    conclusion = sections.get("결론", "결론이 아직 정리되지 않았다.")
    next_action = sections.get("다음행동", "오늘 바꿔볼 한 가지를 아직 정하지 못했다.")
    return {
        "conclusion": conclusion,
        "compressed_conclusion": _compress_conclusion(conclusion),
        "next_action": next_action.removeprefix("오늘 ").removeprefix("오늘은 ").strip(),
    }


def score_variant(variant: BusinessVariant) -> dict[str, float]:
    problem = variant["문제"]
    experiment = variant["실험"]
    summary = variant["한줄결론"]
    full = " ".join(str(v) for v in variant.values())

    problem_clarity = min(1.0, 0.18 * sum(1 for term in PROBLEM_TERMS if term in problem))
    actionability = min(1.0, 0.18 * sum(1 for term in ACTION_TERMS if term in experiment))
    beginner_friendliness = min(1.0, 0.16 * sum(1 for term in BEGINNER_TERMS if term in full))
    brevity = 1.0 if len(summary) <= 80 else 0.5 if len(summary) <= 140 else 0.1
    hype_penalty = min(0.3, 0.1 * sum(1 for term in HYPE_TERMS if term in full))

    total = max(0.0, min(1.0, 0.32 * problem_clarity + 0.28 * actionability + 0.2 * beginner_friendliness + 0.2 * brevity - hype_penalty))
    return {
        "total": total,
        "problem_clarity": problem_clarity,
        "actionability": actionability,
        "beginner_friendliness": beginner_friendliness,
        "brevity": brevity,
        "hype_penalty": -hype_penalty,
    }


def build_business_variant(research_text: str, variant_index: int, preset: Optional[str] = None) -> BusinessVariant:
    fields = normalize_research_fields(parse_sections(research_text, SECTION_NAMES))
    idx = variant_index % 3
    variant = {
        "variant": idx + 1,
        "문제": PROBLEM_PATTERNS[idx].format(conclusion=fields["compressed_conclusion"]),
        "고객": CUSTOMER_PATTERNS[idx],
        "제안": OFFER_PATTERNS[idx],
        "채널": CHANNEL_PATTERNS[idx],
        "실험": EXPERIMENT_PATTERNS[idx],
        "지표": "클릭률, 신청 수, 전환율을 함께 본다.",
        "한줄결론": SUMMARY_PATTERNS[idx],
    }
    if preset in PRESET_SECTION_OVERRIDES:
        variant.update(PRESET_SECTION_OVERRIDES[preset])
    variant["scores"] = score_variant(variant)
    return variant


def research_to_business_variants(research_text: str, count: int = 3, preset: Optional[str] = None) -> list[BusinessVariant]:
    variants = [build_business_variant(research_text, i, preset=preset) for i in range(count)]
    variants.sort(key=lambda item: item["scores"]["total"], reverse=True)
    for rank, item in enumerate(variants, start=1):
        item["rank"] = rank
    return variants


def render_variants(variants: list[BusinessVariant]) -> str:
    blocks = []
    for item in variants:
        lines = [f"=== RANK {item['rank']} | VARIANT {item['variant']} | SCORE {item['scores']['total']:.2f} ==="]
        lines.append(
            f"scores: problem={item['scores']['problem_clarity']:.2f}, action={item['scores']['actionability']:.2f}, beginner={item['scores']['beginner_friendliness']:.2f}, brevity={item['scores']['brevity']:.2f}, hype={item['scores']['hype_penalty']:.2f}"
        )
        for key in ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]:
            lines.append(f"{key}: {item[key]}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def save_variants(variants: list[BusinessVariant], output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    text_path = output_dir / f"{stem}-{timestamp}.txt"
    json_path = output_dir / f"{stem}-{timestamp}.json"
    text_path.write_text(render_variants(variants), encoding="utf-8")
    json_path.write_text(json.dumps(variants, ensure_ascii=False, indent=2), encoding="utf-8")
    return text_path, json_path


def main():
    parser = argparse.ArgumentParser(description="Convert a research draft into ranked business strategy variants.")
    parser.add_argument("input", help="Path to a text file containing research sections")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of section text")
    parser.add_argument("--count", type=int, default=3, help="Number of strategy variants to generate")
    parser.add_argument("--save", action="store_true", help="Save outputs under outputs/business/")
    args = parser.parse_args()

    research_text = Path(args.input).read_text(encoding="utf-8")
    variants = research_to_business_variants(research_text, count=args.count)
    if args.save:
        text_path, json_path = save_variants(variants, Path("outputs/business"), Path(args.input).stem)
        print(f"saved_text={text_path}")
        print(f"saved_json={json_path}")
    if args.json:
        print(json.dumps(variants, ensure_ascii=False, indent=2))
    else:
        print(render_variants(variants))


if __name__ == "__main__":
    main()
