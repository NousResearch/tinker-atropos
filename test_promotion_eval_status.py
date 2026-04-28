from pathlib import Path

from ops.promotion_eval_status import build_comment_body, collect_promotion_eval_status


def test_collect_promotion_eval_status_reads_v2_v3_and_latest_artifacts(tmp_path):
    research = tmp_path / 'research'
    research.mkdir(parents=True)
    (research / 'min_hermes_offline_eval_v2_scoreboard.md').write_text(
        "| lane | mean_total | pass_rate | task_pass_count | lane_passed |\n"
        "| --- | ---: | ---: | ---: | --- |\n"
        "| current_policy | 0.9979 | 1.0000 | 12/12 | yes |\n"
        "| patched_policy | 0.9924 | 1.0000 | 12/12 | yes |\n",
        encoding='utf-8',
    )
    (research / 'min_hermes_offline_eval_v3_scoreboard.md').write_text(
        "| lane | mean_total | pass_rate | task_pass_count | lane_passed |\n"
        "| --- | ---: | ---: | ---: | --- |\n"
        "| current_policy | 0.9750 | 0.0000 | 0/1 | no |\n"
        "| patched_policy | 0.9800 | 1.0000 | 1/1 | yes |\n",
        encoding='utf-8',
    )
    summary_dir = tmp_path / 'outputs' / '2026-04-19' / 'promotion-eval' / 'summary'
    summary_dir.mkdir(parents=True)
    (summary_dir / 'min-hermes-promotion-eval-20260419-010351.json').write_text('{"benchmarks": {}}', encoding='utf-8')
    (summary_dir / 'min-hermes-promotion-eval-20260419-010351.md').write_text('# Min Hermes Promotion Eval', encoding='utf-8')

    summary = collect_promotion_eval_status(tmp_path)

    assert summary['benchmark_count'] == 2
    assert summary['latest_summary_json'].endswith('010351.json')
    assert summary['latest_summary_markdown'].endswith('010351.md')
    assert summary['benchmarks']['v2']['current_policy']['lane_passed'] is True
    assert summary['benchmarks']['v3']['current_policy']['lane_passed'] is False
    assert summary['benchmarks']['v3']['patched_policy']['task_pass_count'] == '1/1'


def test_build_comment_body_summarizes_v2_and_v3_promotion_state():
    summary = {
        'benchmark_count': 2,
        'latest_summary_json': 'outputs/2026-04-19/promotion-eval/summary/min-hermes-promotion-eval-20260419-010351.json',
        'latest_summary_markdown': 'outputs/2026-04-19/promotion-eval/summary/min-hermes-promotion-eval-20260419-010351.md',
        'alert_count': 0,
        'alerts': [],
        'benchmarks': {
            'v2': {
                'current_policy': {'mean_total': 0.9979, 'task_pass_count': '12/12', 'lane_passed': True},
                'patched_policy': {'mean_total': 0.9924, 'task_pass_count': '12/12', 'lane_passed': True},
            },
            'v3': {
                'current_policy': {'mean_total': 0.9750, 'task_pass_count': '0/1', 'lane_passed': False},
                'patched_policy': {'mean_total': 0.9800, 'task_pass_count': '1/1', 'lane_passed': True},
            },
        },
    }

    text = build_comment_body(summary)

    assert 'benchmark_count: 2' in text
    assert 'alert_count: 0' in text
    assert '- v2:' in text
    assert 'current_policy mean_total=0.9979' in text
    assert 'v3' in text
    assert 'patched_policy mean_total=0.9800' in text
    assert '0/1' in text
    assert 'latest_summary_json:' in text



def test_collect_promotion_eval_status_flags_missing_v3_and_missing_markdown_artifact(tmp_path):
    research = tmp_path / 'research'
    research.mkdir(parents=True)
    (research / 'min_hermes_offline_eval_v2_scoreboard.md').write_text(
        "| lane | mean_total | pass_rate | task_pass_count | lane_passed |\n"
        "| --- | ---: | ---: | ---: | --- |\n"
        "| current_policy | 0.9979 | 1.0000 | 12/12 | yes |\n",
        encoding='utf-8',
    )
    summary_dir = tmp_path / 'outputs' / '2026-04-19' / 'promotion-eval' / 'summary'
    summary_dir.mkdir(parents=True)
    (summary_dir / 'min-hermes-promotion-eval-20260419-010351.json').write_text('{"benchmarks": {}}', encoding='utf-8')

    summary = collect_promotion_eval_status(tmp_path)

    assert summary['benchmark_count'] == 1
    assert summary['alert_count'] == 2
    assert 'missing_benchmark:v3' in summary['alerts']
    assert 'missing_summary_markdown' in summary['alerts']



def test_collect_promotion_eval_status_marks_artifact_freshness_and_summary_pair_match(tmp_path):
    research = tmp_path / 'research'
    research.mkdir(parents=True)
    for name in ('v2', 'v3'):
        (research / f'min_hermes_offline_eval_{name}_scoreboard.md').write_text(
            "| lane | mean_total | pass_rate | task_pass_count | lane_passed |\n"
            "| --- | ---: | ---: | ---: | --- |\n"
            "| current_policy | 0.9979 | 1.0000 | 12/12 | yes |\n",
            encoding='utf-8',
        )
    summary_dir = tmp_path / 'outputs' / '2026-04-19' / 'promotion-eval' / 'summary'
    summary_dir.mkdir(parents=True)
    json_path = summary_dir / 'min-hermes-promotion-eval-20260419-010351.json'
    md_path = summary_dir / 'min-hermes-promotion-eval-20260419-010351.md'
    json_path.write_text('{"benchmarks": {}}', encoding='utf-8')
    md_path.write_text('# Min Hermes Promotion Eval', encoding='utf-8')

    summary = collect_promotion_eval_status(tmp_path)

    assert summary['summary_pair_matched'] is True
    assert summary['latest_summary_json_age_seconds'] is not None
    assert summary['latest_summary_markdown_age_seconds'] is not None
    assert summary['latest_summary_json_fresh'] is True
    assert summary['latest_summary_markdown_fresh'] is True
