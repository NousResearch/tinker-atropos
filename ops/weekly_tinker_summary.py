from __future__ import annotations

from pathlib import Path

from ops.environment_status import collect_environment_status
from ops.full_funnel_status import collect_full_funnel_status
from ops.preset_scoreboard import collect_preset_scoreboard
from ops.review_patch_queue import summarize_patch_queue



def collect_weekly_summary(root: Path) -> dict:
    return {
        'environment': collect_environment_status(root),
        'full_funnel': collect_full_funnel_status(root),
        'preset_scoreboard': collect_preset_scoreboard(root),
        'patch_queue': summarize_patch_queue(root / 'feedback' / 'patch_drafts'),
    }



def build_markdown_summary(summary: dict) -> str:
    lines = ['# Weekly Tinker Research Summary']
    env = summary['environment']
    funnel = summary['full_funnel']
    presets = summary['preset_scoreboard']
    queue = summary['patch_queue']

    lines += [
        '',
        '## Environment',
        f"- environment_count: {env['environment_count']}",
        f"- alert_count: {env['alert_count']}",
        '',
        '## Full Funnel',
        f"- run_count: {funnel['run_count']}",
        f"- alert_count: {funnel['alert_count']}",
        '',
        '## Preset Scoreboard',
        f"- preset_count: {presets['preset_count']}",
        f"- final_runs: {presets['totals']['final_runs']}",
    ]
    for preset, item in sorted(presets['presets'].items()):
        lines.append(f"- {preset}: avg_landing_score={item['avg_landing_score']}, avg_x_score={item['avg_x_score']}")
    lines += [
        '',
        '## Patch Queue',
        f"- total_drafts: {queue['total_drafts']}",
        f"- pending_review_count: {queue['pending_review_count']}",
    ]
    if queue.get('top_review_candidate'):
        lines.append(f"- top_review_candidate: {queue['top_review_candidate']['draft_name']} ({queue['top_review_candidate']['status']})")
    else:
        lines.append('- top_review_candidate: none')
    return '\n'.join(lines)
