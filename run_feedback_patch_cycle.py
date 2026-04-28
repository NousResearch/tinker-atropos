import argparse
import subprocess
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
PATCH_COMMANDS = [
    'extract_feedback_hints.py',
    'generate_preset_score_draft.py',
    'generate_score_patch_draft.py',
    'generate_score_patch_file_draft.py',
    'generate_score_patch_v4a.py',
]
OPTIONAL_MEMO_LABELS = {'채널 메모'}


def iter_check_lines(metrics_path: Path):
    lines = metrics_path.read_text(encoding='utf-8').splitlines()
    current = None
    for line in lines:
        stripped = line.strip()
        if stripped == '## 실측 입력':
            current = 'metrics'
            continue
        if stripped == '## 운영 메모':
            current = 'memo'
            continue
        if stripped.startswith('## '):
            current = None
            continue
        if current and stripped.startswith('- '):
            yield current, stripped[2:]


def find_missing_entries(metrics_path: Path) -> list[str]:
    missing = []
    for section, item in iter_check_lines(metrics_path):
        label, _, value = item.partition(':')
        if not _:
            continue
        if value.strip():
            continue
        if section == 'memo' and label.strip() in OPTIONAL_MEMO_LABELS:
            continue
        missing.append(label.strip())
    return missing


def collect_feedback_status(root: Path, date: str) -> list[dict]:
    base = root / 'feedback' / date
    rows = []
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        metrics_path = folder / 'metrics.md'
        missing = find_missing_entries(metrics_path)
        rows.append(
            {
                'project': folder.name,
                'metrics_path': str(metrics_path),
                'missing': missing,
                'ready': not missing,
            }
        )
    return rows


def run_patch_cycle(root: Path, date: str):
    status = collect_feedback_status(root, date)
    blocked = [row for row in status if not row['ready']]
    if blocked:
        details = ', '.join(f"{row['project']}: {', '.join(row['missing'])}" for row in blocked)
        raise RuntimeError(f'실측 입력이 비어 있어 실행을 중단함: {details}')

    for script_name in PATCH_COMMANDS:
        subprocess.run(['python', str(root / script_name)], check=True, cwd=root)
    return status


def render_status(status: list[dict]) -> str:
    lines = ['# Feedback Patch Cycle Status']
    for row in status:
        marker = 'ready' if row['ready'] else 'blocked'
        lines.append(f"- {row['project']}: {marker}")
        if row['missing']:
            lines.append(f"  - missing: {', '.join(row['missing'])}")
        lines.append(f"  - metrics: {row['metrics_path']}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Check feedback metrics readiness and optionally run the patch cycle.')
    parser.add_argument('--date', default='2026-04-17')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()

    if args.run:
        status = run_patch_cycle(ROOT, args.date)
    else:
        status = collect_feedback_status(ROOT, args.date)
    print(render_status(status))


if __name__ == '__main__':
    main()
