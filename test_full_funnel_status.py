from pathlib import Path

from ops.full_funnel_status import collect_full_funnel_status, build_comment_body



def create_summary_run(base: Path, project: str, stem: str = 'sample') -> Path:
    summary = base / 'outputs' / '2026-04-13' / project / 'summary'
    summary.mkdir(parents=True)
    (summary / f'{stem}-best-20260413-100000.json').write_text('{}', encoding='utf-8')
    (summary / f'{stem}-final-20260413-100000.json').write_text('{"x": {}, "landing": {}, "retention": {}}', encoding='utf-8')
    (summary / f'{stem}-report-20260413-100000.md').write_text('# report', encoding='utf-8')
    (summary / f'{stem}-one-line-20260413-100000.txt').write_text('one line', encoding='utf-8')
    return summary



def create_proof_run(base: Path, project: str, stem: str = 'sample') -> Path:
    summary = base / 'outputs' / '2026-04-13' / project / 'summary'
    summary.mkdir(parents=True)
    (summary / f'{stem}-proof-20260413-100000.json').write_text('{}', encoding='utf-8')
    (summary / f'{stem}-proof-20260413-100000.md').write_text('# proof', encoding='utf-8')
    return summary



def test_collect_full_funnel_status_detects_latest_run_and_required_artifacts(tmp_path):
    create_summary_run(tmp_path, 'project-a')

    summary = collect_full_funnel_status(tmp_path)

    assert summary['run_count'] == 1
    assert summary['alert_count'] == 0
    assert summary['latest_run']['project'] == 'project-a'
    assert summary['latest_run']['missing_artifacts'] == []



def test_collect_full_funnel_status_flags_missing_summary_artifacts(tmp_path):
    summary_dir = create_summary_run(tmp_path, 'project-b')
    (summary_dir / 'sample-one-line-20260413-100000.txt').unlink()

    summary = collect_full_funnel_status(tmp_path)

    assert summary['alert_count'] == 1
    assert 'missing artifact' in summary['alerts'][0]
    assert 'one-line' in summary['latest_run']['missing_artifacts'][0]



def test_collect_full_funnel_status_ignores_configured_legacy_missing_artifacts(tmp_path):
    summary_dir = create_summary_run(tmp_path, 'ordinarybiz-quality6')
    (summary_dir / 'sample-one-line-20260413-100000.txt').unlink()

    summary = collect_full_funnel_status(tmp_path)

    assert summary['alert_count'] == 0
    assert summary['latest_run']['missing_artifacts'] == []
    assert summary['latest_run']['allowed_missing_artifacts'] == ['one-line']



def test_collect_full_funnel_status_ignores_non_full_funnel_proof_projects(tmp_path):
    create_summary_run(tmp_path, 'project-a')
    create_proof_run(tmp_path, 'default-public-ready', stem='default_public_normal_lite')

    summary = collect_full_funnel_status(tmp_path)

    assert summary['run_count'] == 1
    assert summary['alert_count'] == 0
    assert summary['latest_run']['project'] == 'project-a'


def test_collect_full_funnel_status_ignores_promotion_eval_projects(tmp_path):
    create_summary_run(tmp_path, 'project-a')
    promotion_summary = tmp_path / 'outputs' / '2026-04-13' / 'promotion-eval' / 'summary'
    promotion_summary.mkdir(parents=True)
    (promotion_summary / 'min-hermes-promotion-eval-20260413-100000.json').write_text('{"benchmarks": {}}', encoding='utf-8')
    (promotion_summary / 'min-hermes-promotion-eval-20260413-100000.md').write_text('# Min Hermes Promotion Eval', encoding='utf-8')

    summary = collect_full_funnel_status(tmp_path)

    assert summary['run_count'] == 1
    assert summary['alert_count'] == 0
    assert summary['latest_run']['project'] == 'project-a'


def test_build_comment_body_includes_latest_run_and_alerts(tmp_path):
    summary_dir = create_summary_run(tmp_path, 'project-c')
    (summary_dir / 'sample-report-20260413-100000.md').unlink()

    summary = collect_full_funnel_status(tmp_path)
    comment = build_comment_body(summary)

    assert 'run_count: 1' in comment
    assert 'latest_project: project-c' in comment
    assert 'alert_count: 1' in comment
    assert 'missing artifact' in comment
