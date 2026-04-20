import json
import subprocess
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')


def main():
    proc = subprocess.run(
        ['python', str(ROOT / 'extract_feedback_hints.py')],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)

    lines = ['# Adjustment Draft']
    preset_usage = data.get('preset_usage', {})
    if preset_usage:
        lines += ['\n## Preset Usage']
        for preset, count in preset_usage.items():
            lines.append(f'- {preset}: {count}')

    chosen_ranks = data.get('chosen_ranks', {})
    if chosen_ranks:
        lines += ['\n## Rank Preference']
        for key, ranks in chosen_ranks.items():
            top_rank = sorted(ranks.items(), key=lambda kv: int(kv[1]), reverse=True)[0][0] if ranks else 'n/a'
            lines.append(f'- {key}: rank {top_rank} 선택 빈도가 가장 높음')

    strengthen = data.get('top_strengthen_hints', [])
    penalize = data.get('top_penalize_hints', [])

    lines += ['\n## Suggested Score/Preset Adjustments']
    if strengthen:
        for text, count in strengthen[:5]:
            lines.append(f'- 강화 후보: {text} ({count}회)')
    else:
        lines.append('- 강화 후보: 아직 데이터 부족')

    if penalize:
        for text, count in penalize[:5]:
            lines.append(f'- 감점 후보: {text} ({count}회)')
    else:
        lines.append('- 감점 후보: 아직 데이터 부족')

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
