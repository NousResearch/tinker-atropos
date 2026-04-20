import argparse
from pathlib import Path

from run_feedback_patch_cycle import OPTIONAL_MEMO_LABELS, iter_check_lines

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')


def collect_missing_lines(metrics_path: Path) -> list[str]:
    missing = []
    for section, item in iter_check_lines(metrics_path):
        label, sep, value = item.partition(':')
        if not sep:
            continue
        if value.strip() or value.strip() == '미집계':
            continue
        if section == 'memo' and label.strip() in OPTIONAL_MEMO_LABELS:
            continue
        missing.append(f'- {label.strip()}:')
    return missing


def build_missing_form_text(root: Path, date: str) -> str:
    base = root / 'feedback' / date
    lines = [
        f'# Feedback missing-only form {date}',
        '',
        '이 폼은 아직 비어 있는 칸만 모아둔 초간단 복붙 폼이다.',
        '',
    ]
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        metrics_path = folder / 'metrics.md'
        missing = collect_missing_lines(metrics_path)
        if not missing:
            continue
        lines.append(f'## {folder.name}')
        lines.extend(missing)
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description='Print a compact form containing only missing feedback fields.')
    parser.add_argument('--date', default='2026-04-17')
    args = parser.parse_args()
    print(build_missing_form_text(ROOT, args.date), end='')


if __name__ == '__main__':
    main()
