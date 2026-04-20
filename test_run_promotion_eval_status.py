from pathlib import Path
import subprocess


def test_run_promotion_eval_status_cli_prints_summary(tmp_path):
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
    (summary_dir / 'min-hermes-promotion-eval-20260419-010351.md').write_text('# Min Hermes Promotion Eval', encoding='utf-8')
    (summary_dir / 'min-hermes-promotion-eval-20260419-010351.json').write_text('{"benchmarks": {}}', encoding='utf-8')

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_promotion_eval_status.py', '--root', str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'v2' in proc.stdout
    assert 'v3' in proc.stdout
    assert '12/12' in proc.stdout
    assert '0/1' in proc.stdout
