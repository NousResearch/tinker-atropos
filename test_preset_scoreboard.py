from pathlib import Path
import json

from ops.preset_scoreboard import collect_preset_scoreboard, infer_preset_from_project, build_comment_body



def write_final(root: Path, project: str, x_score: float, landing_score: float, retention_score: float, headline: str):
    summary = root / 'outputs' / '2026-04-13' / project / 'summary'
    summary.mkdir(parents=True)
    data = {
        'business': {'scores': {'total': 0.5}},
        'x': {'scores': {'total': x_score}},
        'landing': {'scores': {'total': landing_score}, '헤드라인': headline},
        'retention': {'scores': {'total': retention_score}},
    }
    (summary / f'{project}-final-20260413-100000.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')



def test_infer_preset_from_project_detects_known_presets():
    assert infer_preset_from_project('batch-ailit-consult-ailit') == 'ailit'
    assert infer_preset_from_project('preset-round3-youtube') == 'youtube'
    assert infer_preset_from_project('ordinarybiz-vip') == 'vip'
    assert infer_preset_from_project('ordinarybiz-main') == 'ordinarybiz'



def test_collect_preset_scoreboard_groups_scores_by_preset(tmp_path):
    write_final(tmp_path, 'preset-round3-youtube', 0.69, 0.58, 0.60, '유튜브 시청자가 바로 이해하는 신뢰 근거 제안')
    write_final(tmp_path, 'preset-round4-ailit', 0.69, 0.56, 0.55, 'Ailit 상담 신청으로 이어지는 신뢰 근거 제안')
    write_final(tmp_path, 'ordinarybiz-main', 0.68, 0.55, 0.59, '부담 없이 신청으로 이어지는 신뢰 근거 제안')

    summary = collect_preset_scoreboard(tmp_path)

    assert summary['preset_count'] == 3
    assert summary['totals']['final_runs'] == 3
    assert summary['presets']['youtube']['run_count'] == 1
    assert summary['presets']['ailit']['avg_landing_score'] == 0.56
    assert summary['presets']['ordinarybiz']['best_landing_headline'] == '부담 없이 신청으로 이어지는 신뢰 근거 제안'



def test_build_comment_body_includes_top_presets(tmp_path):
    write_final(tmp_path, 'preset-round3-youtube', 0.69, 0.58, 0.60, '유튜브 시청자가 바로 이해하는 신뢰 근거 제안')
    write_final(tmp_path, 'preset-round4-ailit', 0.69, 0.56, 0.55, 'Ailit 상담 신청으로 이어지는 신뢰 근거 제안')

    summary = collect_preset_scoreboard(tmp_path)
    comment = build_comment_body(summary)

    assert 'preset_count: 2' in comment
    assert 'youtube' in comment
    assert 'ailit' in comment
    assert 'avg_landing_score' in comment
