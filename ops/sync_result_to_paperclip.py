from __future__ import annotations

import argparse
import json

from ops.paperclip_curl import curl_json



def build_issue_update_payload(comment: str, status: str | None = None, priority: str | None = None) -> dict:
    payload = {'comment': comment}
    if status:
        payload['status'] = status
    if priority:
        payload['priority'] = priority
    return payload



def build_comment_body(
    *,
    title: str,
    success: bool,
    summary: str,
    log_path: str,
    context_path: str | None = None,
    test_command: str | None = None,
) -> str:
    status_text = '성공' if success else '실패'
    lines = [
        f'작업: {title}',
        f'결과: {status_text}',
        f'요약: {summary}',
        f'로그: {log_path}',
    ]
    if context_path:
        lines.append(f'컨텍스트: {context_path}')
    if test_command:
        lines.append(f'테스트: {test_command}')
    return '\n'.join(lines)



def patch_issue(base_url: str, issue_id: str, payload: dict) -> dict:
    return curl_json('PATCH', f'/api/issues/{issue_id}', payload=payload, base_url=base_url)



def main() -> None:
    parser = argparse.ArgumentParser(description='Paperclip 이슈에 외부 실행 결과를 동기화한다.')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--issue-id', required=True)
    parser.add_argument('--comment', required=True)
    parser.add_argument('--status')
    parser.add_argument('--priority')
    args = parser.parse_args()

    payload = build_issue_update_payload(args.comment, status=args.status, priority=args.priority)
    result = patch_issue(args.base_url, args.issue_id, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
