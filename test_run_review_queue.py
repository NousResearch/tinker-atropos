from pathlib import Path
import subprocess
import json



def test_run_review_queue_cli_prints_summary_and_comment(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'target.py'
    target.write_text('old_line = 1\nscore = 0.1\n', encoding='utf-8')
    patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    patch.write_text(
        '*** Begin Patch\n'
        f'*** Update File: {target}\n'
        '@@\n'
        '# suggested_old: old_line = 1\n'
        '# suggested_new: old_line = 2\n'
        '*** End Patch\n',
        encoding='utf-8',
    )

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_review_queue.py', '--drafts-dir', str(drafts)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'score-patch-v4a-20260413-210049.patch' in proc.stdout
    assert 'pending_review_count' in proc.stdout



def test_run_review_queue_cli_archives_nonactionable_drafts(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    archive_dir = tmp_path / 'archived'
    target = tmp_path / 'target.py'
    target.write_text('old_line = 2\nscore = 0.3\n', encoding='utf-8')

    stale_patch = drafts / 'score-patch-v4a-20260413-210049.patch'
    stale_patch.write_text(
        '*** Begin Patch\n'
        f'*** Update File: {target}\n'
        '@@\n'
        '# suggested_old: old_line = 1\n'
        '# suggested_new: old_line = 2\n'
        '# weight_old: score = 0.1\n'
        '# weight_new: score = 0.2\n'
        '*** End Patch\n',
        encoding='utf-8',
    )
    empty_patch = drafts / 'score-patch-v4a-20260413-141243.patch'
    empty_patch.write_text(
        '*** Begin Patch\n'
        f'*** Update File: {target}\n'
        '@@\n'
        '# strengthen candidate: 신뢰 근거를 먼저 보여주는 headline (1회)\n'
        '*** End Patch\n',
        encoding='utf-8',
    )

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_review_queue.py', '--drafts-dir', str(drafts), '--archive-nonactionable', '--archive-dir', str(archive_dir)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['archive_result']['archived_count'] == 2
    assert payload['summary']['total_drafts'] == 0
    assert (archive_dir / 'stale_partial' / stale_patch.name).exists()
    assert (archive_dir / 'empty' / empty_patch.name).exists()
