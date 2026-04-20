from __future__ import annotations

from pathlib import Path

from ops.paperclip_tinker_atropos_sync import (
    COMPANY_ID as DEFAULT_COMPANY_ID,
    DEFAULT_BASE_URL,
    fetch_company_issues,
    find_issue_for_payload,
    sync_issue,
)
from ops.promotion_eval_status import collect_promotion_eval_status
from ops.tinker_paperclip_sync import (
    build_feedback_triage_sync_payload,
    build_full_funnel_sync_payload,
    build_preset_sync_payload,
    build_promotion_eval_sync_payload,
)
from run_min_hermes_promotion_eval import run_all, save_summary_artifacts

DEFAULT_ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
PROMOTION_IDENTIFIER = 'TIN-24'


def format_metric(value: float) -> str:
    return f'{value:.4f}'.rstrip('0').rstrip('.')


def generate_promotion_eval_summary(root: Path = DEFAULT_ROOT) -> dict:
    summary = run_all(root)
    summary['summary_artifacts'] = save_summary_artifacts(root, summary)
    return summary


def build_sync_payloads(root: Path) -> list[dict]:
    return [
        build_feedback_triage_sync_payload(root),
        build_full_funnel_sync_payload(root),
        build_preset_sync_payload(root),
        build_promotion_eval_sync_payload(root),
    ]


def sync_tinker_cards(
    root: Path,
    base_url: str = DEFAULT_BASE_URL,
    company_id: str = DEFAULT_COMPANY_ID,
    dry_run: bool = False,
) -> dict:
    issues = fetch_company_issues(company_id, base_url)
    results = []
    for payload in build_sync_payloads(root):
        issue = find_issue_for_payload(issues, payload)
        if not issue:
            results.append(
                {
                    'identifier': payload['identifier'],
                    'updated': False,
                    'reason': 'issue_not_found',
                    'status': payload['status'],
                }
            )
            continue
        if dry_run:
            results.append(
                {
                    'identifier': payload['identifier'],
                    'updated': False,
                    'reason': 'dry_run',
                    'status': payload['status'],
                    'issue_id': issue['id'],
                }
            )
            continue
        results.append(sync_issue(issue, payload, base_url))
    return {'company_id': company_id, 'root': str(root), 'results': results}


def build_daily_report(status_summary: dict, sync_results: list[dict]) -> str:
    benchmarks = status_summary.get('benchmarks') or {}
    v2 = benchmarks.get('v2') or {}
    v3 = benchmarks.get('v3') or {}
    promotion = next((item for item in sync_results if item.get('identifier') == PROMOTION_IDENTIFIER), None)

    lines = [
        'tinker-atropos-promotion-eval-daily',
        f"alert_count: {status_summary.get('alert_count')}",
        f"summary_pair_matched: {status_summary.get('summary_pair_matched')}",
        f"latest_summary_json_fresh: {status_summary.get('latest_summary_json_fresh')}",
        f"latest_summary_markdown_fresh: {status_summary.get('latest_summary_markdown_fresh')}",
        f"latest_summary_json: {status_summary.get('latest_summary_json')}",
        f"latest_summary_markdown: {status_summary.get('latest_summary_markdown')}",
        (
            'v2 current_policy: '
            f"lane_passed={v2.get('current_policy', {}).get('lane_passed')} "
            f"task_pass_count={v2.get('current_policy', {}).get('task_pass_count')} "
            f"mean_total={format_metric(v2.get('current_policy', {}).get('mean_total', 0.0))}"
        ),
        (
            'v2 patched_policy: '
            f"lane_passed={v2.get('patched_policy', {}).get('lane_passed')} "
            f"task_pass_count={v2.get('patched_policy', {}).get('task_pass_count')} "
            f"mean_total={format_metric(v2.get('patched_policy', {}).get('mean_total', 0.0))}"
        ),
        (
            'v3 current_policy: '
            f"lane_passed={v3.get('current_policy', {}).get('lane_passed')} "
            f"task_pass_count={v3.get('current_policy', {}).get('task_pass_count')} "
            f"mean_total={format_metric(v3.get('current_policy', {}).get('mean_total', 0.0))}"
        ),
        (
            'v3 patched_policy: '
            f"lane_passed={v3.get('patched_policy', {}).get('lane_passed')} "
            f"task_pass_count={v3.get('patched_policy', {}).get('task_pass_count')} "
            f"mean_total={format_metric(v3.get('patched_policy', {}).get('mean_total', 0.0))}"
        ),
    ]
    if promotion:
        lines.append(
            'paperclip promotion sync: '
            f"updated={promotion.get('updated')} status={promotion.get('status')} issue_id={promotion.get('issue_id')}"
        )
    else:
        lines.append('paperclip promotion sync: missing')
    return '\n'.join(lines)


def run_daily(
    root: Path = DEFAULT_ROOT,
    base_url: str = DEFAULT_BASE_URL,
    company_id: str = DEFAULT_COMPANY_ID,
    dry_run: bool = False,
) -> dict:
    root = Path(root)
    generate_promotion_eval_summary(root)
    sync = sync_tinker_cards(root, base_url=base_url, company_id=company_id, dry_run=dry_run)
    status_summary = collect_promotion_eval_status(root)
    report = build_daily_report(status_summary, sync['results'])
    return {
        'status_summary': status_summary,
        'sync': sync,
        'report': report,
    }
