from __future__ import annotations

from pathlib import Path

from ops.full_funnel_status import build_comment_body as build_full_funnel_comment, collect_full_funnel_status
from ops.preset_scoreboard import build_comment_body as build_preset_comment, collect_preset_scoreboard
from ops.promotion_eval_status import build_comment_body as build_promotion_eval_comment, collect_promotion_eval_status
from ops.review_patch_queue import build_comment_body as build_feedback_comment, summarize_patch_queue

FEEDBACK_TRIAGE_ISSUE_IDENTIFIER = 'TIN-18'
FULL_FUNNEL_ISSUE_IDENTIFIER = 'TIN-15'
PRESET_ISSUE_IDENTIFIER = 'TIN-16'
PROMOTION_EVAL_ISSUE_IDENTIFIER = 'TIN-24'

FEEDBACK_TRIAGE_ISSUE_TITLE = 'Daily Feedback Draft Triage'
FULL_FUNNEL_ISSUE_TITLE = 'Daily Full Funnel Reliability Check'
PRESET_ISSUE_TITLE = 'Daily Preset Performance Snapshot'
PROMOTION_EVAL_ISSUE_TITLE = 'Daily Promotion Evaluation Snapshot'


def determine_full_funnel_issue_status(summary: dict) -> str:
    return 'done' if summary.get('run_count', 0) > 0 and summary.get('alert_count', 0) == 0 else 'todo'


def determine_feedback_triage_issue_status(summary: dict) -> str:
    return 'done' if 'total_drafts' in summary and 'pending_review_count' in summary else 'todo'


def determine_preset_issue_status(summary: dict) -> str:
    totals = summary.get('totals') or {}
    return 'done' if summary.get('preset_count', 0) > 0 and totals.get('final_runs', 0) > 0 else 'todo'


def determine_promotion_eval_issue_status(summary: dict) -> str:
    benchmarks = summary.get('benchmarks') or {}
    v2 = benchmarks.get('v2') or {}
    v3 = benchmarks.get('v3') or {}
    if summary.get('benchmark_count', 0) < 2:
        return 'todo'
    if not summary.get('latest_summary_json') or not summary.get('latest_summary_markdown'):
        return 'todo'
    if not v2 or not v3:
        return 'todo'
    if not (v2.get('current_policy', {}).get('lane_passed') and v2.get('patched_policy', {}).get('lane_passed')):
        return 'todo'
    if v3.get('current_policy', {}).get('lane_passed'):
        return 'todo'
    if not v3.get('patched_policy', {}).get('lane_passed'):
        return 'todo'
    return 'done'


def build_full_funnel_sync_payload(root: Path) -> dict:
    summary = collect_full_funnel_status(root)
    return {
        'identifier': FULL_FUNNEL_ISSUE_IDENTIFIER,
        'title': FULL_FUNNEL_ISSUE_TITLE,
        'status': determine_full_funnel_issue_status(summary),
        'summary': summary,
        'comment': build_full_funnel_comment(summary),
    }


def build_feedback_triage_sync_payload(root: Path) -> dict:
    summary = summarize_patch_queue(root / 'feedback' / 'patch_drafts')
    return {
        'identifier': FEEDBACK_TRIAGE_ISSUE_IDENTIFIER,
        'title': FEEDBACK_TRIAGE_ISSUE_TITLE,
        'status': determine_feedback_triage_issue_status(summary),
        'summary': summary,
        'comment': build_feedback_comment(summary),
    }


def build_preset_sync_payload(root: Path) -> dict:
    summary = collect_preset_scoreboard(root)
    return {
        'identifier': PRESET_ISSUE_IDENTIFIER,
        'title': PRESET_ISSUE_TITLE,
        'status': determine_preset_issue_status(summary),
        'summary': summary,
        'comment': build_preset_comment(summary),
    }


def build_promotion_eval_sync_payload(root: Path) -> dict:
    summary = collect_promotion_eval_status(root)
    return {
        'identifier': PROMOTION_EVAL_ISSUE_IDENTIFIER,
        'title': PROMOTION_EVAL_ISSUE_TITLE,
        'status': determine_promotion_eval_issue_status(summary),
        'summary': summary,
        'comment': build_promotion_eval_comment(summary),
    }
