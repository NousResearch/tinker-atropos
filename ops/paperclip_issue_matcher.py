from __future__ import annotations

OPEN_STATUSES = {'todo', 'in_progress', 'blocked'}
CLOSED_STATUSES = {'done', 'cancelled'}



def _sort_issue_candidates(issues: list[dict]) -> list[dict]:
    return sorted(
        issues,
        key=lambda issue: (issue.get('issueNumber') or 0, issue.get('updatedAt') or ''),
        reverse=True,
    )



def _open_matches(issues: list[dict]) -> list[dict]:
    return [issue for issue in issues if issue.get('status') not in CLOSED_STATUSES]



def _identifier_matches(issues: list[dict], identifier: str | None) -> list[dict]:
    if not identifier:
        return []
    return [issue for issue in issues if issue.get('identifier') == identifier]



def _title_matches(issues: list[dict], title: str | None) -> list[dict]:
    if not title:
        return []
    return [issue for issue in issues if issue.get('title') == title]



def find_issue_for_payload(issues: list[dict], payload: dict) -> dict | None:
    identifier = payload.get('identifier')
    title = payload.get('title')

    identifier_matches = _identifier_matches(issues, identifier)
    title_matches = _title_matches(issues, title)
    both_matches = [
        issue for issue in issues if issue.get('identifier') == identifier and issue.get('title') == title
    ]

    priority_groups = [
        _open_matches(both_matches),
        _open_matches(identifier_matches),
        _open_matches(title_matches),
        both_matches,
        identifier_matches,
        title_matches,
    ]
    for candidates in priority_groups:
        if candidates:
            return _sort_issue_candidates(candidates)[0]
    return None
