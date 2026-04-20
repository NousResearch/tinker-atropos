from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.sync_result_to_paperclip import build_issue_update_payload, patch_issue
from ops.weekly_tinker_summary import build_markdown_summary, collect_weekly_summary



def main() -> None:
    parser = argparse.ArgumentParser(description='주간 Tinker 연구 요약을 생성한다.')
    parser.add_argument('--root', default='/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    parser.add_argument('--issue-id')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--sync', action='store_true')
    args = parser.parse_args()

    summary = collect_weekly_summary(Path(args.root))
    markdown = build_markdown_summary(summary)

    if args.sync and args.issue_id:
        payload = build_issue_update_payload(markdown, status='done')
        patch_issue(args.base_url, args.issue_id, payload)

    print(markdown)
    print('\n--- JSON ---')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
