import pytest

from ops.sync_result_to_paperclip import build_issue_update_payload, build_comment_body
from ops.paperclip_curl import build_curl_command
from ops.tinker_paperclip_sync import determine_full_funnel_issue_status, determine_preset_issue_status, determine_feedback_triage_issue_status



def test_build_issue_update_payload_includes_comment_and_status():
    payload = build_issue_update_payload(
        comment='테스트 통과',
        status='done',
        priority='high',
    )

    assert payload == {
        'comment': '테스트 통과',
        'status': 'done',
        'priority': 'high',
    }



def test_build_comment_body_summarizes_result_paths_and_outcome():
    body = build_comment_body(
        title='Feedback Patch Draft Review Queue',
        success=True,
        summary='관련 테스트 통과',
        log_path='logs/2026-04-13-feedback.log',
        context_path='.omx/context-feedback.md',
        test_command='pytest test_patch_precision.py -q',
    )

    assert 'Feedback Patch Draft Review Queue' in body
    assert '성공' in body
    assert '관련 테스트 통과' in body
    assert 'logs/2026-04-13-feedback.log' in body
    assert '.omx/context-feedback.md' in body
    assert 'pytest test_patch_precision.py -q' in body



def test_build_curl_command_adds_authorization_and_json_payload(monkeypatch):
    monkeypatch.setenv('PAPERCLIP_API_KEY', 'dummy-token')

    command = build_curl_command(
        method='PATCH',
        url='http://127.0.0.1:3100/api/issues/issue-1',
        payload={'status': 'done', 'comment': '완료'},
    )

    assert command[:4] == ['curl', '-sS', '-X', 'PATCH']
    assert 'Authorization: Bearer dummy-token' in command
    assert 'Content-Type: application/json' in command
    assert any(part == '{"status": "done", "comment": "완료"}' for part in command)



def test_build_curl_command_allows_local_trusted_without_api_key(monkeypatch):
    monkeypatch.delenv('PAPERCLIP_API_KEY', raising=False)
    monkeypatch.setattr('ops.paperclip_curl.is_local_trusted_mode', lambda url: True)

    command = build_curl_command(
        method='GET',
        url='http://127.0.0.1:3100/api/companies/company-1/issues',
    )

    assert command[:4] == ['curl', '-sS', '-X', 'GET']
    assert not any('Authorization: Bearer ' in part for part in command)



def test_build_curl_command_requires_paperclip_api_key(monkeypatch):
    monkeypatch.delenv('PAPERCLIP_API_KEY', raising=False)
    monkeypatch.setattr('ops.paperclip_curl.is_local_trusted_mode', lambda url: False)

    with pytest.raises(RuntimeError):
        build_curl_command(
            method='GET',
            url='http://127.0.0.1:3100/api/companies/company-1/issues',
        )



def test_tinker_sync_status_helpers_cover_full_funnel_preset_and_feedback():
    assert determine_full_funnel_issue_status({'run_count': 1, 'alert_count': 0}) == 'done'
    assert determine_full_funnel_issue_status({'run_count': 1, 'alert_count': 1}) == 'todo'
    assert determine_preset_issue_status({'preset_count': 1, 'totals': {'final_runs': 1}}) == 'done'
    assert determine_preset_issue_status({'preset_count': 0, 'totals': {'final_runs': 1}}) == 'todo'
    assert determine_feedback_triage_issue_status({'total_drafts': 9, 'pending_review_count': 2}) == 'done'
