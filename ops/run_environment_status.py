from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.environment_status import build_comment_body, collect_environment_status
from ops.sync_result_to_paperclip import build_issue_update_payload, patch_issue



def main() -> None:
    parser = argparse.ArgumentParser(description='Tinker-Atropos 환경 상태를 요약한다.')
    parser.add_argument('--root', default='/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    parser.add_argument('--issue-id')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--sync', action='store_true')
    args = parser.parse_args()

    summary = collect_environment_status(Path(args.root))
    comment = build_comment_body(summary)

    if args.sync and args.issue_id:
        status = 'done' if summary['alert_count'] == 0 else 'todo'
        payload = build_issue_update_payload(comment, status=status)
        patch_issue(args.base_url, args.issue_id, payload)

    print(json.dumps({'summary': summary, 'comment': comment}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
