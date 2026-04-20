from __future__ import annotations

import json
import re
import time
from pathlib import Path

BENCHMARK_FILES = {
    'v2': 'research/min_hermes_offline_eval_v2_scoreboard.md',
    'v3': 'research/min_hermes_offline_eval_v3_scoreboard.md',
}
SUMMARY_FRESHNESS_SECONDS = 60 * 60 * 36

LANE_ROW_RE = re.compile(r'^\|\s*([^|]+?)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9]+/[0-9]+)\s*\|\s*(yes|no)\s*\|$')


def _parse_lane_summary(markdown_path: Path) -> dict[str, dict]:
    lines = markdown_path.read_text(encoding='utf-8').splitlines()
    lanes: dict[str, dict] = {}
    for line in lines:
        match = LANE_ROW_RE.match(line.strip())
        if not match:
            continue
        lane_name, mean_total, pass_rate, task_pass_count, lane_passed = match.groups()
        if lane_name == 'lane':
            continue
        lanes[lane_name] = {
            'mean_total': float(mean_total),
            'pass_rate': float(pass_rate),
            'task_pass_count': task_pass_count,
            'lane_passed': lane_passed == 'yes',
        }
    return lanes


def _find_latest_summary_artifact(root: Path, suffix: str) -> Path | None:
    files = sorted((root / 'outputs').glob(f'*/promotion-eval/summary/*.{suffix}'))
    if not files:
        return None
    return max(files, key=lambda item: item.stat().st_mtime)



def _age_seconds(path: Path | None) -> float | None:
    if not path or not path.exists():
        return None
    return max(0.0, time.time() - path.stat().st_mtime)



def _stem_without_suffix(path: Path | None) -> str | None:
    if not path:
        return None
    return path.stem



def collect_promotion_eval_status(root: Path) -> dict:
    benchmarks: dict[str, dict] = {}
    alerts: list[str] = []
    for benchmark_name, rel_path in BENCHMARK_FILES.items():
        path = root / rel_path
        if not path.exists():
            alerts.append(f'missing_benchmark:{benchmark_name}')
            continue
        benchmarks[benchmark_name] = _parse_lane_summary(path)

    latest_summary_json = _find_latest_summary_artifact(root, 'json')
    latest_summary_markdown = _find_latest_summary_artifact(root, 'md')
    latest_summary_json_age_seconds = _age_seconds(latest_summary_json)
    latest_summary_markdown_age_seconds = _age_seconds(latest_summary_markdown)
    latest_summary_json_fresh = latest_summary_json_age_seconds is not None and latest_summary_json_age_seconds <= SUMMARY_FRESHNESS_SECONDS
    latest_summary_markdown_fresh = latest_summary_markdown_age_seconds is not None and latest_summary_markdown_age_seconds <= SUMMARY_FRESHNESS_SECONDS
    summary_pair_matched = (
        latest_summary_json is not None
        and latest_summary_markdown is not None
        and _stem_without_suffix(latest_summary_json) == _stem_without_suffix(latest_summary_markdown)
    )

    if latest_summary_json is None:
        alerts.append('missing_summary_json')
    elif not latest_summary_json_fresh:
        alerts.append('stale_summary_json')
    if latest_summary_markdown is None:
        alerts.append('missing_summary_markdown')
    elif not latest_summary_markdown_fresh:
        alerts.append('stale_summary_markdown')
    if latest_summary_json is not None and latest_summary_markdown is not None and not summary_pair_matched:
        alerts.append('summary_pair_mismatch')

    return {
        'benchmark_count': len(benchmarks),
        'benchmarks': benchmarks,
        'latest_summary_json': str(latest_summary_json) if latest_summary_json else None,
        'latest_summary_markdown': str(latest_summary_markdown) if latest_summary_markdown else None,
        'latest_summary_json_age_seconds': latest_summary_json_age_seconds,
        'latest_summary_markdown_age_seconds': latest_summary_markdown_age_seconds,
        'latest_summary_json_fresh': latest_summary_json_fresh,
        'latest_summary_markdown_fresh': latest_summary_markdown_fresh,
        'summary_pair_matched': summary_pair_matched,
        'alert_count': len(alerts),
        'alerts': alerts,
    }

def build_comment_body(summary: dict) -> str:
    lines = [
        f"benchmark_count: {summary['benchmark_count']}",
        f"alert_count: {summary.get('alert_count', 0)}",
        f"latest_summary_json: {summary.get('latest_summary_json')}",
        f"latest_summary_markdown: {summary.get('latest_summary_markdown')}",
        f"latest_summary_json_fresh: {summary.get('latest_summary_json_fresh')}",
        f"latest_summary_markdown_fresh: {summary.get('latest_summary_markdown_fresh')}",
        f"summary_pair_matched: {summary.get('summary_pair_matched')}",
        'alerts:',
    ]
    for alert in summary.get('alerts', []):
        lines.append(f'- {alert}')
    lines.append('benchmarks:')
    for benchmark_name, lanes in sorted(summary.get('benchmarks', {}).items()):
        lines.append(f'- {benchmark_name}:')
        for lane_name, lane in lanes.items():
            lines.append(
                f"  - {lane_name} mean_total={lane['mean_total']:.4f}, task_pass_count={lane['task_pass_count']}, lane_passed={'yes' if lane['lane_passed'] else 'no'}"
            )
    return '\n'.join(lines)


if __name__ == '__main__':
    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    print(json.dumps(collect_promotion_eval_status(root), ensure_ascii=False, indent=2))
