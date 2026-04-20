from __future__ import annotations

import json
from pathlib import Path

REQUIRED_SUFFIXES = ['best', 'final', 'report', 'one-line']
IGNORED_PROJECTS = {
    'default-public-ready',
}
LEGACY_ALLOWED_MISSING = {
    'ordinarybiz-opsummary': {'final', 'one-line'},
    'ordinarybiz-report': {'final', 'one-line'},
    'ordinarybiz-summary': {'final', 'one-line'},
    'ordinarybiz-summary2': {'final', 'one-line'},
    'ordinarybiz-quality2': {'final', 'one-line'},
    'ordinarybiz-quality3': {'final', 'one-line'},
    'ordinarybiz-quality4': {'final', 'one-line'},
    'ordinarybiz-quality5': {'final', 'one-line'},
    'ordinarybiz-quality6': {'one-line'},
    'ordinarybiz-quality7': {'one-line'},
    'ordinarybiz-quality8': {'one-line'},
}



def _find_latest_summary_dir(outputs_root: Path) -> list[Path]:
    if not outputs_root.exists():
        return []
    return sorted(outputs_root.glob('*/*/summary'))



def _match_latest(directory: Path, token: str) -> str | None:
    files = list(directory.glob(f'*-{token}-*.*'))
    if not files:
        return None
    latest = max(files, key=lambda item: item.stat().st_mtime)
    return str(latest)



def collect_full_funnel_status(root: Path) -> dict:
    outputs_root = root / 'outputs'
    summary_dirs = _find_latest_summary_dir(outputs_root)
    runs = []
    alerts = []
    for summary_dir in summary_dirs:
        project = summary_dir.parent.name
        if project in IGNORED_PROJECTS:
            continue
        artifacts = {suffix: _match_latest(summary_dir, suffix) for suffix in REQUIRED_SUFFIXES}
        allowed_missing = sorted(LEGACY_ALLOWED_MISSING.get(project, set()))
        missing = [suffix for suffix, path in artifacts.items() if path is None and suffix not in LEGACY_ALLOWED_MISSING.get(project, set())]
        if missing:
            alerts.append(f'missing artifact in {project}: {", ".join(missing)}')
        runs.append(
            {
                'project': project,
                'summary_dir': str(summary_dir),
                'artifacts': artifacts,
                'missing_artifacts': missing,
                'allowed_missing_artifacts': allowed_missing,
                'latest_final': artifacts['final'],
                'latest_mtime': max((Path(path).stat().st_mtime for path in artifacts.values() if path), default=0),
            }
        )
    runs.sort(key=lambda item: item['latest_mtime'], reverse=True)
    latest_run = runs[0] if runs else None
    if latest_run:
        latest_run = {k: v for k, v in latest_run.items() if k != 'latest_mtime'}
    return {
        'run_count': len(runs),
        'alert_count': len(alerts),
        'alerts': alerts,
        'latest_run': latest_run,
        'runs': [{k: v for k, v in item.items() if k != 'latest_mtime'} for item in runs],
    }



def build_comment_body(summary: dict) -> str:
    lines = [
        f"run_count: {summary['run_count']}",
        f"alert_count: {summary['alert_count']}",
    ]
    latest = summary.get('latest_run')
    if latest:
        lines.append(f"latest_project: {latest['project']}")
        lines.append(f"latest_final: {latest['latest_final']}")
    lines.append('alerts:')
    if summary['alerts']:
        lines.extend(f'- {item}' for item in summary['alerts'])
    else:
        lines.append('- none')
    return '\n'.join(lines)


if __name__ == '__main__':
    summary = collect_full_funnel_status(Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos'))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
