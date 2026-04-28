from pathlib import Path

from ops.environment_status import collect_environment_status, build_comment_body



def test_collect_environment_status_reports_env_tests_and_configs(tmp_path):
    root = tmp_path
    env_dir = root / 'tinker_atropos' / 'environments'
    test_dir = root / 'tinker_atropos' / 'tests'
    cfg_dir = root / 'configs'
    outputs_dir = root / 'outputs' / 'business'
    drafts_dir = root / 'feedback' / 'patch_drafts'

    env_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)
    cfg_dir.mkdir(parents=True)
    outputs_dir.mkdir(parents=True)
    drafts_dir.mkdir(parents=True)

    (env_dir / 'min_business_strategy_tinker.py').write_text('x', encoding='utf-8')
    (test_dir / 'test_min_business_strategy_env.py').write_text('x', encoding='utf-8')
    (cfg_dir / 'min_business_strategy_smoke.yaml').write_text('x', encoding='utf-8')
    (cfg_dir / 'min_business_strategy_ultra_smoke.yaml').write_text('x', encoding='utf-8')
    (env_dir / 'min_design_system_operator_tinker.py').write_text('x', encoding='utf-8')
    (test_dir / 'test_min_design_system_operator_env.py').write_text('x', encoding='utf-8')
    (cfg_dir / 'min_design_system_operator_ultra_smoke.yaml').write_text('x', encoding='utf-8')
    (outputs_dir / 'sample.json').write_text('{}', encoding='utf-8')
    (drafts_dir / 'score-patch-v4a-20260413-210049.patch').write_text('*** Begin Patch\n*** End Patch\n', encoding='utf-8')

    summary = collect_environment_status(root)

    business = next(item for item in summary['environments'] if item['name'] == 'min_business_strategy')
    design = next(item for item in summary['environments'] if item['name'] == 'min_design_system_operator')
    assert business['env_exists'] is True
    assert business['test_exists'] is True
    assert business['config_count'] == 2
    assert design['env_exists'] is True
    assert design['test_exists'] is True
    assert design['config_count'] == 1
    assert summary['artifacts']['patch_draft_count'] == 1
    assert summary['artifacts']['output_json_count'] == 1



def test_collect_environment_status_marks_missing_assets():
    summary = collect_environment_status(Path('/tmp/nonexistent-tinker-root'))

    business = next(item for item in summary['environments'] if item['name'] == 'min_business_strategy')
    assert business['env_exists'] is False
    assert business['test_exists'] is False
    assert business['config_count'] == 0
    assert summary['artifacts']['patch_draft_count'] == 0



def test_build_comment_body_includes_open_alerts_and_artifact_summary(tmp_path):
    root = tmp_path
    env_dir = root / 'tinker_atropos' / 'environments'
    test_dir = root / 'tinker_atropos' / 'tests'
    cfg_dir = root / 'configs'
    env_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)
    cfg_dir.mkdir(parents=True)

    (env_dir / 'min_business_strategy_tinker.py').write_text('x', encoding='utf-8')
    (cfg_dir / 'min_business_strategy_smoke.yaml').write_text('x', encoding='utf-8')

    summary = collect_environment_status(root)
    comment = build_comment_body(summary)

    assert 'environment_count: 6' in comment
    assert 'alert_count:' in comment
    assert 'missing test: min_business_strategy' in comment
    assert 'artifacts:' in comment
