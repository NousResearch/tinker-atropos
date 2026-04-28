import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos/feedback')


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def read_lines(path: Path, marker: str):
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    out = []
    capture = False
    for line in lines:
        if line.strip().startswith(marker):
            capture = True
            continue
        if capture and line.startswith('## '):
            break
        if capture and line.strip().startswith('- '):
            out.append(line.strip()[2:])
    return out


def main():
    preset_counter = Counter()
    chosen_rank_counter = defaultdict(Counter)
    strengthen = Counter()
    penalize = Counter()

    for selected in ROOT.glob('*/**/selected_variant.json'):
        data = read_json(selected)
        if not data:
            continue
        preset = data.get('preset', 'unknown')
        preset_counter[preset] += 1
        for key in ['chosen_business_rank', 'chosen_x_rank', 'chosen_landing_rank', 'chosen_retention_rank']:
            if key in data:
                chosen_rank_counter[key][str(data[key])] += 1

        lessons = selected.parent / 'lessons.md'
        for item in read_lines(lessons, '## 다음 번 자동 생성에서 강화할 포인트'):
            strengthen[item] += 1
        for item in read_lines(lessons, '## 다음 번 자동 생성에서 감점할 포인트'):
            penalize[item] += 1

    summary = {
        'preset_usage': dict(preset_counter),
        'chosen_ranks': {k: dict(v) for k, v in chosen_rank_counter.items()},
        'top_strengthen_hints': strengthen.most_common(10),
        'top_penalize_hints': penalize.most_common(10),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
