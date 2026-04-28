from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.apply_patch_draft import parse_patch_draft


STAMP_RE = re.compile(r'(\d{8}-\d{6})')



def _entry_status(text: str, entry) -> str:
    old_in = entry.old in text
    new_in = entry.new in text
    if new_in and not old_in:
        return 'applied'
    if old_in and not new_in:
        return 'pending'
    if not old_in and not new_in:
        return 'stale'
    return 'ambiguous'



def _status_for_entries(target: Path, entries) -> dict[str, int | str]:
    if not target.exists():
        return {'target_status': 'missing_file', 'applied': 0, 'pending': 0, 'stale': 0, 'ambiguous': 0}
    text = target.read_text(encoding='utf-8')
    counts = {'applied': 0, 'pending': 0, 'stale': 0, 'ambiguous': 0}
    total = len(entries)
    if total == 0:
        return {'target_status': 'empty', **counts}
    for entry in entries:
        counts[_entry_status(text, entry)] += 1
    if counts['pending'] > 0:
        target_status = 'partial' if counts['applied'] > 0 or counts['stale'] > 0 or counts['ambiguous'] > 0 else 'pending'
    elif counts['stale'] > 0:
        target_status = 'stale_partial' if counts['applied'] > 0 else 'stale'
    elif counts['ambiguous'] > 0:
        target_status = 'partial' if counts['applied'] > 0 else 'pending'
    else:
        target_status = 'applied'
    return {'target_status': target_status, **counts}



def summarize_patch_queue(drafts_dir: Path) -> dict:
    items = []
    for patch_file in drafts_dir.glob('score-patch-v4a-*.patch'):
        parsed = parse_patch_draft(patch_file)
        total_entries = sum(len(entries) for entries in parsed.values())
        applied_entries = 0
        pending_entries = 0
        stale_entries = 0
        ambiguous_entries = 0
        statuses = []
        targets = []
        for raw_target, entries in parsed.items():
            target = Path(raw_target)
            target_result = _status_for_entries(target, entries)
            statuses.append(target_result['target_status'])
            applied_entries += int(target_result['applied'])
            pending_entries += int(target_result['pending'])
            stale_entries += int(target_result['stale'])
            ambiguous_entries += int(target_result['ambiguous'])
            targets.append(str(target))
        if 'missing_file' in statuses:
            status = 'missing_file'
        elif total_entries == 0:
            status = 'empty'
        elif pending_entries > 0:
            status = 'partial' if applied_entries > 0 or stale_entries > 0 or ambiguous_entries > 0 else 'pending'
        elif stale_entries > 0:
            status = 'stale_partial' if applied_entries > 0 else 'stale'
        elif ambiguous_entries > 0:
            status = 'partial' if applied_entries > 0 else 'pending'
        else:
            status = 'applied'
        stamp_match = STAMP_RE.search(patch_file.name)
        stamp = stamp_match.group(1) if stamp_match else ''
        items.append(
            {
                'draft_name': patch_file.name,
                'draft_path': str(patch_file),
                'stamp': stamp,
                'status': status,
                'total_entries': total_entries,
                'applied_entries': applied_entries,
                'pending_entries': pending_entries,
                'stale_entries': stale_entries,
                'ambiguous_entries': ambiguous_entries,
                'targets': targets,
                'targets_key': tuple(sorted(targets)),
            }
        )
    items.sort(key=lambda item: item['stamp'], reverse=True)

    seen_target_sets: set[tuple[str, ...]] = set()
    for item in items:
        if item['targets_key'] in seen_target_sets and item['status'] in {'pending', 'partial', 'stale_partial', 'stale'}:
            item['status'] = 'superseded'
        seen_target_sets.add(item['targets_key'])

    top_review_candidate = next((item for item in items if item['status'] in {'pending', 'partial', 'missing_file'}), None)
    pending_review_count = sum(1 for item in items if item['status'] in {'pending', 'partial', 'missing_file'})
    empty_draft_count = sum(1 for item in items if item['status'] == 'empty')
    stale_partial_count = sum(1 for item in items if item['status'] == 'stale_partial')
    for item in items:
        item.pop('targets_key', None)
    return {
        'total_drafts': len(items),
        'pending_review_count': pending_review_count,
        'empty_draft_count': empty_draft_count,
        'stale_partial_count': stale_partial_count,
        'top_review_candidate': top_review_candidate,
        'items': items,
    }



def archive_nonactionable_drafts(drafts_dir: Path, archive_dir: Path | None = None) -> dict:
    archive_dir = archive_dir or drafts_dir / 'archived'
    summary = summarize_patch_queue(drafts_dir)

    def targets_key_from_item(item: dict) -> tuple[str, ...]:
        return tuple(sorted(item.get('targets', [])))

    active_archive_target_keys = {
        targets_key_from_item(item)
        for item in summary['items']
        if item['status'] in {'empty', 'stale_partial'}
    }
    existing_archive_target_keys: set[tuple[str, ...]] = set()
    for status_dir in ('empty', 'stale_partial'):
        existing_dir = archive_dir / status_dir
        if not existing_dir.exists():
            continue
        for patch_file in existing_dir.glob('score-patch-v4a-*.patch'):
            parsed = parse_patch_draft(patch_file)
            targets = [str(Path(raw_target)) for raw_target in parsed]
            existing_archive_target_keys.add(tuple(sorted(targets)))
    archive_target_keys = active_archive_target_keys | existing_archive_target_keys

    archived_items = []
    for item in summary['items']:
        source = Path(item['draft_path'])
        if not source.exists():
            continue
        item_targets_key = targets_key_from_item(item)
        archive_status = None
        if item_targets_key in existing_archive_target_keys:
            archive_status = 'superseded'
        elif item['status'] in {'empty', 'stale_partial'}:
            archive_status = item['status']
        elif item_targets_key in archive_target_keys:
            archive_status = 'superseded'
        if not archive_status:
            continue
        target_dir = archive_dir / archive_status
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / source.name
        shutil.move(str(source), str(destination))
        archived_items.append(
            {
                'draft_name': source.name,
                'status': archive_status,
                'destination': str(destination),
            }
        )
    return {
        'archived_count': len(archived_items),
        'archive_dir': str(archive_dir),
        'items': archived_items,
    }



def build_comment_body(summary: dict) -> str:
    lines = [
        f"total_drafts: {summary['total_drafts']}",
        f"pending_review_count: {summary['pending_review_count']}",
        f"empty_draft_count: {summary.get('empty_draft_count', 0)}",
        f"stale_partial_count: {summary.get('stale_partial_count', 0)}",
    ]
    candidate = summary.get('top_review_candidate')
    if candidate:
        lines.append(f"top_review_candidate: {candidate['draft_name']} ({candidate['status']})")
    lines.append('queue:')
    for item in summary['items']:
        lines.append(
            f"- {item['draft_name']}: status={item['status']}, applied_entries={item['applied_entries']}/{item['total_entries']}, pending_entries={item.get('pending_entries', 0)}, stale_entries={item.get('stale_entries', 0)}"
        )
    return '\n'.join(lines)



def main() -> None:
    parser = argparse.ArgumentParser(description='feedback patch draft review queue 를 요약한다.')
    parser.add_argument('--drafts-dir', default='feedback/patch_drafts')
    args = parser.parse_args()

    summary = summarize_patch_queue(Path(args.drafts_dir))
    print(json.dumps({'summary': summary, 'comment': build_comment_body(summary)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
