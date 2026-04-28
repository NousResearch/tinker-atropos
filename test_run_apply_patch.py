from pathlib import Path

from ops.run_apply_patch import build_status_comment, determine_issue_status, execute_patch_run


SAMPLE_DRAFT = """*** Begin Patch
*** Update File: TARGET_FILE
@@
# suggested_old: old_line = 1
# suggested_new: old_line = 2
*** End Patch
"""


def make_patch(path: Path, target: Path) -> Path:
    path.write_text(SAMPLE_DRAFT.replace('TARGET_FILE', str(target)), encoding='utf-8')
    return path


def test_determine_issue_status_marks_done_only_when_patch_and_tests_pass():
    assert determine_issue_status(applied=3, failed_tests=0, missing_files=0, rolled_back=False, approved=True) == 'done'
    assert determine_issue_status(applied=0, failed_tests=0, missing_files=0, rolled_back=False, approved=True) == 'blocked'
    assert determine_issue_status(applied=3, failed_tests=1, missing_files=0, rolled_back=False, approved=True) == 'blocked'
    assert determine_issue_status(applied=3, failed_tests=0, missing_files=1, rolled_back=False, approved=True) == 'blocked'
    assert determine_issue_status(applied=3, failed_tests=0, missing_files=0, rolled_back=True, approved=True) == 'blocked'
    assert determine_issue_status(applied=3, failed_tests=0, missing_files=0, rolled_back=False, approved=False) == 'blocked'


def test_build_status_comment_includes_apply_test_and_approval_summary():
    comment = build_status_comment(
        patch_file='feedback/patch_drafts/example.patch',
        apply_results={
            'build_business_to_x_loop.py': {'applied': 2, 'skipped': 1, 'missing_file': 0, 'changed': 1},
            'build_business_to_landing_loop.py': {'applied': 1, 'skipped': 0, 'missing_file': 0, 'changed': 1},
        },
        test_results=[
            {'command': 'pytest test_patch_precision.py -q', 'returncode': 0},
            {'command': 'pytest test_build_business_to_x_loop.py -q', 'returncode': 0},
        ],
        rolled_back=True,
        rollback_reason='tests_failed',
        approved=False,
        approval_status='denied',
        approval_reason='queue_status_superseded',
        next_action='review_candidate:new.patch',
        status='blocked',
        priority='medium',
    )

    first_line = comment.splitlines()[0]
    assert first_line == '[막힘 · 보통] 롤백'
    assert '## 결과 요약' in comment
    assert '- patch_file: feedback/patch_drafts/example.patch' in comment
    assert '- 승인됨: 아니오' in comment
    assert '- 승인 상태: denied' in comment
    assert '- 승인 사유: queue_status_superseded' in comment
    assert '- 다음 행동: review_candidate:new.patch' in comment
    assert '## 적용 결과' in comment
    assert 'build_business_to_x_loop.py' in comment
    assert 'applied=2' in comment
    assert 'skipped=1' in comment
    assert 'changed=1' in comment
    assert '## 테스트' in comment
    assert 'pytest test_patch_precision.py -q' in comment
    assert 'returncode=0' in comment
    assert '## 롤백' in comment
    assert '- rolled_back: 예' in comment
    assert '- rollback_reason: tests_failed' in comment


def test_execute_patch_run_blocks_when_patch_is_not_top_review_candidate(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\n', encoding='utf-8')

    older_patch = make_patch(drafts / 'score-patch-v4a-20260413-200417.patch', target)
    make_patch(drafts / 'score-patch-v4a-20260413-210049.patch', target)

    result = execute_patch_run(
        older_patch,
        test_commands=["python -c 'import sys; sys.exit(1)'"],
        root=tmp_path,
        drafts_dir=drafts,
    )

    assert result['status'] == 'blocked'
    assert result['priority'] == 'medium'
    assert result['approved'] is False
    assert result['approval_status'] == 'denied'
    assert result['approval_reason'] == 'queue_status_superseded'
    assert result['next_action'] == 'review_candidate:score-patch-v4a-20260413-210049.patch'
    assert result['applied'] == 0
    assert result['failed_tests'] == 0
    assert result['test_results'] == []
    assert target.read_text(encoding='utf-8') == 'old_line = 1\n'


def test_execute_patch_run_rolls_back_when_tests_fail(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\n', encoding='utf-8')
    patch_file = make_patch(drafts / 'score-patch-v4a-20260413-210049.patch', target)

    result = execute_patch_run(
        patch_file,
        test_commands=["python -c 'import sys; sys.exit(1)'"],
        root=tmp_path,
        drafts_dir=drafts,
    )

    assert result['approved'] is True
    assert result['priority'] == 'high'
    assert result['rolled_back'] is True
    assert result['rollback_reason'] == 'tests_failed'
    assert target.read_text(encoding='utf-8') == 'old_line = 1\n'


def test_execute_patch_run_keeps_changes_when_tests_pass(tmp_path):
    drafts = tmp_path / 'patch_drafts'
    drafts.mkdir()
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\n', encoding='utf-8')
    patch_file = make_patch(drafts / 'score-patch-v4a-20260413-210049.patch', target)

    result = execute_patch_run(
        patch_file,
        test_commands=["python -c 'print(123)'"],
        root=tmp_path,
        drafts_dir=drafts,
    )

    assert result['status'] == 'done'
    assert result['priority'] == 'low'
    assert result['approved'] is True
    assert result['approval_status'] == 'approved'
    assert result['approval_reason'] == 'top_review_candidate'
    assert result['rolled_back'] is False
    assert result['rollback_reason'] == ''
    assert target.read_text(encoding='utf-8') == 'old_line = 2\n'


def test_execute_patch_run_skip_approval_check_allows_manual_override(tmp_path):
    target = tmp_path / 'example.py'
    target.write_text('old_line = 1\n', encoding='utf-8')
    patch_file = make_patch(tmp_path / 'draft.patch', target)

    result = execute_patch_run(
        patch_file,
        test_commands=["python -c 'print(123)'"],
        root=tmp_path,
        drafts_dir=tmp_path / 'patch_drafts',
        skip_approval_check=True,
    )

    assert result['status'] == 'done'
    assert result['approved'] is True
    assert result['approval_status'] == 'override'
    assert result['approval_reason'] == 'skip_approval_check'
    assert result['next_action'] == 'run_patch_execution'
    assert target.read_text(encoding='utf-8') == 'old_line = 2\n'
