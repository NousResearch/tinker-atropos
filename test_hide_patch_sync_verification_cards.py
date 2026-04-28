from ops.hide_patch_sync_verification_cards import build_hide_payload, select_patch_sync_verification_issues


def test_select_patch_sync_verification_issues_skips_hidden_and_nonmatching_titles():
    issues = [
        {'id': '1', 'identifier': 'TIN-23', 'title': 'Patch Sync Verification 승인 거부', 'hiddenAt': None},
        {'id': '2', 'identifier': 'TIN-24', 'title': 'Patch Sync Verification 롤백', 'hiddenAt': '2026-04-15T22:49:11.000Z'},
        {'id': '3', 'identifier': 'TIN-18', 'title': 'Daily Feedback Draft Triage', 'hiddenAt': None},
    ]

    selected = select_patch_sync_verification_issues(issues)

    assert [issue['identifier'] for issue in selected] == ['TIN-23']


def test_build_hide_payload_sets_hidden_at_and_comment():
    payload = build_hide_payload('2026-04-16T00:00:00Z', comment='검증 완료')

    assert payload == {
        'comment': '검증 완료',
        'hiddenAt': '2026-04-16T00:00:00Z',
    }
