from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.paperclip_curl import curl_json

DEFAULT_BASE_URL = 'http://127.0.0.1:3100'
DEFAULT_COMPANY_ID = '162e6af8-809e-4d24-b270-213f5603cf7b'
TITLE_PREFIX = 'Patch Sync Verification'
DEFAULT_COMMENT = '임시 검증 카드 자동 숨김 처리 완료. 상태 증거는 기존 댓글에 남아 있다.'


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fetch_company_issues(company_id: str, base_url: str = DEFAULT_BASE_URL) -> list[dict]:
    return curl_json('GET', f'/api/companies/{company_id}/issues?includeRoutineExecutions=true&limit=300', base_url=base_url)


def select_patch_sync_verification_issues(issues: list[dict], title_prefix: str = TITLE_PREFIX) -> list[dict]:
    return [
        issue for issue in issues
        if str(issue.get('title', '')).startswith(title_prefix) and not issue.get('hiddenAt')
    ]


def build_hide_payload(hidden_at: str, comment: str = DEFAULT_COMMENT) -> dict:
    return {
        'comment': comment,
        'hiddenAt': hidden_at,
    }


def hide_issue(issue_id: str, payload: dict, base_url: str = DEFAULT_BASE_URL) -> dict:
    return curl_json('PATCH', f'/api/issues/{issue_id}', payload=payload, base_url=base_url)


def run_hide_pass(
    *,
    company_id: str = DEFAULT_COMPANY_ID,
    base_url: str = DEFAULT_BASE_URL,
    title_prefix: str = TITLE_PREFIX,
    comment: str = DEFAULT_COMMENT,
    hidden_at: str | None = None,
) -> dict:
    effective_hidden_at = hidden_at or now_utc_iso()
    issues = fetch_company_issues(company_id, base_url=base_url)
    targets = select_patch_sync_verification_issues(issues, title_prefix=title_prefix)
    payload = build_hide_payload(effective_hidden_at, comment=comment)
    results = []
    for issue in targets:
        updated = hide_issue(issue['id'], payload, base_url=base_url)
        results.append({
            'id': updated.get('id', issue['id']),
            'identifier': updated.get('identifier', issue.get('identifier')),
            'status': updated.get('status', issue.get('status')),
            'hiddenAt': updated.get('hiddenAt', effective_hidden_at),
        })
    return {
        'company_id': company_id,
        'title_prefix': title_prefix,
        'hidden_at': effective_hidden_at,
        'count': len(results),
        'results': results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Patch Sync Verification 임시 카드를 자동 숨김 처리한다.')
    parser.add_argument('--company-id', default=DEFAULT_COMPANY_ID)
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--title-prefix', default=TITLE_PREFIX)
    parser.add_argument('--comment', default=DEFAULT_COMMENT)
    parser.add_argument('--hidden-at')
    args = parser.parse_args()

    result = run_hide_pass(
        company_id=args.company_id,
        base_url=args.base_url,
        title_prefix=args.title_prefix,
        comment=args.comment,
        hidden_at=args.hidden_at,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
