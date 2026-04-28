#!/usr/bin/env python3
"""Evaluator for the Tinker-Atropos quality-first default setup research mission.

The evaluator scores a structured research deliverable instead of executing long
training runs. This keeps the autoresearch loop cheap while still producing a
machine-checkable comparison artifact.
"""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_REPORT = REPO_ROOT / "research" / "tinker_quality_first_default.json"
MD_REPORT = REPO_ROOT / "research" / "tinker_quality_first_default.md"


def add_reason(reasons: list[str], condition: bool, message: str, points: int, score: int) -> int:
    if condition:
        reasons.append(f"+{points}: {message}")
        return score + points
    reasons.append(f"+0: missing {message}")
    return score


def load_json_report() -> tuple[dict, list[str]]:
    reasons: list[str] = []
    if not JSON_REPORT.exists():
        reasons.append(f"JSON report missing: {JSON_REPORT.relative_to(REPO_ROOT)}")
        return {}, reasons
    try:
        data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        reasons.append(f"JSON report is invalid: {exc}")
        return {}, reasons
    if not isinstance(data, dict):
        reasons.append("JSON report must be an object")
        return {}, reasons
    return data, reasons


def config_exists(config_path: str) -> bool:
    if not config_path:
        return False
    return (REPO_ROOT / config_path).exists()


def main() -> None:
    score = 0
    reasons: list[str] = []
    report, preload_reasons = load_json_report()
    reasons.extend(preload_reasons)

    score = add_reason(
        reasons,
        MD_REPORT.exists(),
        f"markdown report exists at {MD_REPORT.relative_to(REPO_ROOT)}",
        10,
        score,
    )
    score = add_reason(
        reasons,
        bool(report),
        f"json report exists at {JSON_REPORT.relative_to(REPO_ROOT)}",
        10,
        score,
    )

    candidates = report.get("candidate_setups")
    valid_candidate_count = isinstance(candidates, list) and 2 <= len(candidates) <= 3
    score = add_reason(
        reasons,
        valid_candidate_count,
        "candidate_setups has 2-3 entries",
        20,
        score,
    )

    candidate_names: list[str] = []
    if isinstance(candidates, list):
        all_candidate_fields = True
        all_candidate_paths = True
        for candidate in candidates:
            if not isinstance(candidate, dict):
                all_candidate_fields = False
                all_candidate_paths = False
                continue
            name = candidate.get("name")
            config_path = candidate.get("config_path")
            candidate_names.append(name if isinstance(name, str) else "")
            required = [
                isinstance(name, str) and bool(name.strip()),
                isinstance(config_path, str) and bool(config_path.strip()),
                isinstance(candidate.get("quality_summary"), str) and bool(candidate["quality_summary"].strip()),
                isinstance(candidate.get("cost_note"), str) and bool(candidate["cost_note"].strip()),
                isinstance(candidate.get("beginner_repeatability"), str)
                and bool(candidate["beginner_repeatability"].strip()),
            ]
            if not all(required):
                all_candidate_fields = False
            if not (isinstance(config_path, str) and config_exists(config_path)):
                all_candidate_paths = False
        score = add_reason(reasons, all_candidate_fields, "every candidate includes required fields", 15, score)
        score = add_reason(reasons, all_candidate_paths, "every candidate points to an existing config path", 10, score)
    else:
        reasons.append("+0: candidate_setups missing or not a list")

    recommended = report.get("recommended_default")
    recommended_name = None
    recommendation_valid = False
    if isinstance(recommended, dict):
        recommended_name = recommended.get("name")
        recommended_config = recommended.get("config_path")
        recommendation_valid = (
            isinstance(recommended_name, str)
            and recommended_name in candidate_names
            and isinstance(recommended_config, str)
            and config_exists(recommended_config)
        )
    score = add_reason(
        reasons,
        recommendation_valid,
        "recommended_default matches one of the compared candidates",
        15,
        score,
    )

    rationale = report.get("selection_rationale")
    rationale_text = rationale.lower() if isinstance(rationale, str) else ""
    rationale_has_quality = "quality" in rationale_text or "품질" in rationale_text
    rationale_has_repeatability = (
        "repeat" in rationale_text
        or "beginner" in rationale_text
        or "초보" in rationale_text
        or "반복" in rationale_text
    )
    score = add_reason(
        reasons,
        isinstance(rationale, str) and bool(rationale.strip()),
        "selection_rationale is present",
        5,
        score,
    )
    score = add_reason(
        reasons,
        rationale_has_quality and rationale_has_repeatability,
        "selection_rationale mentions quality and beginner repeatability",
        5,
        score,
    )

    excluded = report.get("excluded_options")
    score = add_reason(
        reasons,
        isinstance(excluded, list) and len(excluded) >= 1,
        "excluded_options explains what was intentionally left out",
        5,
        score,
    )

    validation_plan = report.get("next_step_validation_plan")
    score = add_reason(
        reasons,
        isinstance(validation_plan, list) and len(validation_plan) >= 2,
        "next_step_validation_plan has at least two concrete follow-ups",
        5,
        score,
    )

    result = {
        "pass": True,
        "score": score,
        "report_path": str(JSON_REPORT.relative_to(REPO_ROOT)),
        "reasons": reasons,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
