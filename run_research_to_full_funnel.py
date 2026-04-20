import argparse
import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from build_research_to_business_loop import research_to_business_variants, render_variants as render_business_variants, save_variants as save_business_variants
from build_business_to_x_loop import business_to_x_variants, render_variants as render_x_variants, save_variants as save_x_variants
from build_business_to_landing_loop import business_to_landing_variants, render_variants as render_landing_variants, save_variants as save_landing_variants
from build_business_to_retention_loop import business_to_retention_variants, render_variants as render_retention_variants, save_variants as save_retention_variants
from tinker_atropos.environments.min_business_strategy_tinker import BUSINESS_STRATEGY_ITEMS, score_business_answer
from tinker_atropos.environments.min_x_strategy_tinker import X_STRATEGY_ITEMS, score_x_answer
from tinker_atropos.environments.min_landing_cro_tinker import LANDING_CRO_ITEMS, score_landing_answer
from tinker_atropos.environments.min_membership_retention_tinker import MEMBERSHIP_RETENTION_ITEMS, score_retention_answer


BUSINESS_KEYS = ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]
X_KEYS = ["후크", "본문", "댓글유도", "행동유도", "금지"]
RETENTION_KEYS = ["체크인메시지", "첫주미션", "재참여장치", "운영원칙", "지표"]

PRESET_HINTS = {
    "ordinarybiz": [],
    "bootcamp": ["부트캠프", "체험", "업그레이드", "멤버십"],
    "vip": ["VIP", "체크인", "온보딩", "재참여"],
    "ailit": ["Ailit", "상담", "입문 상품", "업셀"],
    "youtube": ["유튜브", "설명란", "채널", "시청자"],
    "x-article": ["X", "아티클", "긴 글", "후크"],
}

REWARD_EVAL_SPECS = {
    "business": {
        "items": BUSINESS_STRATEGY_ITEMS,
        "score_fn": score_business_answer,
        "summary_fields": ["scenario", "offer"],
    },
    "x": {
        "items": X_STRATEGY_ITEMS,
        "score_fn": score_x_answer,
        "summary_fields": ["topic", "desired_action"],
    },
    "landing": {
        "items": LANDING_CRO_ITEMS,
        "score_fn": score_landing_answer,
        "summary_fields": ["page_type", "offer"],
    },
    "retention": {
        "items": MEMBERSHIP_RETENTION_ITEMS,
        "score_fn": score_retention_answer,
        "summary_fields": ["membership", "risk_stage"],
    },
}


def strategy_text_from_business(business: dict) -> str:
    return "\n".join(f"{key}: {business.get(key, '')}" for key in BUSINESS_KEYS)


def x_text_from_variant(variant: dict) -> str:
    return "\n".join(f"{key}: {variant.get(key, '')}" for key in X_KEYS)


def landing_text_from_variant(strategy: dict, variant: dict) -> str:
    bullet_text = variant.get("핵심불릿", "")
    return "\n".join(
        [
            f"병목: {strategy.get('문제', '')}",
            f"개선안: {variant.get('서브카피', '')}",
            f"카피수정: 헤드라인 {variant.get('헤드라인', '')} / CTA {variant.get('CTA', '')} / 핵심불릿 {bullet_text}",
            f"실험: {variant.get('실험', '')}",
            f"지표: {variant.get('지표', '')}",
        ]
    )


def retention_text_from_variant(strategy: dict, variant: dict) -> str:
    return "\n".join(
        [
            f"이탈원인: {strategy.get('문제', '')}",
            f"온보딩수정: {variant.get('첫주미션', '')}",
            f"리텐션장치: {variant.get('재참여장치', '')}",
            f"운영메시지: {variant.get('체크인메시지', '')} / 운영원칙 {variant.get('운영원칙', '')}",
            f"지표: {variant.get('지표', '')}",
        ]
    )


def _collect_item_terms(item: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for value in item.values():
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                terms.append(cleaned)
        elif isinstance(value, list):
            for child in value:
                if isinstance(child, str):
                    cleaned = child.strip()
                    if cleaned:
                        terms.append(cleaned)
    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        lowered = term.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(term)
    return deduped


def _build_item_summary(item: dict[str, Any], fields: list[str]) -> str:
    summary_parts = [str(item[field]).strip() for field in fields if item.get(field)]
    return " | ".join(summary_parts)


def select_best_reward_item(stage: str, reference_text: str, preset: str = "ordinarybiz") -> dict[str, Any]:
    spec = REWARD_EVAL_SPECS[stage]
    lowered_text = reference_text.lower()
    preset_hints = PRESET_HINTS.get(preset, [])
    best_candidate: dict[str, Any] | None = None

    for index, item in enumerate(spec["items"]):
        item_terms = _collect_item_terms(item)
        matched_terms = [term for term in item_terms if term.lower() in lowered_text]
        preset_term_hits = [term for term in preset_hints if term.lower() in lowered_text and any(term.lower() in item_term.lower() for item_term in item_terms)]
        long_field_hits = sum(1 for field in spec["summary_fields"] if str(item.get(field, "")).strip().lower() in lowered_text)
        lexical_score = float(len(matched_terms)) + 1.5 * float(len(preset_term_hits)) + 2.0 * float(long_field_hits)
        confidence = round(min(1.0, lexical_score / max(4.0, float(len(item_terms)))), 4)
        candidate = {
            "item_index": index,
            "item": item,
            "matched_terms": matched_terms[:8],
            "preset_term_hits": preset_term_hits,
            "lexical_score": round(lexical_score, 4),
            "confidence": confidence,
            "item_summary": _build_item_summary(item, spec["summary_fields"]),
        }
        if best_candidate is None or (candidate["lexical_score"], candidate["confidence"], -candidate["item_index"]) > (
            best_candidate["lexical_score"],
            best_candidate["confidence"],
            -best_candidate["item_index"],
        ):
            best_candidate = candidate

    return best_candidate or {
        "item_index": 0,
        "item": spec["items"][0],
        "matched_terms": [],
        "preset_term_hits": [],
        "lexical_score": 0.0,
        "confidence": 0.0,
        "item_summary": _build_item_summary(spec["items"][0], spec["summary_fields"]),
    }


def attach_reward_replay(best: dict[str, Any], research_text: str, preset: str = "ordinarybiz") -> dict[str, Any]:
    enriched = copy.deepcopy(best)
    business = enriched.get("business")
    x_variant = enriched.get("x")
    landing_variant = enriched.get("landing")
    retention_variant = enriched.get("retention")

    if business:
        business_answer = strategy_text_from_business(business)
        business_match = select_best_reward_item("business", f"{research_text}\n{business_answer}", preset=preset)
        business_metrics = REWARD_EVAL_SPECS["business"]["score_fn"](business_answer, business_match["item"])
        business["reward_eval"] = {
            "matched_item_index": business_match["item_index"],
            "matched_item_summary": business_match["item_summary"],
            "matched_terms": business_match["matched_terms"],
            "confidence": business_match["confidence"],
            "lexical_score": business_match["lexical_score"],
            "scores": business_metrics,
        }
    else:
        business_answer = research_text

    if x_variant:
        x_answer = x_text_from_variant(x_variant)
        x_match = select_best_reward_item("x", f"{research_text}\n{business_answer}\n{x_answer}", preset=preset)
        x_metrics = REWARD_EVAL_SPECS["x"]["score_fn"](x_answer, x_match["item"])
        x_variant["reward_eval"] = {
            "matched_item_index": x_match["item_index"],
            "matched_item_summary": x_match["item_summary"],
            "matched_terms": x_match["matched_terms"],
            "confidence": x_match["confidence"],
            "lexical_score": x_match["lexical_score"],
            "scores": x_metrics,
        }

    if landing_variant and business:
        landing_answer = landing_text_from_variant(business, landing_variant)
        landing_match = select_best_reward_item("landing", f"{research_text}\n{business_answer}\n{landing_answer}", preset=preset)
        landing_metrics = REWARD_EVAL_SPECS["landing"]["score_fn"](landing_answer, landing_match["item"])
        landing_variant["reward_eval"] = {
            "matched_item_index": landing_match["item_index"],
            "matched_item_summary": landing_match["item_summary"],
            "matched_terms": landing_match["matched_terms"],
            "confidence": landing_match["confidence"],
            "lexical_score": landing_match["lexical_score"],
            "scores": landing_metrics,
        }

    if retention_variant and business:
        retention_answer = retention_text_from_variant(business, retention_variant)
        retention_match = select_best_reward_item("retention", f"{research_text}\n{business_answer}\n{retention_answer}", preset=preset)
        retention_metrics = REWARD_EVAL_SPECS["retention"]["score_fn"](retention_answer, retention_match["item"])
        retention_variant["reward_eval"] = {
            "matched_item_index": retention_match["item_index"],
            "matched_item_summary": retention_match["item_summary"],
            "matched_terms": retention_match["matched_terms"],
            "confidence": retention_match["confidence"],
            "lexical_score": retention_match["lexical_score"],
            "scores": retention_metrics,
        }

    return enriched


def attach_reward_replay_to_funnel_results(
    research_text: str,
    funnel_results: list[dict[str, Any]],
    preset: str = "ordinarybiz",
) -> list[dict[str, Any]]:
    enriched_results = copy.deepcopy(funnel_results)
    for path in enriched_results:
        strategy = path.get("strategy")
        if not strategy:
            continue
        strategy_text = strategy_text_from_business(strategy)
        strategy_reward = attach_reward_replay({"business": strategy}, research_text, preset=preset)
        path["strategy"] = strategy_reward["business"]

        x_variants = []
        for variant in path.get("x_variants", []):
            x_answer = x_text_from_variant(variant)
            x_match = select_best_reward_item("x", f"{research_text}\n{strategy_text}\n{x_answer}", preset=preset)
            enriched_variant = copy.deepcopy(variant)
            enriched_variant["reward_eval"] = {
                "matched_item_index": x_match["item_index"],
                "matched_item_summary": x_match["item_summary"],
                "matched_terms": x_match["matched_terms"],
                "confidence": x_match["confidence"],
                "lexical_score": x_match["lexical_score"],
                "scores": REWARD_EVAL_SPECS["x"]["score_fn"](x_answer, x_match["item"]),
            }
            x_variants.append(enriched_variant)
        path["x_variants"] = x_variants

        landing_variants = []
        for variant in path.get("landing_variants", []):
            landing_answer = landing_text_from_variant(strategy, variant)
            landing_match = select_best_reward_item("landing", f"{research_text}\n{strategy_text}\n{landing_answer}", preset=preset)
            enriched_variant = copy.deepcopy(variant)
            enriched_variant["reward_eval"] = {
                "matched_item_index": landing_match["item_index"],
                "matched_item_summary": landing_match["item_summary"],
                "matched_terms": landing_match["matched_terms"],
                "confidence": landing_match["confidence"],
                "lexical_score": landing_match["lexical_score"],
                "scores": REWARD_EVAL_SPECS["landing"]["score_fn"](landing_answer, landing_match["item"]),
            }
            landing_variants.append(enriched_variant)
        path["landing_variants"] = landing_variants

        retention_variants = []
        for variant in path.get("retention_variants", []):
            retention_answer = retention_text_from_variant(strategy, variant)
            retention_match = select_best_reward_item("retention", f"{research_text}\n{strategy_text}\n{retention_answer}", preset=preset)
            enriched_variant = copy.deepcopy(variant)
            enriched_variant["reward_eval"] = {
                "matched_item_index": retention_match["item_index"],
                "matched_item_summary": retention_match["item_summary"],
                "matched_terms": retention_match["matched_terms"],
                "confidence": retention_match["confidence"],
                "lexical_score": retention_match["lexical_score"],
                "scores": REWARD_EVAL_SPECS["retention"]["score_fn"](retention_answer, retention_match["item"]),
            }
            retention_variants.append(enriched_variant)
        path["retention_variants"] = retention_variants
    return enriched_results


def build_reward_replay_aggregate(best: dict[str, Any], funnel_results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}

    def summarize_stage(variants: list[dict[str, Any]], top_stage: dict[str, Any] | None) -> dict[str, Any] | None:
        reward_pairs = []
        for variant in variants:
            reward = variant.get("reward_eval", {}).get("scores", {}).get("total")
            if reward is None:
                continue
            reward_pairs.append((variant, float(reward)))
        if not reward_pairs:
            return None
        rewards = [pair[1] for pair in reward_pairs]
        best_reward_variant, best_reward = max(reward_pairs, key=lambda pair: pair[1])
        top_generator_reward = None
        if top_stage and top_stage.get("reward_eval"):
            top_generator_reward = round(float(top_stage["reward_eval"]["scores"]["total"]), 4)
        return {
            "variant_count": len(reward_pairs),
            "reward_mean": round(sum(rewards) / len(rewards), 4),
            "reward_max": round(best_reward, 4),
            "reward_min": round(min(rewards), 4),
            "best_reward_rank": best_reward_variant.get("rank"),
            "top_generator_rank": top_stage.get("rank") if top_stage else None,
            "top_generator_reward": top_generator_reward,
        }

    business_stage = best.get("business")
    business_reward = business_stage.get("reward_eval", {}).get("scores", {}).get("total") if business_stage else None
    if business_reward is not None:
        aggregate["business"] = {
            "variant_count": 1,
            "reward_mean": round(float(business_reward), 4),
            "reward_max": round(float(business_reward), 4),
            "reward_min": round(float(business_reward), 4),
            "best_reward_rank": business_stage.get("rank"),
            "top_generator_rank": business_stage.get("rank"),
            "top_generator_reward": round(float(business_reward), 4),
        }

    stage_key_map = {
        "x": "x_variants",
        "landing": "landing_variants",
        "retention": "retention_variants",
    }
    for stage_name, key in stage_key_map.items():
        all_variants: list[dict[str, Any]] = []
        for path in funnel_results:
            all_variants.extend(path.get(key, []))
        summary = summarize_stage(all_variants, best.get(stage_name))
        if summary:
            aggregate[stage_name] = summary
    return aggregate


def apply_preset_to_best(best: dict, preset: Optional[str]) -> dict:
    if not preset or preset == "ordinarybiz":
        return best

    business = best.get("business")
    x = best.get("x")
    landing = best.get("landing")
    retention = best.get("retention")

    if preset == "bootcamp":
        if business:
            business["한줄결론"] += " 실전 부트캠프 문맥에서 바로 써먹게 만드는 것이 중요하다."
        if x and x.get("본문") and "부트캠프" not in x["본문"]:
            x["본문"] = f"부트캠프 실전 기준으로 {x['본문']}"
        if retention and retention.get("체크인메시지") and "실전" not in retention["체크인메시지"]:
            retention["체크인메시지"] = f"실전 체크인: {retention['체크인메시지']}"
        return best
    if preset == "vip":
        if business:
            business["한줄결론"] += " VIP에게는 더 빠른 실행과 더 높은 신뢰가 핵심이다."
        if landing and landing.get("헤드라인") and "VIP" not in landing["헤드라인"]:
            landing["헤드라인"] = f"VIP {landing['헤드라인']}"
        if retention and retention.get("체크인메시지") and "VIP" not in retention["체크인메시지"]:
            retention["체크인메시지"] = f"VIP 체크인: {retention['체크인메시지']}"
        return best
    if preset == "ailit":
        if business:
            business["한줄결론"] += " Ailit 상담 전환 흐름에 바로 붙이는 것이 중요하다."
        return best
    if preset == "youtube":
        if business:
            business["한줄결론"] += " 유튜브 채널 흐름과 설명란 전환을 같이 맞추는 것이 중요하다."
        if x and x.get("본문") and "유튜브" not in x["본문"]:
            x["본문"] = f"유튜브 전환 기준으로 {x['본문']}"
        if landing and landing.get("헤드라인") and "유튜브" not in landing["헤드라인"]:
            landing["헤드라인"] = f"유튜브 {landing['헤드라인']}"
        return best
    if preset == "x-article":
        if business:
            business["한줄결론"] += " 긴 글 아티클 기준으로 논리를 더 선명하게 압축하는 것이 중요하다."
        if x and x.get("본문") and "아티클" not in x["본문"] and "긴 글" not in x["본문"]:
            x["본문"] = f"긴 글 아티클 기준으로 {x['본문']}"
        return best
    return best


def choose_best_stage_variants(
    funnel_results: list[dict[str, Any]],
    selection_mode: str = "generator",
) -> dict[str, Any]:
    selected: dict[str, Any] = {"business": None, "x": None, "landing": None, "retention": None}

    strategies = [path.get("strategy") for path in funnel_results if path.get("strategy")]
    if strategies:
        if selection_mode == "reward":
            selected["business"] = max(
                strategies,
                key=lambda item: float(item.get("reward_eval", {}).get("scores", {}).get("total", -1.0)),
            )
        else:
            selected["business"] = max(strategies, key=lambda item: float(item.get("scores", {}).get("total", -1.0)))

    def gather(stage_key: str) -> list[dict[str, Any]]:
        variants: list[dict[str, Any]] = []
        for path in funnel_results:
            variants.extend(path.get(stage_key, []))
        return variants

    for stage_name, stage_key in [("x", "x_variants"), ("landing", "landing_variants"), ("retention", "retention_variants")]:
        variants = gather(stage_key)
        if not variants:
            continue
        if selection_mode == "reward":
            selected[stage_name] = max(
                variants,
                key=lambda item: float(item.get("reward_eval", {}).get("scores", {}).get("total", -1.0)),
            )
        else:
            selected[stage_name] = max(variants, key=lambda item: float(item.get("scores", {}).get("total", -1.0)))
    return selected


def build_best_summary(research_text: str, business_variants, funnel_results, preset: str = "ordinarybiz", selection_mode: str = "generator"):
    selected = choose_best_stage_variants(funnel_results, selection_mode=selection_mode)
    top_business = selected.get("business") or (business_variants[0] if business_variants else None)
    top_x = selected.get("x")
    top_landing = selected.get("landing")
    top_retention = selected.get("retention")
    summary = {
        "business": top_business,
        "x": top_x,
        "landing": top_landing,
        "retention": top_retention,
    }
    enriched = attach_reward_replay(summary, research_text, preset=preset)
    enriched["selection_mode"] = selection_mode
    enriched["reward_replay_aggregate"] = build_reward_replay_aggregate(enriched, funnel_results)
    return enriched


def render_best_summary(best: dict) -> str:
    blocks = ["# Best Results Summary"]
    if best.get("business"):
        b = best["business"]
        blocks += [
            "\n## Best Business",
            f"rank: {b['rank']} | variant: {b['variant']} | score: {b['scores']['total']:.2f}",
        ] + [f"{key}: {b[key]}" for key in BUSINESS_KEYS]
        if b.get("reward_eval"):
            reward = b["reward_eval"]
            blocks.append(
                f"reward_total: {reward['scores']['total']:.2f} | reward_match: {reward['matched_item_summary']} | confidence: {reward['confidence']:.2f}"
            )
    if best.get("x"):
        x = best["x"]
        blocks += [
            "\n## Best X",
            f"rank: {x['rank']} | variant: {x['variant']} | score: {x['scores']['total']:.2f}",
        ] + [f"{key}: {x[key]}" for key in ["후크", "본문", "댓글유도", "행동유도", "금지"]]
        if x.get("reward_eval"):
            reward = x["reward_eval"]
            blocks.append(
                f"reward_total: {reward['scores']['total']:.2f} | reward_match: {reward['matched_item_summary']} | confidence: {reward['confidence']:.2f}"
            )
    if best.get("landing"):
        landing_variant = best["landing"]
        blocks += [
            "\n## Best Landing",
            f"rank: {landing_variant['rank']} | variant: {landing_variant['variant']} | score: {landing_variant['scores']['total']:.2f}",
        ] + [f"{key}: {landing_variant[key]}" for key in ["헤드라인", "서브카피", "핵심불릿", "CTA", "실험", "지표"]]
        if landing_variant.get("reward_eval"):
            reward = landing_variant["reward_eval"]
            blocks.append(
                f"reward_total: {reward['scores']['total']:.2f} | reward_match: {reward['matched_item_summary']} | confidence: {reward['confidence']:.2f}"
            )
    if best.get("retention"):
        r = best["retention"]
        blocks += [
            "\n## Best Retention",
            f"rank: {r['rank']} | variant: {r['variant']} | score: {r['scores']['total']:.2f}",
        ] + [f"{key}: {r[key]}" for key in ["체크인메시지", "첫주미션", "재참여장치", "운영원칙", "지표"]]
        if r.get("reward_eval"):
            reward = r["reward_eval"]
            blocks.append(
                f"reward_total: {reward['scores']['total']:.2f} | reward_match: {reward['matched_item_summary']} | confidence: {reward['confidence']:.2f}"
            )
    return "\n".join(blocks)


def render_reward_replay_section(best: dict) -> list[str]:
    lines = ["reward_replay:"]
    for stage_name, label in [("business", "business"), ("x", "x"), ("landing", "landing"), ("retention", "retention")]:
        stage = best.get(stage_name)
        reward = stage.get("reward_eval") if stage else None
        if not reward:
            continue
        lines.append(
            f"- {label}: total={reward['scores']['total']:.2f}, match={reward['matched_item_summary']}, confidence={reward['confidence']:.2f}"
        )
    return lines if len(lines) > 1 else []


def _extract_stage_quality_snapshot(best: dict[str, Any], stage_name: str) -> dict[str, Any] | None:
    stage = best.get(stage_name)
    if not stage:
        return None
    reward_total = stage.get("reward_eval", {}).get("scores", {}).get("total")
    generator_total = stage.get("scores", {}).get("total")
    return {
        "rank": stage.get("rank"),
        "variant": stage.get("variant"),
        "generator_total": round(float(generator_total), 4) if generator_total is not None else None,
        "reward_total": round(float(reward_total), 4) if reward_total is not None else None,
    }


def render_quality_comparison_report(
    input_name: str,
    generator_best: dict[str, Any],
    reward_best: dict[str, Any],
    preset: str = "ordinarybiz",
) -> str:
    lines = [
        "# Quality Comparison Report",
        f"input: {input_name}",
        f"preset: {preset}",
        f"generator_selection_mode: {generator_best.get('selection_mode', 'generator')}",
        f"reward_selection_mode: {reward_best.get('selection_mode', 'reward')}",
    ]
    stage_counts = reward_best.get("reward_replay_aggregate") or generator_best.get("reward_replay_aggregate") or {}
    reward_preferred = 0
    same_stage = 0
    generator_kept = 0
    comparison_lines: list[str] = []

    for stage_name in ["business", "x", "landing", "retention"]:
        generator_snapshot = _extract_stage_quality_snapshot(generator_best, stage_name)
        reward_snapshot = _extract_stage_quality_snapshot(reward_best, stage_name)
        if not generator_snapshot and not reward_snapshot:
            continue
        variant_count = stage_counts.get(stage_name, {}).get("variant_count")
        if generator_snapshot == reward_snapshot:
            decision = "동일"
            same_stage += 1
        else:
            generator_reward = generator_snapshot.get("reward_total") if generator_snapshot else None
            reward_reward = reward_snapshot.get("reward_total") if reward_snapshot else None
            if reward_reward is not None and (generator_reward is None or reward_reward > generator_reward):
                decision = "보상 선택이 더 적합"
                reward_preferred += 1
            else:
                decision = "생성기 선택 유지"
                generator_kept += 1
        comparison_lines.append(
            "- {stage}: variants={variants} | generator rank={g_rank} variant={g_variant} score={g_score} reward={g_reward} | reward rank={r_rank} variant={r_variant} score={r_score} reward={r_reward} | decision={decision}".format(
                stage=stage_name,
                variants=variant_count if variant_count is not None else "-",
                g_rank=generator_snapshot.get("rank") if generator_snapshot else "-",
                g_variant=generator_snapshot.get("variant") if generator_snapshot else "-",
                g_score=f"{generator_snapshot['generator_total']:.2f}" if generator_snapshot and generator_snapshot.get("generator_total") is not None else "-",
                g_reward=f"{generator_snapshot['reward_total']:.2f}" if generator_snapshot and generator_snapshot.get("reward_total") is not None else "-",
                r_rank=reward_snapshot.get("rank") if reward_snapshot else "-",
                r_variant=reward_snapshot.get("variant") if reward_snapshot else "-",
                r_score=f"{reward_snapshot['generator_total']:.2f}" if reward_snapshot and reward_snapshot.get("generator_total") is not None else "-",
                r_reward=f"{reward_snapshot['reward_total']:.2f}" if reward_snapshot and reward_snapshot.get("reward_total") is not None else "-",
                decision=decision,
            )
        )

    recommended_mode = "reward" if reward_preferred > 0 else "generator"
    lines += [
        f"권장 선택기준: {recommended_mode}",
        f"보상 선택 우세 단계 수: {reward_preferred}",
        f"동일 단계 수: {same_stage}",
        f"생성기 유지 단계 수: {generator_kept}",
        "",
        "## Stage Comparison",
    ]
    lines.extend(comparison_lines)
    return "\n".join(lines)


def render_execution_report(input_name: str, business_variants, funnel_results, preset: str = "ordinarybiz", best: Optional[dict] = None) -> str:
    fallback_business = business_variants[0] if business_variants else None
    fallback_x = funnel_results[0]["x_variants"][0] if funnel_results else None
    fallback_landing = funnel_results[0]["landing_variants"][0] if funnel_results else None
    fallback_retention = funnel_results[0]["retention_variants"][0] if funnel_results else None
    best = best or {
        "business": fallback_business,
        "x": fallback_x,
        "landing": fallback_landing,
        "retention": fallback_retention,
    }
    top_business = best.get("business") if best.get("business", {}).get("scores") else fallback_business
    top_x = best.get("x") if best.get("x", {}).get("scores") else fallback_x
    top_landing = best.get("landing") if best.get("landing", {}).get("scores") else fallback_landing
    top_retention = best.get("retention") if best.get("retention", {}).get("scores") else fallback_retention
    best_scores = {
        "business": top_business['scores']['total'] if top_business else 0,
        "x": top_x['scores']['total'] if top_x else 0,
        "landing": top_landing['scores']['total'] if top_landing else 0,
        "retention": top_retention['scores']['total'] if top_retention else 0,
    }
    best_stage = max(best_scores, key=best_scores.__getitem__)
    operator_summary_lines = []
    if top_business and top_x and top_landing and top_retention:
        operator_summary_lines = [
            f"1. X 실행: {top_x['행동유도']}",
            f"2. 랜딩 적용: {top_landing['헤드라인']}",
            f"3. 유지 시작: {top_retention['첫주미션']}",
        ]
    preset_notes = {
        "ordinarybiz": "operator_note: ordinarybiz 기본 흐름으로 빠르게 검토하고 바로 실행한다.",
        "bootcamp": "operator_note: 부트캠프 참가자가 바로 따라 할 수 있는 실전 과제로 검토한다.",
        "vip": "operator_note: VIP용 빠른 실행과 높은 신뢰 기준으로 검토한다.",
        "ailit": "operator_note: Ailit 상담 전환 흐름과 제안 연결성을 우선 본다.",
        "youtube": "operator_note: 유튜브 시청자와 설명란 전환 연결을 우선 본다.",
        "x-article": "operator_note: X 아티클 확장성과 긴 글 논리 흐름을 우선 본다.",
    }
    preset_checklists = {
        "ordinarybiz": ["핵심 제안 한 줄 확인", "X 행동 문장 확인", "랜딩 CTA 확인"],
        "bootcamp": ["참가자가 바로 따라 할 한 단계 확인", "체크인 문구 실전성 확인", "랜딩 설명 단순성 확인"],
        "vip": ["가장 빠른 실행안 확인", "신뢰 표현 강화 확인", "VIP 톤 중복 여부 확인"],
        "ailit": ["상담 전환 문장 확인", "CTA와 상담 흐름 연결 확인", "체크인에서 Ailit 언급 확인"],
        "youtube": ["설명란 연결 문장 확인", "유튜브 시청자용 헤드라인 확인", "유입 체크인 문구 확인"],
        "x-article": ["긴 글 확장성 확인", "후크와 본문 논리 연결 확인", "아티클 후속 체크인 확인"],
    }
    lines = [
        "# Execution Report",
        f"input: {input_name}",
        f"preset: {preset}",
        f"selection_mode: {best.get('selection_mode', 'generator')}",
        f"business_variants: {len(business_variants)}",
        f"funnel_paths: {len(funnel_results)}",
        f"best_stage: {best_stage}",
        f"best_stage_score: {best_scores[best_stage]:.2f}",
        preset_notes.get(preset, preset_notes['ordinarybiz']),
    ]
    if operator_summary_lines:
        lines += ["operator_summary:"] + operator_summary_lines
    lines += ["operator_checklist:"] + [f"- {item}" for item in preset_checklists.get(preset, preset_checklists['ordinarybiz'])]
    if top_business:
        lines.append(f"best_business_score: {top_business['scores']['total']:.2f}")
    if top_x:
        lines.append(f"best_x_score: {top_x['scores']['total']:.2f}")
    if top_landing:
        lines.append(f"best_landing_score: {top_landing['scores']['total']:.2f}")
    if top_retention:
        lines.append(f"best_retention_score: {top_retention['scores']['total']:.2f}")
    reward_lines = render_reward_replay_section(best)
    if reward_lines:
        lines.extend(reward_lines)
    reward_aggregate = best.get("reward_replay_aggregate") or build_reward_replay_aggregate(best, funnel_results)
    if reward_aggregate:
        lines.append("reward_replay_aggregate:")
        for stage_name in ["business", "x", "landing", "retention"]:
            stage_summary = reward_aggregate.get(stage_name)
            if not stage_summary:
                continue
            lines.append(
                f"- {stage_name}: variants={stage_summary['variant_count']}, mean={stage_summary['reward_mean']:.2f}, max={stage_summary['reward_max']:.2f}, top_generator_reward={stage_summary['top_generator_reward']:.2f}, best_reward_rank={stage_summary['best_reward_rank']}"
            )
    lines.append("mode: full_funnel")
    return "\n".join(lines)


def render_final_output(best: dict, preset: str = "ordinarybiz") -> str:
    business = best.get("business")
    x = best.get("x")
    landing = best.get("landing")
    retention = best.get("retention")
    title_map = {
        "ordinarybiz": "# Final Output",
        "bootcamp": "# Final Output - Bootcamp Brief",
        "vip": "# Final Output - VIP Brief",
        "ailit": "# Final Output - Ailit Brief",
        "youtube": "# Final Output - YouTube Brief",
        "x-article": "# Final Output - X Article Brief",
    }
    focus_map = {
        "ordinarybiz": "실전 적용",
        "bootcamp": "실전 과제",
        "vip": "빠른 실행",
        "ailit": "상담 전환",
        "youtube": "설명란 전환",
        "x-article": "긴 글 확장",
    }
    lines = [title_map.get(preset, title_map["ordinarybiz"])]
    if business or x or landing:
        lines += ["\n## Today", f"- 초점: {focus_map.get(preset, focus_map['ordinarybiz'])}"]
        if business:
            lines.append(f"- 전략: {business['한줄결론']}")
        if x:
            lines.append(f"- 행동: {x['행동유도']}")
        if landing:
            lines.append(f"- 랜딩 적용: {landing['헤드라인']}")
    if x or landing:
        lines += ["\n## Assets"]
        if x:
            lines.append(f"- 후크: {x['후크']}")
            lines.append(f"- 본문: {x['본문']}")
        if landing:
            lines.append(f"- 헤드라인: {landing['헤드라인']}")
            lines.append(f"- CTA: {landing['CTA']}")
    if retention:
        lines += ["\n## Retention"]
        lines.append(f"- 체크인: {retention['체크인메시지']}")
        lines.append(f"- 첫주미션: {retention['첫주미션']}")
        lines.append(f"- 재참여: {retention['재참여장치']}")
    note_map = {
        "bootcamp": ("## Coaching Note", "- 참가자가 바로 따라 할 수 있는 한 단계만 먼저 꺼낸다."),
        "vip": ("## VIP Note", "- 속도, 신뢰, 선명함 기준으로 가장 빠른 실행안을 우선 적용한다."),
        "ailit": ("## Ailit Note", "- 상담 전환으로 이어지는 문장과 CTA 연결을 먼저 점검한다."),
        "youtube": ("## YouTube Note", "- 설명란 첫 문장과 랜딩 헤드라인의 일치를 먼저 확인한다."),
        "x-article": ("## X Article Note", "- 긴 글 논리와 저장 가치가 유지되는지 먼저 확인한다."),
    }
    if preset in note_map:
        lines += ["", note_map[preset][0], note_map[preset][1]]
    checklist_map = {
        "ordinarybiz": ["핵심 제안 한 줄 확인", "X 행동 문장 확인", "랜딩 CTA 확인"],
        "bootcamp": ["실전 과제 한 단계 확인", "체크인 문구 실전성 확인", "랜딩 설명 단순성 확인"],
        "vip": ["빠른 실행안 확인", "신뢰 표현 강화 확인", "VIP 톤 중복 여부 확인"],
        "ailit": ["상담 전환 문장 확인", "CTA 연결 확인", "Ailit 체크인 문구 확인"],
        "youtube": ["설명란 연결 문장 확인", "유튜브 헤드라인 확인", "유입 체크인 확인"],
        "x-article": ["긴 글 확장성 확인", "후크-본문 논리 확인", "아티클 후속 체크인 확인"],
    }
    lines += ["\n## Checklist"] + [f"- {item}" for item in checklist_map.get(preset, checklist_map['ordinarybiz'])]
    return "\n".join(lines)


def render_one_line_summary(best: dict, preset: str = "ordinarybiz") -> str:
    x = best.get("x")
    landing = best.get("landing")
    retention = best.get("retention")
    label_map = {
        "ordinarybiz": "오늘 할 일",
        "bootcamp": "부트캠프 오늘 할 일",
        "vip": "VIP 오늘 할 일",
        "ailit": "Ailit 오늘 할 일",
        "youtube": "YouTube 오늘 할 일",
        "x-article": "X Article 오늘 할 일",
    }
    parts = [label_map.get(preset, label_map["ordinarybiz"])]
    parts.append(f"선택기준: {best.get('selection_mode', 'generator')}")
    if x:
        parts.append(f"X: {x['행동유도']}")
    if landing:
        parts.append(f"랜딩: {landing['헤드라인']}")
    if retention:
        parts.append(f"유지: {retention['첫주미션']}")
    return " | ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Run research -> business -> x -> landing -> retention full funnel pipeline.")
    parser.add_argument("input", help="Path to research draft text file")
    parser.add_argument("--business-count", type=int, default=3)
    parser.add_argument("--x-count", type=int, default=3)
    parser.add_argument("--landing-count", type=int, default=3)
    parser.add_argument("--retention-count", type=int, default=3)
    parser.add_argument("--project", help="Optional project slug for dated output folders")
    parser.add_argument("--preset", choices=["ordinarybiz", "bootcamp", "vip", "ailit", "youtube", "x-article"], default="ordinarybiz", help="Style preset for summaries and final outputs")
    parser.add_argument("--selection-mode", choices=["generator", "reward"], default="generator", help="Best summary selection mode")
    parser.add_argument("--all-business", action="store_true", help="Generate downstream outputs for every business variant instead of only top-ranked one")
    parser.add_argument("--save", action="store_true", help="Save intermediate and final outputs")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    research_text = input_path.read_text(encoding="utf-8")

    business_variants = research_to_business_variants(research_text, count=args.business_count, preset=args.preset)
    selected_business = business_variants if args.all_business else [business_variants[0]]

    funnel_results = []
    for business in selected_business:
        strategy_text = strategy_text_from_business(business)
        x_variants = business_to_x_variants(strategy_text, count=args.x_count, preset=args.preset)
        landing_variants = business_to_landing_variants(strategy_text, count=args.landing_count, preset=args.preset)
        retention_variants = business_to_retention_variants(strategy_text, count=args.retention_count, preset=args.preset)
        funnel_results.append(
            {
                "source_business_rank": business["rank"],
                "source_business_variant": business["variant"],
                "strategy": business,
                "x_variants": x_variants,
                "landing_variants": landing_variants,
                "retention_variants": retention_variants,
            }
        )

    funnel_results = attach_reward_replay_to_funnel_results(research_text, funnel_results, preset=args.preset)

    saved = {}
    generator_best_summary = apply_preset_to_best(
        build_best_summary(research_text, business_variants, funnel_results, preset=args.preset, selection_mode="generator"),
        args.preset,
    )
    reward_best_summary = apply_preset_to_best(
        build_best_summary(research_text, business_variants, funnel_results, preset=args.preset, selection_mode="reward"),
        args.preset,
    )
    best_summary = reward_best_summary if args.selection_mode == "reward" else generator_best_summary
    if args.save:
        stem = input_path.stem
        date_folder = datetime.now().strftime("%Y-%m-%d")
        project_folder = args.project or stem
        base_dir = Path("outputs") / date_folder / project_folder
        business_dir = base_dir / "business"
        x_dir = base_dir / "x"
        landing_dir = base_dir / "landing"
        retention_dir = base_dir / "retention"
        summary_dir = base_dir / "summary"

        business_text, business_json = save_business_variants(business_variants, business_dir, stem + "-from-research")
        saved["business_text"] = str(business_text)
        saved["business_json"] = str(business_json)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for item in funnel_results:
            base_stem = f"{stem}-business-rank{item['source_business_rank']}-{timestamp}"
            x_text, x_json = save_x_variants(item["x_variants"], x_dir, base_stem)
            landing_text, landing_json = save_landing_variants(item["landing_variants"], landing_dir, base_stem)
            retention_text, retention_json = save_retention_variants(item["retention_variants"], retention_dir, base_stem)
            item["saved_text_x"] = str(x_text)
            item["saved_json_x"] = str(x_json)
            item["saved_text_landing"] = str(landing_text)
            item["saved_json_landing"] = str(landing_json)
            item["saved_text_retention"] = str(retention_text)
            item["saved_json_retention"] = str(retention_json)

        summary_dir.mkdir(parents=True, exist_ok=True)
        best_text = summary_dir / f"{stem}-best-{timestamp}.md"
        best_json = summary_dir / f"{stem}-best-{timestamp}.json"
        report_text = summary_dir / f"{stem}-report-{timestamp}.md"
        quality_text = summary_dir / f"{stem}-quality-comparison-{timestamp}.md"
        final_text = summary_dir / f"{stem}-final-{timestamp}.md"
        final_json = summary_dir / f"{stem}-final-{timestamp}.json"
        one_line_text = summary_dir / f"{stem}-one-line-{timestamp}.txt"
        best_text.write_text(render_best_summary(best_summary), encoding="utf-8")
        best_json.write_text(json.dumps(best_summary, ensure_ascii=False, indent=2), encoding="utf-8")
        report_text.write_text(render_execution_report(stem, business_variants, funnel_results, preset=args.preset, best=best_summary), encoding="utf-8")
        quality_text.write_text(render_quality_comparison_report(stem, generator_best_summary, reward_best_summary, preset=args.preset), encoding="utf-8")
        final_text.write_text(render_final_output(best_summary, preset=args.preset), encoding="utf-8")
        final_json.write_text(json.dumps(best_summary, ensure_ascii=False, indent=2), encoding="utf-8")
        one_line_text.write_text(render_one_line_summary(best_summary, preset=args.preset), encoding="utf-8")
        saved["best_text"] = str(best_text)
        saved["best_json"] = str(best_json)
        saved["report_text"] = str(report_text)
        saved["quality_text"] = str(quality_text)
        saved["final_text"] = str(final_text)
        saved["final_json"] = str(final_json)
        saved["one_line_text"] = str(one_line_text)

    if args.json:
        print(json.dumps({"business_variants": business_variants, "funnel_results": funnel_results, "best_summary": best_summary, "saved": saved}, ensure_ascii=False, indent=2))
        return

    print("=== BUSINESS VARIANTS ===")
    print(render_business_variants(business_variants))
    print()
    for item in funnel_results:
        rank = item["source_business_rank"]
        print(f"=== X VARIANTS FROM BUSINESS RANK {rank} ===")
        print(render_x_variants(item["x_variants"]))
        print()
        print(f"=== LANDING VARIANTS FROM BUSINESS RANK {rank} ===")
        print(render_landing_variants(item["landing_variants"]))
        print()
        print(f"=== RETENTION VARIANTS FROM BUSINESS RANK {rank} ===")
        print(render_retention_variants(item["retention_variants"]))
        if args.save:
            print(f"saved_text_x={item['saved_text_x']}")
            print(f"saved_json_x={item['saved_json_x']}")
            print(f"saved_text_landing={item['saved_text_landing']}")
            print(f"saved_json_landing={item['saved_json_landing']}")
            print(f"saved_text_retention={item['saved_text_retention']}")
            print(f"saved_json_retention={item['saved_json_retention']}")
        print()
    if args.save:
        print(f"saved_business_text={saved['business_text']}")
        print(f"saved_business_json={saved['business_json']}")
        print(f"saved_best_text={saved['best_text']}")
        print(f"saved_best_json={saved['best_json']}")
        print(f"saved_report_text={saved['report_text']}")
        print(f"saved_quality_text={saved['quality_text']}")
        print(f"saved_final_text={saved['final_text']}")
        print(f"saved_final_json={saved['final_json']}")
        print(f"saved_one_line_text={saved['one_line_text']}")


if __name__ == "__main__":
    main()
