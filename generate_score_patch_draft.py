import json
import subprocess
from pathlib import Path

from generate_score_patch_v4a import collect_patch_entries

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')



def main():
    proc = subprocess.run(
        ['python', str(ROOT / 'extract_feedback_hints.py')],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    print(build_markdown_draft(data))



def build_markdown_draft(data: dict) -> str:
    chosen_ranks = data.get('chosen_ranks', {})
    lines = ['# Score Patch Draft']
    lines += ['\n## Rank Bias']
    for key, ranks in chosen_ranks.items():
        if ranks:
            top_rank, top_count = sorted(ranks.items(), key=lambda kv: int(kv[1]), reverse=True)[0]
            lines.append(f'- {key}: rank {top_rank} 선택 빈도 {top_count}회 → 상위 rank 가산 유지 검토')
        else:
            lines.append(f'- {key}: 데이터 부족')

    entries = collect_patch_entries(data)
    lines += ['\n## Concrete Patch Targets']
    if not entries:
        lines.append('- 아직 강화 데이터 부족')
        return '\n'.join(lines)

    for entry in entries:
        lines.append(f"\n### {entry['intent']} | {entry['phrase']}")
        lines.append(f"- 파일: {entry['file']}")
        lines.append(f"- 카테고리: {entry['category']}")
        lines.append(f"- 빈도: {entry['count']}회")
        rule = entry['rule']
        if rule:
            lines.append(f"- 이유: {rule['comment']}")
            lines.append('- suggested_old:')
            lines.extend(f'  {row}' for row in rule['old'].strip().splitlines())
            lines.append('- suggested_new:')
            lines.extend(f'  {row}' for row in rule['new'].strip().splitlines())
        if entry['weight_old'] and entry['weight_new']:
            lines.append('- weight_old:')
            lines.extend(f'  {row}' for row in entry['weight_old'].strip().splitlines())
            lines.append('- weight_new:')
            lines.extend(f'  {row}' for row in entry['weight_new'].strip().splitlines())
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
