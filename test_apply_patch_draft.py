from pathlib import Path

from ops.apply_patch_draft import PatchEntry, apply_entries_to_file, parse_patch_draft


SAMPLE_DRAFT = """*** Begin Patch
*** Update File: /tmp/example.py
@@
# suggested_old: old_line = 1
# suggested_new: old_line = 2
# weight_old: score = 0.1
# weight_new: score = 0.2
# suggested_old: old_line = 1
# suggested_new: old_line = 2
*** End Patch
"""


def test_parse_patch_draft_extracts_entries_and_deduplicates_pairs(tmp_path):
    draft = tmp_path / 'sample.patch'
    draft.write_text(SAMPLE_DRAFT, encoding='utf-8')

    parsed = parse_patch_draft(draft)

    assert list(parsed) == ['/tmp/example.py']
    entries = parsed['/tmp/example.py']
    assert entries == [
        PatchEntry(old='old_line = 1', new='old_line = 2', source='suggested'),
        PatchEntry(old='score = 0.1', new='score = 0.2', source='weight'),
    ]



def test_apply_entries_to_file_updates_all_matching_blocks(tmp_path):
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')
    entries = [
        PatchEntry(old='old_line = 1', new='old_line = 2', source='suggested'),
        PatchEntry(old='score = 0.1', new='score = 0.2', source='weight'),
    ]

    result = apply_entries_to_file(target, entries)

    assert result['applied'] == 2
    assert result['skipped'] == 0
    assert target.read_text(encoding='utf-8') == 'old_line = 2\nscore = 0.2\n'



def test_apply_entries_to_file_skips_missing_blocks_without_crashing(tmp_path):
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\n', encoding='utf-8')
    entries = [
        PatchEntry(old='missing = 0', new='missing = 1', source='suggested'),
    ]

    result = apply_entries_to_file(target, entries)

    assert result['applied'] == 0
    assert result['skipped'] == 1
    assert target.read_text(encoding='utf-8') == 'old_line = 1\n'
