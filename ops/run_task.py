from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.external_execution import ExecutionSpec, build_execution_plan, render_shell_script
from ops.sync_result_to_paperclip import build_comment_body, patch_issue, build_issue_update_payload



def run_shell_script(script: str, workdir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['bash', '-lc', script],
        cwd=workdir,
        capture_output=True,
        text=True,
    )



def main() -> None:
    parser = argparse.ArgumentParser(description='외부 실행 래퍼를 생성하거나 실행한다.')
    parser.add_argument('--title', required=True)
    parser.add_argument('--task-type', default='general')
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--target', action='append', dest='targets')
    parser.add_argument('--test-command')
    parser.add_argument('--issue-id')
    parser.add_argument('--base-url', default='http://127.0.0.1:3100')
    parser.add_argument('--use-rp', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--sync', action='store_true')
    args = parser.parse_args()

    spec = ExecutionSpec(
        title=args.title,
        task_type=args.task_type,
        prompt=args.prompt,
        targets=args.targets,
        use_rp=args.use_rp,
        test_command=args.test_command,
    )
    plan = build_execution_plan(spec)

    if not args.execute:
        print(json.dumps({'plan': plan, 'script': render_shell_script(plan)}, ensure_ascii=False, indent=2))
        return

    script = render_shell_script(plan)
    result = run_shell_script(script, Path(plan['workdir']))
    success = result.returncode == 0
    summary = '외부 실행이 정상 종료됐다.' if success else '외부 실행 중 오류가 발생했다.'

    if args.sync and args.issue_id:
        comment = build_comment_body(
            title=args.title,
            success=success,
            summary=summary,
            log_path=plan['log_path'],
            context_path=plan['context_path'] if args.use_rp and args.targets else None,
            test_command=args.test_command,
        )
        payload = build_issue_update_payload(comment, status='done' if success else 'blocked')
        patch_issue(args.base_url, args.issue_id, payload)

    print(json.dumps({
        'success': success,
        'returncode': result.returncode,
        'plan': plan,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
