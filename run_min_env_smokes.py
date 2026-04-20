import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
ENV = os.environ.copy()

CASES = [
    ('min_business_strategy', 'tinker_atropos/environments/min_business_strategy_tinker.py', 'configs/min_business_strategy_smoke.yaml'),
    ('min_x_strategy', 'tinker_atropos/environments/min_x_strategy_tinker.py', 'configs/min_x_strategy_smoke.yaml'),
    ('min_landing_cro', 'tinker_atropos/environments/min_landing_cro_tinker.py', 'configs/min_landing_cro_smoke.yaml'),
    ('min_membership_retention', 'tinker_atropos/environments/min_membership_retention_tinker.py', 'configs/min_membership_retention_smoke.yaml'),
    ('min_agentic_research', 'tinker_atropos/environments/min_agentic_research_tinker.py', 'configs/min_agentic_research_smoke.yaml'),
]


def kill_port_8001():
    proc = subprocess.run(
        ['bash', '-lc', 'lsof -tiTCP:8001 -sTCP:LISTEN || true'],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=ENV,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                os.kill(int(line), signal.SIGKILL)
            except ProcessLookupError:
                pass


def grab(pattern: str, text: str):
    match = re.search(pattern, text)
    return match.group(1) if match else None


def wait_or_kill(proc: subprocess.Popen, timeout: int):
    try:
        return proc.wait(timeout=timeout), False
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
        return None, True


results = []
for name, env_py, cfg in CASES:
    logdir = ROOT / 'smoke_logs' / name
    logdir.mkdir(parents=True, exist_ok=True)
    trainer_log = logdir / 'trainer.log'
    env_log = logdir / 'env.log'

    kill_port_8001()
    time.sleep(1)

    with trainer_log.open('w') as tf:
        trainer = subprocess.Popen(
            ['python', '-u', 'launch_training.py', '--config', cfg, '--no-wandb'],
            cwd=ROOT,
            env=ENV,
            stdout=tf,
            stderr=subprocess.STDOUT,
        )

    time.sleep(8)

    with env_log.open('w') as ef:
        env_proc = subprocess.Popen(
            ['python', '-u', env_py, 'serve', '--config', cfg],
            cwd=ROOT,
            env=ENV,
            stdout=ef,
            stderr=subprocess.STDOUT,
        )
        env_rc, env_timed_out = wait_or_kill(env_proc, timeout=120)

    trainer_rc, trainer_timed_out = wait_or_kill(trainer, timeout=120)

    t = trainer_log.read_text(errors='ignore')
    e = env_log.read_text(errors='ignore')
    last_trainer_lines = '\n'.join(t.splitlines()[-8:])
    results.append({
        'name': name,
        'trainer_registered': 'Registered as trainer:' in t,
        'got_datum_objects': grab(r'Got (\d+) Datum objects', t),
        'loss': grab(r'Loss: ([0-9.]+)', t),
        'reward_mean': grab(r'Reward/mean: ([0-9.]+)', t),
        'weights': grab(r'Final weights are available here: (tinker://\S+)', t),
        'trainer_success': 'Training completed successfully!' in t,
        'trainer_rc': trainer_rc,
        'trainer_timed_out': trainer_timed_out,
        'env_started': 'BaseEnvConfig(' in e,
        'env_rc': env_rc,
        'env_timed_out': env_timed_out,
        'trainer_tail': last_trainer_lines,
    })

print(json.dumps(results, ensure_ascii=False, indent=2))
