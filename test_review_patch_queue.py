from pathlib import Path

from ops.review_patch_queue import archive_nonactionable_drafts, summarize_patch_queue


SAMPLE_PATCH = """*** Begin Patch
*** Update File: TARGET_FILE
@@
# suggested_old: old_line = 1
# suggested_new: old_line = 2
# weight_old: score = 0.1
# weight_new: score = 0.2
*** End Patch
"""

EMPTY_PATCH = """*** Begin Patch
*** Update File: TARGET_FILE
@@
# strengthen candidate: 신뢰 근거를 먼저 보여주는 headline (1회)
# penalize candidate: 긴 설명형 서브카피 (1회)
*** End Patch
"""


def test_summarize_patch_queue_marks_applied_partial_and_pending(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.1\n', encoding='utf-8')

    patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)

    assert summary['total_drafts'] == 1
    assert summary['items'][0]['status'] == 'partial'
    assert summary['items'][0]['applied_entries'] == 1
    assert summary['items'][0]['total_entries'] == 2
    assert summary['pending_review_count'] == 1



def test_summarize_patch_queue_sorts_newest_first(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')

    older = drafts / 'score-patch-v4a-20260413-200417.patch'
    newer = drafts / 'score-patch-v4a-20260413-210049.patch'
    older.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')
    newer.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)

    assert [item['draft_name'] for item in summary['items']] == [
        'score-patch-v4a-20260413-210049.patch',
        'score-patch-v4a-20260413-200417.patch',
    ]
    assert summary['items'][0]['status'] == 'pending'
    assert summary['items'][1]['status'] == 'superseded'



def test_summarize_patch_queue_reports_top_review_candidate(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')

    patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)

    assert summary['top_review_candidate']['draft_name'] == 'score-patch-v4a-20260413-210049.patch'
    assert summary['top_review_candidate']['status'] == 'pending'



def test_summarize_patch_queue_marks_empty_draft_and_excludes_it_from_pending_review(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')

    patch = drafts / 'score-patch-v4a-20260413-141243.patch'
    patch.write_text(EMPTY_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)

    assert summary['items'][0]['status'] == 'empty'
    assert summary['items'][0]['total_entries'] == 0
    assert summary['pending_review_count'] == 0
    assert summary['top_review_candidate'] is None



def test_summarize_patch_queue_marks_stale_partial_and_excludes_it_from_pending_review(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.3\n', encoding='utf-8')

    patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)

    assert summary['items'][0]['status'] == 'stale_partial'
    assert summary['items'][0]['applied_entries'] == 1
    assert summary['items'][0]['stale_entries'] == 1
    assert summary['items'][0]['pending_entries'] == 0
    assert summary['pending_review_count'] == 0
    assert summary['stale_partial_count'] == 1
    assert summary['top_review_candidate'] is None



def test_archive_nonactionable_drafts_moves_empty_and_stale_partial(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    archive_dir = tmp_path / 'archive'
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.3\n', encoding='utf-8')

    stale_patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    stale_patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')
    empty_patch = drafts / 'score-patch-v4a-20260413-141243.patch'
    empty_patch.write_text(EMPTY_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    result = archive_nonactionable_drafts(drafts, archive_dir=archive_dir)

    assert result['archived_count'] == 2
    assert not stale_patch.exists()
    assert not empty_patch.exists()
    assert (archive_dir / 'stale_partial' / stale_patch.name).exists()
    assert (archive_dir / 'empty' / empty_patch.name).exists()



def test_archive_nonactionable_drafts_also_moves_older_related_patches(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    archive_dir = tmp_path / 'archive'
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.3\n', encoding='utf-8')

    newer = drafts / 'score-patch-v4a-20260413-210049.patch'
    newer.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')
    older = drafts / 'score-patch-v4a-20260413-200417.patch'
    older.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    result = archive_nonactionable_drafts(drafts, archive_dir=archive_dir)

    assert result['archived_count'] == 2
    assert not newer.exists()
    assert not older.exists()
    assert (archive_dir / 'stale_partial' / newer.name).exists()
    assert (archive_dir / 'superseded' / older.name).exists()



def test_archive_nonactionable_drafts_uses_existing_archived_nonactionable_groups(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    archive_dir = tmp_path / 'archive'
    archived_stale_dir = archive_dir / 'stale_partial'
    archived_stale_dir.mkdir(parents=True)
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.3\n', encoding='utf-8')

    archived_patch = archived_stale_dir / 'score-patch-v4a-20260413-210049.patch'
    archived_patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')
    active_older = drafts / 'score-patch-v4a-20260413-200417.patch'
    active_older.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    result = archive_nonactionable_drafts(drafts, archive_dir=archive_dir)

    assert result['archived_count'] == 1
    assert not active_older.exists()
    assert (archive_dir / 'superseded' / active_older.name).exists()



def test_build_comment_body_lists_queue_statuses(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')

    patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    patch.write_text(SAMPLE_PATCH.replace('TARGET_FILE', str(target)), encoding='utf-8')

    summary = summarize_patch_queue(drafts)
    from ops.review_patch_queue import build_comment_body

    comment = build_comment_body(summary)

    assert 'total_drafts: 1' in comment
    assert 'pending_review_count: 1' in comment
    assert 'score-patch-v4a-20260413-210049.patch' in comment
    assert 'status=pending' in comment
