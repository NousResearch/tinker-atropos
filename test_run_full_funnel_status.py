from pathlib import Path
import subprocess



def test_run_full_funnel_status_cli_prints_summary(tmp_path):
    summary = tmp_path / 'outputs' / '2026-04-13' / 'project-a' / 'summary'
    summary.mkdir(parents=True)
    (summary / 'sample-final-20260413-100000.json').write_text('{"x": {}, "landing": {}, "retention": {}}', encoding='utf-8')

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_full_funnel_status.py', '--root', str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'project-a' in proc.stdout
    assert 'run_count' in proc.stdout
