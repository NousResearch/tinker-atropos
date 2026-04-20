import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
ENV = os.environ.copy()


def run_once(name, env_py, cfg, env_var_name, env_var_value, run_idx):
    cmd = [
        'python', 'run_ultra_ready_smoke_generic.py',
        f'{name}_run{run_idx}', env_py, cfg, env_var_name, env_var_value
    ]
    proc = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True)
    payload = json.loads(proc.stdout)
    payload['run'] = run_idx
    return payload


def main():
    if len(sys.argv) != 7:
        print('usage: python run_repeat_generic.py <name> <env_py> <cfg> <env_var_name> <env_var_value> <repeat_count>', file=sys.stderr)
        sys.exit(2)
    name, env_py, cfg, env_var_name, env_var_value, repeat_count = sys.argv[1:]
    repeat_count = int(repeat_count)
    results = []
    for idx in range(1, repeat_count + 1):
        results.append(run_once(name, env_py, cfg, env_var_name, env_var_value, idx))
    print(json.dumps({'name': name, 'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
