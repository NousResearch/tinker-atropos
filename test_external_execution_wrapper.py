from pathlib import Path
import subprocess

from ops.external_execution import ExecutionSpec, build_execution_plan, render_shell_script


def test_build_execution_plan_adds_rp_and_codex_steps_for_complex_code_tasks():
    spec = ExecutionSpec(
        title='Feedback Patch Draft Review Queue',
        task_type='patch-review',
        prompt='feedback patch 분류 로직 개선',
        targets=['generate_score_patch_v4a.py', 'test_patch_precision.py'],
        use_rp=True,
        test_command='pytest test_patch_precision.py -q',
    )

    plan = build_execution_plan(spec)

    assert plan['context_path'].endswith('.md')
    assert plan['log_path'].endswith('.log')
    assert plan['steps'][0]['kind'] == 'rp'
    assert 'rp-cli build --repo .' in plan['steps'][0]['command']
    assert '--target generate_score_patch_v4a.py --target test_patch_precision.py' in plan['steps'][0]['command']
    assert plan['steps'][1]['kind'] == 'codex'
    assert 'codex exec --context' in plan['steps'][1]['command']
    assert 'feedback patch 분류 로직 개선' in plan['steps'][1]['command']
    assert plan['steps'][2]['kind'] == 'test'
    assert 'pytest test_patch_precision.py -q' == plan['steps'][2]['command']


def test_build_execution_plan_skips_rp_for_lightweight_tasks():
    spec = ExecutionSpec(
        title='Weekly Tinker Research Summary',
        task_type='summary',
        prompt='이번 주 요약 정리',
        use_rp=False,
    )

    plan = build_execution_plan(spec)

    assert [step['kind'] for step in plan['steps']] == ['codex']
    assert '--context' not in plan['steps'][0]['command']


def test_render_shell_script_contains_workdir_and_log_reference():
    spec = ExecutionSpec(
        title='Daily Full Funnel Run Monitor',
        task_type='full-funnel-check',
        prompt='full funnel 출력 점검',
        targets=['run_research_to_full_funnel.py'],
        use_rp=True,
    )

    script = render_shell_script(build_execution_plan(spec))

    assert 'set -euo pipefail' in script
    assert 'cd /Users/heomin/.hermes/hermes-agent/tinker-atropos' in script
    assert 'rp-cli build --repo .' in script
    assert 'codex exec --context' in script
    assert 'tee -a' in script



def test_run_task_cli_prints_plan_when_called_as_script():
    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        [
            'python',
            'ops/run_task.py',
            '--title', 'Feedback Patch Draft Review Queue',
            '--task-type', 'patch-review',
            '--prompt', 'feedback patch 분류 로직 개선',
            '--target', 'generate_score_patch_v4a.py',
            '--use-rp',
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'rp-cli build --repo .' in proc.stdout
    assert 'codex exec --context' in proc.stdout
