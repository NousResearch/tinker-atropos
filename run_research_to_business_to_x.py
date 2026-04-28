import argparse
import json
from datetime import datetime
from pathlib import Path

from build_research_to_business_loop import research_to_business_variants, render_variants as render_business_variants, save_variants as save_business_variants
from build_business_to_x_loop import business_to_x_variants, render_variants as render_x_variants, save_variants as save_x_variants


def main():
    parser = argparse.ArgumentParser(description="Run research -> business -> x end-to-end pipeline.")
    parser.add_argument("input", help="Path to research draft text file")
    parser.add_argument("--business-count", type=int, default=3)
    parser.add_argument("--x-count", type=int, default=3)
    parser.add_argument("--all-business", action="store_true", help="Generate X variants for every business variant instead of only top-ranked one")
    parser.add_argument("--save", action="store_true", help="Save intermediate and final outputs")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    research_text = input_path.read_text(encoding="utf-8")

    business_variants = research_to_business_variants(research_text, count=args.business_count)

    selected_business = business_variants if args.all_business else [business_variants[0]]
    x_results = []
    for business in selected_business:
        strategy_text = "\n".join(
            f"{key}: {business[key]}" for key in ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]
        )
        x_variants = business_to_x_variants(strategy_text, count=args.x_count)
        x_results.append(
            {
                "source_business_rank": business["rank"],
                "source_business_variant": business["variant"],
                "strategy": business,
                "x_variants": x_variants,
            }
        )

    saved = {}
    if args.save:
        stem = input_path.stem
        business_text, business_json = save_business_variants(business_variants, Path("outputs/business"), stem + "-from-research")
        saved["business_text"] = str(business_text)
        saved["business_json"] = str(business_json)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for item in x_results:
            x_text, x_json = save_x_variants(
                item["x_variants"],
                Path("outputs/x"),
                f"{stem}-business-rank{item['source_business_rank']}-{timestamp}",
            )
            item["saved_text"] = str(x_text)
            item["saved_json"] = str(x_json)

    if args.json:
        print(json.dumps({"business_variants": business_variants, "x_results": x_results, "saved": saved}, ensure_ascii=False, indent=2))
        return

    print("=== BUSINESS VARIANTS ===")
    print(render_business_variants(business_variants))
    print()
    for item in x_results:
        print(f"=== X VARIANTS FROM BUSINESS RANK {item['source_business_rank']} ===")
        print(render_x_variants(item["x_variants"]))
        if args.save:
            print(f"saved_text={item['saved_text']}")
            print(f"saved_json={item['saved_json']}")
        print()
    if args.save:
        print(f"saved_business_text={saved['business_text']}")
        print(f"saved_business_json={saved['business_json']}")


if __name__ == "__main__":
    main()
