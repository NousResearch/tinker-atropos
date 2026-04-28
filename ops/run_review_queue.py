from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.review_patch_queue import archive_nonactionable_drafts, build_comment_body, summarize_patch_queue
from ops.sync_result_to_paperclip import build_issue_update_payload, patch_issue



def main() -> None:
    parser = argparse.ArgumentParser(description='Feedback patch draft review queue 를 요약하고 필요 시 Paperclip 에 동기화한다.')
    parser.add_argument('--drafts-dir', default='feedback/patch_drafts')
    parser.add_argument('--issue-id')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--archive-nonactionable', action='store_true')
    parser.add_argument('--archive-dir')
    args = parser.parse_args()

    drafts_dir = Path(args.drafts_dir)
    archive_result = None
    if args.archive_nonactionable:
        archive_result = archive_nonactionable_drafts(
            drafts_dir,
            archive_dir=Path(args.archive_dir) if args.archive_dir else None,
        )

    summary = summarize_patch_queue(drafts_dir)
    comment = build_comment_body(summary)

    if args.sync and args.issue_id:
        status = 'done' if summary['pending_review_count'] == 0 else 'todo'
        payload = build_issue_update_payload(comment, status=status)
        patch_issue(args.base_url, args.issue_id, payload)

    print(json.dumps({'summary': summary, 'comment': comment, 'archive_result': archive_result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
