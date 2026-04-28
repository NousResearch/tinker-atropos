from pathlib import Path

from ops.promotion_eval_daily import build_daily_report, run_daily


def sample_status_summary() -> dict:
    return {
        'benchmark_count': 2,
        'benchmarks': {
            'v2': {
                'current_policy': {
                    'lane_passed': True,
                    'task_pass_count': '12/12',
                    'mean_total': 0.9979,
                },
                'patched_policy': {
                    'lane_passed': True,
                    'task_pass_count': '12/12',
                    'mean_total': 0.9924,
                },
            },
            'v3': {
                'current_policy': {
                    'lane_passed': False,
                    'task_pass_count': '0/1',
                    'mean_total': 0.975,
                },
                'patched_policy': {
                    'lane_passed': True,
                    'task_pass_count': '1/1',
                    'mean_total': 0.98,
                },
            },
        },
        'alert_count': 0,
        'alerts': [],
        'latest_summary_json_fresh': True,
        'latest_summary_markdown_fresh': True,
        'summary_pair_matched': True,
        'latest_summary_json': '/tmp/min-hermes-promotion-eval.json',
        'latest_summary_markdown': '/tmp/min-hermes-promotion-eval.md',
    }


def sample_sync_results() -> list[dict]:
    return [
        {'identifier': 'TIN-18', 'updated': True, 'status': 'done', 'issue_id': 'feedback-id'},
        {'identifier': 'TIN-24', 'updated': True, 'status': 'done', 'issue_id': 'promotion-id'},
    ]


def test_build_daily_report_includes_latest_paths_v2_v3_and_promotion_sync():
    text = build_daily_report(sample_status_summary(), sample_sync_results())

    assert 'tinker-atropos-promotion-eval-daily' in text
    assert 'alert_count: 0' in text
    assert 'summary_pair_matched: True' in text
    assert 'latest_summary_json_fresh: True' in text
    assert 'latest_summary_markdown_fresh: True' in text
    assert 'latest_summary_json: /tmp/min-hermes-promotion-eval.json' in text
    assert 'latest_summary_markdown: /tmp/min-hermes-promotion-eval.md' in text
    assert 'v2 current_policy: lane_passed=True task_pass_count=12/12 mean_total=0.9979' in text
    assert 'v2 patched_policy: lane_passed=True task_pass_count=12/12 mean_total=0.9924' in text
    assert 'v3 current_policy: lane_passed=False task_pass_count=0/1 mean_total=0.975' in text
    assert 'v3 patched_policy: lane_passed=True task_pass_count=1/1 mean_total=0.98' in text
    assert 'paperclip promotion sync: updated=True status=done issue_id=promotion-id' in text


def test_run_daily_uses_repo_helpers_and_returns_plaintext_report(monkeypatch, tmp_path: Path):
    collected = []

    def fake_generate(root: Path) -> dict:
        collected.append(('generate', root))
        return {'summary_artifacts': {'json': '/tmp/generated.json', 'markdown': '/tmp/generated.md'}}

    def fake_sync(root: Path, base_url: str, company_id: str, dry_run: bool = False) -> dict:
        collected.append(('sync', root, base_url, company_id, dry_run))
        return {'company_id': company_id, 'root': str(root), 'results': sample_sync_results()}

    monkeypatch.setattr('ops.promotion_eval_daily.generate_promotion_eval_summary', fake_generate)
    monkeypatch.setattr('ops.promotion_eval_daily.sync_tinker_cards', fake_sync)
    monkeypatch.setattr('ops.promotion_eval_daily.collect_promotion_eval_status', lambda root: sample_status_summary())

    result = run_daily(tmp_path, base_url='http://127.0.0.1:3100', company_id='company-123', dry_run=True)

    assert collected[0] == ('generate', tmp_path)
    assert collected[1] == ('sync', tmp_path, 'http://127.0.0.1:3100', 'company-123', True)
    assert result['sync']['company_id'] == 'company-123'
    assert result['status_summary']['benchmark_count'] == 2
    assert 'tinker-atropos-promotion-eval-daily' in result['report']
