import pytest

from ops.tinker_paperclip_sync import determine_full_funnel_issue_status, determine_preset_issue_status, determine_promotion_eval_issue_status
from ops.paperclip_issue_matcher import find_issue_for_payload



def test_determine_full_funnel_issue_status_requires_runs_and_zero_alerts():
    assert determine_full_funnel_issue_status({'run_count': 1, 'alert_count': 0}) == 'done'
    assert determine_full_funnel_issue_status({'run_count': 0, 'alert_count': 0}) == 'todo'
    assert determine_full_funnel_issue_status({'run_count': 5, 'alert_count': 2}) == 'todo'



def test_determine_preset_issue_status_requires_presets_and_final_runs():
    assert determine_preset_issue_status({'preset_count': 1, 'totals': {'final_runs': 3}}) == 'done'
    assert determine_preset_issue_status({'preset_count': 0, 'totals': {'final_runs': 3}}) == 'todo'
    assert determine_preset_issue_status({'preset_count': 2, 'totals': {'final_runs': 0}}) == 'todo'



def test_determine_promotion_eval_issue_status_requires_v2_and_v3_signal_shape():
    good = {
        'benchmark_count': 2,
        'latest_summary_json': 'outputs/2026-04-19/promotion-eval/summary/min-hermes-promotion-eval-20260419-010351.json',
        'latest_summary_markdown': 'outputs/2026-04-19/promotion-eval/summary/min-hermes-promotion-eval-20260419-010351.md',
        'benchmarks': {
            'v2': {
                'current_policy': {'lane_passed': True},
                'patched_policy': {'lane_passed': True},
            },
            'v3': {
                'current_policy': {'lane_passed': False},
                'patched_policy': {'lane_passed': True},
            },
        },
    }
    bad_missing_v3 = {
        'benchmark_count': 1,
        'benchmarks': {
            'v2': {
                'current_policy': {'lane_passed': True},
                'patched_policy': {'lane_passed': True},
            },
        },
    }
    bad_flat = {
        'benchmark_count': 2,
        'benchmarks': {
            'v2': {
                'current_policy': {'lane_passed': True},
                'patched_policy': {'lane_passed': True},
            },
            'v3': {
                'current_policy': {'lane_passed': True},
                'patched_policy': {'lane_passed': True},
            },
        },
    }

    assert determine_promotion_eval_issue_status(good) == 'done'
    assert determine_promotion_eval_issue_status(bad_missing_v3) == 'todo'
    assert determine_promotion_eval_issue_status(bad_flat) == 'todo'



def test_find_issue_for_payload_prefers_latest_open_issue_by_title_when_identifier_changed():
    issues = [
        {'id': 'old-done', 'identifier': 'TIN-15', 'title': 'Daily Full Funnel Reliability Check', 'status': 'done'},
        {'id': 'latest-open', 'identifier': 'TIN-20', 'title': 'Daily Full Funnel Reliability Check', 'status': 'blocked', 'issueNumber': 20},
        {'id': 'other', 'identifier': 'TIN-22', 'title': 'Daily Preset Performance Snapshot', 'status': 'todo', 'issueNumber': 22},
    ]
    payload = {'identifier': 'TIN-15', 'title': 'Daily Full Funnel Reliability Check'}

    chosen = find_issue_for_payload(issues, payload)

    assert chosen['id'] == 'latest-open'
    assert chosen['identifier'] == 'TIN-20'



def test_find_issue_for_payload_prefers_open_identifier_match_when_title_drifted():
    issues = [
        {'id': 'stale-title', 'identifier': 'TIN-24', 'title': 'Old Promotion Title', 'status': 'todo', 'issueNumber': 24},
        {'id': 'new-title', 'identifier': 'TIN-47', 'title': 'Daily Promotion Evaluation Snapshot', 'status': 'done', 'issueNumber': 47},
    ]
    payload = {'identifier': 'TIN-24', 'title': 'Daily Promotion Evaluation Snapshot'}

    chosen = find_issue_for_payload(issues, payload)

    assert chosen['id'] == 'stale-title'
    assert chosen['identifier'] == 'TIN-24'



def test_find_issue_for_payload_prefers_latest_open_identifier_match_among_duplicates():
    issues = [
        {'id': 'older-open', 'identifier': 'TIN-18', 'title': 'Daily Feedback Draft Triage', 'status': 'todo', 'issueNumber': 18},
        {'id': 'latest-open', 'identifier': 'TIN-18', 'title': 'Daily Feedback Draft Triage', 'status': 'blocked', 'issueNumber': 28},
        {'id': 'done-copy', 'identifier': 'TIN-18', 'title': 'Daily Feedback Draft Triage', 'status': 'done', 'issueNumber': 30},
    ]
    payload = {'identifier': 'TIN-18', 'title': 'Daily Feedback Draft Triage'}

    chosen = find_issue_for_payload(issues, payload)

    assert chosen['id'] == 'latest-open'
    assert chosen['status'] == 'blocked'
