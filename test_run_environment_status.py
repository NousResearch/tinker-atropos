from pathlib import Path
import subprocess



def test_run_environment_status_cli_prints_summary(tmp_path):
    root = tmp_path
    env_dir = root / 'tinker_atropos' / 'environments'
    env_dir.mkdir(parents=True)
    (env_dir / 'min_business_strategy_tinker.py').write_text('x', encoding='utf-8')

    project_root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'ops/run_environment_status.py', '--root', str(root)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'min_business_strategy' in proc.stdout
    assert 'environment_count' in proc.stdout
