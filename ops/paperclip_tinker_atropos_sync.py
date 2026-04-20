#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.paperclip_curl import curl_json
from ops.paperclip_issue_matcher import find_issue_for_payload
from ops.tinker_paperclip_sync import build_feedback_triage_sync_payload, build_full_funnel_sync_payload, build_preset_sync_payload, build_promotion_eval_sync_payload


COMPANY_ID = '162e6af8-809e-4d24-b270-213f5603cf7b'
ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
DEFAULT_BASE_URL = 'http://127.0.0.1:3100'



def fetch_company_issues(company_id: str, base_url: str) -> list[dict]:
    return curl_json('GET', f'/api/companies/{company_id}/issues?includeRoutineExecutions=true&limit=300', base_url=base_url)



def sync_issue(issue: dict, payload: dict, base_url: str) -> dict:
    comment = f"Tinker Atropos external sync\n\n{payload['comment']}"
    curl_json('POST', f"/api/issues/{issue['id']}/comments", payload={'body': comment}, base_url=base_url)
    curl_json('PATCH', f"/api/issues/{issue['id']}", payload={'status': payload['status']}, base_url=base_url)
    return {
        'identifier': payload['identifier'],
        'issue_id': issue['id'],
        'status': payload['status'],
        'updated': True,
    }



def main() -> None:
    parser = argparse.ArgumentParser(description='Tinker Atropos Ops company sync draft')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--company-id', default=COMPANY_ID)
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    root = Path(args.root)
    issues = fetch_company_issues(args.company_id, args.base_url)
    payloads = [
        build_feedback_triage_sync_payload(root),
        build_full_funnel_sync_payload(root),
        build_preset_sync_payload(root),
        build_promotion_eval_sync_payload(root),
    ]

    results = []
    for payload in payloads:
        issue = find_issue_for_payload(issues, payload)
        if not issue:
            results.append({'identifier': payload['identifier'], 'updated': False, 'reason': 'issue_not_found', 'status': payload['status']})
            continue
        if args.dry_run:
            results.append({'identifier': payload['identifier'], 'updated': False, 'reason': 'dry_run', 'status': payload['status']})
            continue
        results.append(sync_issue(issue, payload, args.base_url))

    print(json.dumps({'company_id': args.company_id, 'root': str(root), 'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
