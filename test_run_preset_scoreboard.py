from pathlib import Path
import subprocess
import json



def test_run_preset_scoreboard_cli_prints_summary(tmp_path):
    summary = tmp_path / 'outputs' / '2026-04-13' / 'preset-round3-youtube' / 'summary'
    summary.mkdir(parents=True)
    data = {
        'business': {'scores': {'total': 0.5}},
        'x': {'scores': {'total': 0.69}},
        'landing': {'scores': {'total': 0.58}, '헤드라인': '유튜브 시청자가 바로 이해하는 신뢰 근거 제안'},
        'retention': {'scores': {'total': 0.60}},
    }
    (summary / 'sample-final-20260413-100000.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_preset_scoreboard.py', '--root', str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'youtube' in proc.stdout
    assert 'preset_count' in proc.stdout
