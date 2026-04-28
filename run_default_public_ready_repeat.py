import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')


def parse_step(step_text: str | None) -> tuple[int, int]:
    if not step_text or '/' not in step_text:
        return (-1, -1)
    left, right = step_text.split('/', 1)
    try:
        return (int(left), int(right))
    except ValueError:
        return (-1, -1)


def aggregate_runs(runs: list[dict]) -> dict:
    working_runs = [run for run in runs if run.get('assessment', {}).get('working') is True]
    datum_objects = [run.get('trainer', {}).get('got_datum_objects') for run in working_runs if run.get('trainer', {}).get('got_datum_objects') is not None]
    reward_means = [run.get('trainer', {}).get('reward_mean') for run in working_runs if run.get('trainer', {}).get('reward_mean') is not None]
    steps = [run.get('trainer', {}).get('last_step') for run in working_runs if run.get('trainer', {}).get('last_step')]
    max_step = None
    if steps:
        max_step = max(steps, key=parse_step)
    return {
        'run_count': len(runs),
        'working_count': len(working_runs),
        'working_rate': round(len(working_runs) / len(runs), 4) if runs else 0.0,
        'status_counts': {
            status: sum(1 for run in runs if run.get('assessment', {}).get('status') == status)
            for status in sorted({run.get('assessment', {}).get('status') for run in runs})
        },
        'max_last_step': max_step,
        'datum_objects_observed': datum_objects,
        'reward_means': reward_means,
    }


def main():
    repeat = int(os.environ.get('DEFAULT_PUBLIC_READY_REPEAT', '3'))
    config = os.environ.get('DEFAULT_PUBLIC_READY_CONFIG', 'configs/default_public_normal_lite.yaml')
    timeout = os.environ.get('DEFAULT_PUBLIC_READY_TIMEOUT', '120')
    runs = []
    for _ in range(repeat):
        proc = subprocess.run(
            ['python', 'run_default_public_ready_smoke.py'],
            cwd=ROOT,
            env={**os.environ, 'DEFAULT_PUBLIC_READY_CONFIG': config, 'DEFAULT_PUBLIC_READY_TIMEOUT': timeout},
            capture_output=True,
            text=True,
            check=True,
        )
        runs.append(json.loads(proc.stdout))

    summary = {
        'config': config,
        'repeat': repeat,
        'aggregate': aggregate_runs(runs),
        'runs': runs,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
