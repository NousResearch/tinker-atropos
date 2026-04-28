import argparse
import json
from datetime import datetime
from pathlib import Path

from build_research_to_business_loop import research_to_business_variants, render_variants as render_business_variants, save_variants as save_business_variants
from build_business_to_retention_loop import business_to_retention_variants, render_variants as render_retention_variants, save_variants as save_retention_variants


def main():
    parser = argparse.ArgumentParser(description="Run research -> business -> retention end-to-end pipeline.")
    parser.add_argument("input", help="Path to research draft text file")
    parser.add_argument("--business-count", type=int, default=3)
    parser.add_argument("--retention-count", type=int, default=3)
    parser.add_argument("--all-business", action="store_true", help="Generate retention variants for every business variant instead of only top-ranked one")
    parser.add_argument("--save", action="store_true", help="Save intermediate and final outputs")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    research_text = input_path.read_text(encoding="utf-8")

    business_variants = research_to_business_variants(research_text, count=args.business_count)

    selected_business = business_variants if args.all_business else [business_variants[0]]
    retention_results = []
    for business in selected_business:
        strategy_text = "\n".join(
            f"{key}: {business[key]}" for key in ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]
        )
        retention_variants = business_to_retention_variants(strategy_text, count=args.retention_count)
        retention_results.append(
            {
                "source_business_rank": business["rank"],
                "source_business_variant": business["variant"],
                "strategy": business,
                "retention_variants": retention_variants,
            }
        )

    saved = {}
    if args.save:
        stem = input_path.stem
        business_text, business_json = save_business_variants(business_variants, Path("outputs/business"), stem + "-from-research")
        saved["business_text"] = str(business_text)
        saved["business_json"] = str(business_json)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for item in retention_results:
            retention_text, retention_json = save_retention_variants(
                item["retention_variants"],
                Path("outputs/retention"),
                f"{stem}-business-rank{item['source_business_rank']}-{timestamp}",
            )
            item["saved_text"] = str(retention_text)
            item["saved_json"] = str(retention_json)

    if args.json:
        print(json.dumps({"business_variants": business_variants, "retention_results": retention_results, "saved": saved}, ensure_ascii=False, indent=2))
        return

    print("=== BUSINESS VARIANTS ===")
    print(render_business_variants(business_variants))
    print()
    for item in retention_results:
        print(f"=== RETENTION VARIANTS FROM BUSINESS RANK {item['source_business_rank']} ===")
        print(render_retention_variants(item['retention_variants']))
        if args.save:
            print(f"saved_text={item['saved_text']}")
            print(f"saved_json={item['saved_json']}")
        print()
    if args.save:
        print(f"saved_business_text={saved['business_text']}")
        print(f"saved_business_json={saved['business_json']}")


if __name__ == "__main__":
    main()
