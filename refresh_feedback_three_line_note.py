import argparse
from pathlib import Path

from run_feedback_patch_cycle import iter_check_lines, OPTIONAL_MEMO_LABELS

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
DEFAULT_OUTPUT = Path('/Users/heomin/Obsidian Vault/Tinker-Atropos 2026-04-17 실측 feedback 남은 빈칸 세 줄 요약.md')


def collect_missing_by_section(metrics_path: Path) -> tuple[list[str], list[str]]:
    metrics_missing = []
    memo_missing = []
    for section, item in iter_check_lines(metrics_path):
        label, sep, value = item.partition(':')
        if not sep:
            continue
        if value.strip() or value.strip() == '미집계':
            continue
        clean = label.strip()
        if section == 'memo':
            if clean in OPTIONAL_MEMO_LABELS:
                continue
            memo_missing.append(clean)
        else:
            metrics_missing.append(clean)
    return metrics_missing, memo_missing


def build_note_text(root: Path, date: str) -> str:
    base = root / 'feedback' / date
    lines = [
        f'# Tinker-Atropos {date} 실측 feedback 남은 빈칸 세 줄 요약',
        '',
        '작성 목적: 지금 남아 있는 입력 칸을 프로젝트별 세 줄로만 빠르게 보는 요약판이다.',
        '',
        '관련 노트',
        f'- [[Tinker-Atropos {date} 전체 진행상황 종합 보고]]',
        f'- [[Tinker-Atropos {date} 실측 feedback 초간단 복붙 폼]]',
        f'- [[Tinker-Atropos {date} 실측 feedback 일괄 입력 시트]]',
        '',
    ]
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        metrics_missing, memo_missing = collect_missing_by_section(folder / 'metrics.md')
        lines.append(f'## {folder.name}')
        lines.append('- 실측: ' + (', '.join(metrics_missing) if metrics_missing else '없음'))
        lines.append('- 운영: ' + (', '.join(memo_missing) if memo_missing else '없음'))
        lines.append(f'- 입력판: [[Tinker-Atropos {date} 실측 feedback 초간단 복붙 폼]]')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def write_note(root: Path, date: str, output_path: Path):
    output_path.write_text(build_note_text(root=root, date=date), encoding='utf-8')
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Refresh the three-line summary note for remaining feedback blanks.')
    parser.add_argument('--date', default='2026-04-17')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    out = write_note(root=ROOT, date=args.date, output_path=Path(args.output))
    print(out)


if __name__ == '__main__':
    main()
