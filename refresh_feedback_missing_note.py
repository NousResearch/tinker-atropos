import argparse
from pathlib import Path

from print_feedback_missing_form import build_missing_form_text

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
DEFAULT_OUTPUT = Path('/Users/heomin/Obsidian Vault/Tinker-Atropos 2026-04-17 실측 feedback 초간단 복붙 폼.md')


def build_note_text(root: Path, date: str) -> str:
    missing_form = build_missing_form_text(root=root, date=date).strip()
    return (
        f'# Tinker-Atropos {date} 실측 feedback 초간단 복붙 폼\n\n'
        '작성 목적: 아직 비어 있는 칸만 모아 빠르게 복붙 입력하기 위한 최소 폼이다.\n\n'
        '관련 노트\n'
        f'- [[Tinker-Atropos {date} 전체 진행상황 종합 보고]]\n'
        f'- [[Tinker-Atropos {date} 실측 feedback 데이터 출처 맵]]\n'
        f'- [[Tinker-Atropos {date} 실측 feedback 입력용 한 장 체크리스트]]\n'
        f'- [[Tinker-Atropos {date} 실측 feedback 일괄 입력 시트]]\n\n'
        '사용 순서\n'
        '1. 아래 빈칸만 채운다.\n'
        '2. 값이 없으면 `미집계` 로 적는다.\n'
        '3. 채운 값을 일괄 입력 시트나 각 `metrics.md` 에 반영한다.\n'
        '4. 반영 후 아래 명령으로 점검하고 실행한다.\n\n'
        '```bash\n'
        'cd /Users/heomin/.hermes/hermes-agent/tinker-atropos\n'
        f'python refresh_feedback_missing_note.py --date {date}\n'
        f'python run_feedback_patch_cycle.py --date {date}\n'
        f'python run_feedback_patch_cycle.py --date {date} --run\n'
        '```\n\n'
        f'{missing_form}\n'
    )


def write_note(root: Path, date: str, output_path: Path):
    output_path.write_text(build_note_text(root=root, date=date), encoding='utf-8')
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Refresh the Obsidian missing-only feedback form note.')
    parser.add_argument('--date', default='2026-04-17')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    out = write_note(root=ROOT, date=args.date, output_path=Path(args.output))
    print(out)


if __name__ == '__main__':
    main()
