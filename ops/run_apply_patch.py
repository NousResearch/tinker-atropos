from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.apply_patch_draft import apply_patch_draft, parse_patch_draft
from ops.review_patch_queue import summarize_patch_queue
from ops.sync_result_to_paperclip import build_issue_update_payload, patch_issue

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
DEFAULT_DRAFTS_DIR = ROOT / 'feedback' / 'patch_drafts'


def _normalize_path(path: Path) -> Path:
    return path.expanduser().resolve()


def run_test_commands(commands: list[str], workdir: Path) -> list[dict]:
    results = []
    for command in commands:
        proc = subprocess.run(['bash', '-lc', command], cwd=workdir, capture_output=True, text=True)
        results.append({'command': command, 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
    return results


def snapshot_existing_targets(patch_file: Path, root: Path | None = None) -> dict[Path, str]:
    originals: dict[Path, str] = {}
    parsed = parse_patch_draft(patch_file)
    for raw_target in parsed:
        target = Path(raw_target)
        if root and not target.is_absolute():
            target = root / target
        if target.exists():
            originals[target] = target.read_text(encoding='utf-8')
    return originals


def rollback_files(originals: dict[Path, str]) -> int:
    restored = 0
    for path, content in originals.items():
        path.write_text(content, encoding='utf-8')
        restored += 1
    return restored


def assess_patch_approval(
    *,
    patch_file: Path,
    drafts_dir: Path,
    skip_approval_check: bool = False,
) -> dict[str, object]:
    normalized_patch = _normalize_path(patch_file)
    if skip_approval_check:
        return {
            'approved': True,
            'approval_status': 'override',
            'approval_reason': 'skip_approval_check',
            'next_action': 'run_patch_execution',
        }

    summary = summarize_patch_queue(drafts_dir)
    items = summary.get('items', [])
    matched_item = next(
        (
            item
            for item in items
            if _normalize_path(Path(item['draft_path'])) == normalized_patch
        ),
        None,
    )
    if matched_item is None:
        return {
            'approved': False,
            'approval_status': 'denied',
            'approval_reason': 'not_in_review_queue',
            'next_action': 'run_review_queue',
        }

    top_candidate = summary.get('top_review_candidate')
    if top_candidate and _normalize_path(Path(top_candidate['draft_path'])) == normalized_patch:
        return {
            'approved': True,
            'approval_status': 'approved',
            'approval_reason': 'top_review_candidate',
            'next_action': 'run_patch_execution',
        }

    item_status = str(matched_item.get('status', 'unknown'))
    reason = f'queue_status_{item_status}'
    next_action = 'run_review_queue'
    if top_candidate:
        next_action = f"review_candidate:{top_candidate['draft_name']}"
    return {
        'approved': False,
        'approval_status': 'denied',
        'approval_reason': reason,
        'next_action': next_action,
    }


def determine_issue_status(
    *,
    applied: int,
    failed_tests: int,
    missing_files: int,
    rolled_back: bool,
    approved: bool,
) -> str:
    return 'done' if approved and applied > 0 and failed_tests == 0 and missing_files == 0 and not rolled_back else 'blocked'


def determine_issue_priority(
    *,
    approved: bool,
    failed_tests: int,
    missing_files: int,
    rolled_back: bool,
) -> str:
    if rolled_back or failed_tests > 0 or missing_files > 0:
        return 'high'
    if not approved:
        return 'medium'
    return 'low'


def build_status_comment(
    *,
    patch_file: str,
    apply_results: dict[str, dict[str, int]],
    test_results: list[dict],
    rolled_back: bool,
    rollback_reason: str,
    approved: bool,
    approval_status: str,
    approval_reason: str,
    next_action: str,
    status: str,
    priority: str,
) -> str:
    yes_no = '예' if rolled_back else '아니오'
    approved_text = '예' if approved else '아니오'
    status_text = '완료' if status == 'done' else '막힘' if status == 'blocked' else status
    priority_text = '높음' if priority == 'high' else '보통' if priority == 'medium' else '낮음' if priority == 'low' else priority
    summary_text = '성공' if status == 'done' else '롤백' if rolled_back else '승인 거부' if not approved else '검토 필요'
    lines = [
        f'[{status_text} · {priority_text}] {summary_text}',
        '## 결과 요약',
        f'- patch_file: {patch_file}',
        f'- 승인됨: {approved_text}',
        f'- 승인 상태: {approval_status}',
        f'- 승인 사유: {approval_reason}',
        f'- 다음 행동: {next_action}',
        '',
        '## 적용 결과',
    ]
    if apply_results:
        for path, result in apply_results.items():
            lines.append(
                f'- {path}: applied={result.get("applied", 0)}, skipped={result.get("skipped", 0)}, '
                f'missing_file={result.get("missing_file", 0)}, changed={result.get("changed", 0)}'
            )
    else:
        lines.append('- no changes applied')
    lines.extend(['', '## 테스트'])
    if test_results:
        for result in test_results:
            lines.append(f'- {result["command"]}: returncode={result["returncode"]}')
    else:
        lines.append('- no tests run')
    lines.extend([
        '',
        '## 롤백',
        f'- rolled_back: {yes_no}',
        f'- rollback_reason: {rollback_reason}',
    ])
    return '\n'.join(lines)


def execute_patch_run(
    patch_file: Path,
    test_commands: list[str],
    root: Path = ROOT,
    drafts_dir: Path = DEFAULT_DRAFTS_DIR,
    skip_approval_check: bool = False,
) -> dict:
    approval = assess_patch_approval(
        patch_file=patch_file,
        drafts_dir=drafts_dir,
        skip_approval_check=skip_approval_check,
    )
    approved = bool(approval['approved'])
    approval_status = str(approval['approval_status'])
    approval_reason = str(approval['approval_reason'])
    next_action = str(approval['next_action'])

    apply_results: dict[str, dict[str, int]] = {}
    originals: dict[Path, str] = {}
    if approved:
        originals = snapshot_existing_targets(patch_file, root=root)
        apply_results = apply_patch_draft(patch_file, root=root)

    applied = sum(item['applied'] for item in apply_results.values())
    skipped = sum(item.get('skipped', 0) for item in apply_results.values())
    missing_files = sum(item.get('missing_file', 0) for item in apply_results.values())

    test_results: list[dict] = []
    rollback_reason = ''
    if not approved:
        rollback_reason = 'approval_denied'
    elif missing_files > 0 or skipped > 0:
        rollback_reason = 'apply_verification_failed'
    else:
        test_results = run_test_commands(test_commands, root) if test_commands else []
        if any(item['returncode'] != 0 for item in test_results):
            rollback_reason = 'tests_failed'

    rolled_back = False
    restored_files = 0
    if rollback_reason and applied > 0:
        restored_files = rollback_files(originals)
        rolled_back = True

    failed_tests = sum(1 for item in test_results if item['returncode'] != 0)
    status = determine_issue_status(
        applied=applied,
        failed_tests=failed_tests,
        missing_files=missing_files,
        rolled_back=rolled_back,
        approved=approved,
    )
    priority = determine_issue_priority(
        approved=approved,
        failed_tests=failed_tests,
        missing_files=missing_files,
        rolled_back=rolled_back,
    )
    comment = build_status_comment(
        patch_file=str(patch_file),
        apply_results=apply_results,
        test_results=test_results,
        rolled_back=rolled_back,
        rollback_reason=rollback_reason,
        approved=approved,
        approval_status=approval_status,
        approval_reason=approval_reason,
        next_action=next_action,
        status=status,
        priority=priority,
    )
    return {
        'status': status,
        'priority': priority,
        'approved': approved,
        'approval_status': approval_status,
        'approval_reason': approval_reason,
        'next_action': next_action,
        'applied': applied,
        'skipped': skipped,
        'missing_files': missing_files,
        'failed_tests': failed_tests,
        'rolled_back': rolled_back,
        'restored_files': restored_files,
        'rollback_reason': rollback_reason,
        'apply_results': apply_results,
        'test_results': [{'command': item['command'], 'returncode': item['returncode']} for item in test_results],
        'comment': comment,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='patch draft 를 실제 파일에 적용하고 테스트 후 Paperclip 에 동기화한다.')
    parser.add_argument('patch_file')
    parser.add_argument('--test-command', action='append', default=[])
    parser.add_argument('--drafts-dir', default=str(DEFAULT_DRAFTS_DIR))
    parser.add_argument('--issue-id')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--skip-approval-check', action='store_true')
    args = parser.parse_args()

    patch_file = Path(args.patch_file)
    result = execute_patch_run(
        patch_file,
        test_commands=args.test_command,
        root=ROOT,
        drafts_dir=Path(args.drafts_dir),
        skip_approval_check=args.skip_approval_check,
    )

    if args.sync and args.issue_id:
        payload = build_issue_update_payload(
            result['comment'],
            status=result['status'],
            priority=result['priority'],
        )
        patch_issue(args.base_url, args.issue_id, payload)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
