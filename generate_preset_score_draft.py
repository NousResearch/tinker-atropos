import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
FEEDBACK = ROOT / 'feedback'

PRESET_TARGETS = {
    'ordinarybiz': ['landing.headline_strength', 'x.action_clarity'],
    'bootcamp': ['landing.brevity', 'retention.checkin_strength'],
    'vip': ['landing.headline_strength', 'retention.checkin_strength'],
    'ailit': ['landing.cta_strength', 'retention.retention_strength'],
    'youtube': ['x.action_clarity', 'landing.headline_strength'],
    'x-article': ['x.body_brevity', 'landing.headline_strength'],
}


def load_feedback():
    items = []
    for selected in FEEDBACK.glob('*/**/selected_variant.json'):
        try:
            data = json.loads(selected.read_text(encoding='utf-8'))
        except Exception:
            continue
        lessons = selected.parent / 'lessons.md'
        text = lessons.read_text(encoding='utf-8') if lessons.exists() else ''
        items.append((data, text))
    return items


def main():
    grouped = defaultdict(list)
    for data, lessons in load_feedback():
        preset = data.get('preset', 'ordinarybiz')
        grouped[preset].append((data, lessons))

    lines = ['# Preset Score Draft']
    for preset, rows in sorted(grouped.items()):
        lines += [f'\n## {preset}']
        lines.append(f'- samples: {len(rows)}')
        targets = PRESET_TARGETS.get(preset, [])
        if targets:
            lines.append(f'- suggested_targets: {", ".join(targets)}')
        strengthen = Counter()
        penalize = Counter()
        for _data, lessons in rows:
            current = None
            for raw in lessons.splitlines():
                line = raw.strip()
                if line.startswith('## 다음 번 자동 생성에서 강화할 포인트'):
                    current = 'up'
                    continue
                if line.startswith('## 다음 번 자동 생성에서 감점할 포인트'):
                    current = 'down'
                    continue
                if line.startswith('## '):
                    current = None
                    continue
                if current == 'up' and line.startswith('- '):
                    strengthen[line[2:]] += 1
                if current == 'down' and line.startswith('- '):
                    penalize[line[2:]] += 1
        if strengthen:
            lines.append('- strengthen_hints:')
            for text, count in strengthen.most_common(3):
                lines.append(f'  - {text} ({count})')
        if penalize:
            lines.append('- penalize_hints:')
            for text, count in penalize.most_common(3):
                lines.append(f'  - {text} ({count})')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
