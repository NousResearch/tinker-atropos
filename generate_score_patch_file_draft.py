import json
import subprocess
from datetime import datetime
from pathlib import Path

from generate_score_patch_v4a import collect_patch_entries

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
OUT_DIR = ROOT / 'feedback' / 'patch_drafts'



def get_hints():
    proc = subprocess.run(
        ['python', str(ROOT / 'extract_feedback_hints.py')],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)



def _append_block(lines: list[str], label: str, text: str):
    lines.append(f'      {label}: |')
    for row in text.strip().splitlines():
        lines.append(f'        {row}')



def build_patch_text(data: dict) -> str:
    lines = ['# Score Patch File Draft', '', 'suggested_changes:']
    entries = collect_patch_entries(data)
    if not entries:
        lines.append('  []')
        return '\n'.join(lines)

    for entry in entries:
        lines.append('  - file: "%s"' % entry['file'])
        lines.append('    category: "%s"' % entry['category'])
        lines.append('    intent: "%s"' % entry['intent'])
        lines.append('    phrase: "%s"' % entry['phrase'])
        lines.append('    count: %s' % entry['count'])
        rule = entry['rule']
        if rule:
            lines.append('    reason: "%s"' % rule['comment'])
            _append_block(lines, 'suggested_old', rule['old'])
            _append_block(lines, 'suggested_new', rule['new'])
        if entry['weight_old'] and entry['weight_new']:
            _append_block(lines, 'weight_old', entry['weight_old'])
            _append_block(lines, 'weight_new', entry['weight_new'])
    return '\n'.join(lines)



def main():
    data = get_hints()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = OUT_DIR / f'score-patch-draft-{stamp}.md'
    out.write_text(build_patch_text(data), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
