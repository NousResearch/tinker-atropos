from pathlib import Path
import json

from ops.weekly_tinker_summary import collect_weekly_summary, build_markdown_summary



def write_final(root: Path, project: str, score: float):
    summary = root / 'outputs' / '2026-04-13' / project / 'summary'
    summary.mkdir(parents=True)
    data = {
        'business': {'scores': {'total': 0.5}},
        'x': {'scores': {'total': 0.69}},
        'landing': {'scores': {'total': score}, '헤드라인': f'{project} 헤드라인'},
        'retention': {'scores': {'total': 0.60}},
    }
    (summary / f'{project}-final-20260413-100000.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')



def test_collect_weekly_summary_gathers_core_operational_sections(tmp_path):
    write_final(tmp_path, 'preset-round3-youtube', 0.58)
    drafts = tmp_path / 'feedback' / 'patch_drafts'
    drafts.mkdir(parents=True)
    (drafts / 'score-patch-v4a-20260413-210049.patch').write_text('*** Begin Patch\n*** End Patch\n', encoding='utf-8')
    env_dir = tmp_path / 'tinker_atropos' / 'environments'
    test_dir = tmp_path / 'tinker_atropos' / 'tests'
    cfg_dir = tmp_path / 'configs'
    env_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)
    cfg_dir.mkdir(parents=True)
    (env_dir / 'min_business_strategy_tinker.py').write_text('x', encoding='utf-8')
    (test_dir / 'test_min_business_strategy_env.py').write_text('x', encoding='utf-8')
    (cfg_dir / 'min_business_strategy_smoke.yaml').write_text('x', encoding='utf-8')

    summary = collect_weekly_summary(tmp_path)

    assert 'environment' in summary
    assert 'full_funnel' in summary
    assert 'preset_scoreboard' in summary
    assert 'patch_queue' in summary
    assert summary['preset_scoreboard']['preset_count'] == 1



def test_build_markdown_summary_mentions_top_candidate_and_best_preset(tmp_path):
    write_final(tmp_path, 'preset-round3-youtube', 0.58)
    write_final(tmp_path, 'preset-round4-ailit', 0.56)
    drafts = tmp_path / 'feedback' / 'patch_drafts'
    drafts.mkdir(parents=True)
    (drafts / 'score-patch-v4a-20260413-210049.patch').write_text('*** Begin Patch\n*** End Patch\n', encoding='utf-8')

    summary = collect_weekly_summary(tmp_path)
    text = build_markdown_summary(summary)

    assert '# Weekly Tinker Research Summary' in text
    assert 'top_review_candidate' in text
    assert 'preset scoreboard' in text.lower()
    assert 'youtube' in text or 'ailit' in text
