from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from ops.promotion_eval_daily import DEFAULT_BASE_URL, DEFAULT_COMPANY_ID, DEFAULT_ROOT, run_daily


def main() -> None:
    parser = argparse.ArgumentParser(description='승격 평가 일일 실행기와 Paperclip 동기화를 한 번에 실행한다.')
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--company-id', default=DEFAULT_COMPANY_ID)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = run_daily(
        root=Path(args.root),
        base_url=args.base_url,
        company_id=args.company_id,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(result['report'])


if __name__ == '__main__':
    main()
