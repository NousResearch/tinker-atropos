from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class PatchEntry:
    old: str
    new: str
    source: str



def _collect_block(lines: list[str], start_index: int, prefix: str) -> tuple[str, int]:
    line = lines[start_index]
    content = line.split(prefix, 1)[1].lstrip()
    block = [content] if content else []
    index = start_index + 1
    while index < len(lines):
        current = lines[index]
        if current.startswith('# ') or current.startswith('*** '):
            break
        block.append(current)
        index += 1
    return '\n'.join(block).strip(), index



def parse_patch_draft(path: Path) -> dict[str, list[PatchEntry]]:
    lines = path.read_text(encoding='utf-8').splitlines()
    current_file: str | None = None
    parsed: dict[str, list[PatchEntry]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith('*** Update File: '):
            current_file = line.split(': ', 1)[1].strip()
            parsed.setdefault(current_file, [])
            index += 1
            continue
        if current_file and line.startswith('# suggested_old:'):
            old_text, next_index = _collect_block(lines, index, '# suggested_old:')
            if next_index >= len(lines) or not lines[next_index].startswith('# suggested_new:'):
                raise ValueError(f'suggested_old without suggested_new near line {index + 1}')
            new_text, index = _collect_block(lines, next_index, '# suggested_new:')
            key = (current_file, 'suggested', old_text, new_text)
            if old_text and new_text and key not in seen:
                parsed[current_file].append(PatchEntry(old=old_text, new=new_text, source='suggested'))
                seen.add(key)
            continue
        if current_file and line.startswith('# weight_old:'):
            old_text, next_index = _collect_block(lines, index, '# weight_old:')
            if next_index >= len(lines) or not lines[next_index].startswith('# weight_new:'):
                raise ValueError(f'weight_old without weight_new near line {index + 1}')
            new_text, index = _collect_block(lines, next_index, '# weight_new:')
            key = (current_file, 'weight', old_text, new_text)
            if old_text and new_text and key not in seen:
                parsed[current_file].append(PatchEntry(old=old_text, new=new_text, source='weight'))
                seen.add(key)
            continue
        index += 1
    return parsed



def apply_entries_to_file(path: Path, entries: Iterable[PatchEntry]) -> dict[str, int]:
    original_text = path.read_text(encoding='utf-8')
    text = original_text
    applied = 0
    skipped = 0
    for entry in entries:
        if entry.old in text:
            text = text.replace(entry.old, entry.new, 1)
            applied += 1
        else:
            skipped += 1
    changed = int(text != original_text)
    path.write_text(text, encoding='utf-8')
    return {'applied': applied, 'skipped': skipped, 'changed': changed}



def apply_patch_draft(path: Path, root: Path | None = None) -> dict[str, dict[str, int]]:
    parsed = parse_patch_draft(path)
    results: dict[str, dict[str, int]] = {}
    for raw_target, entries in parsed.items():
        target = Path(raw_target)
        if root and not target.is_absolute():
            target = root / target
        if not target.exists():
            results[str(target)] = {'applied': 0, 'skipped': len(entries), 'missing_file': 1}
            continue
        result = apply_entries_to_file(target, entries)
        result['missing_file'] = 0
        results[str(target)] = result
    return results



def main() -> None:
    parser = argparse.ArgumentParser(description='generated score patch draft 를 실제 파일에 적용한다.')
    parser.add_argument('patch_file')
    parser.add_argument('--root')
    args = parser.parse_args()

    results = apply_patch_draft(Path(args.patch_file), root=Path(args.root) if args.root else None)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
