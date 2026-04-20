import json
import os
import signal
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
BASE_ENV = os.environ.copy()
OUT_DIR = ROOT / 'smoke_logs' / 'compare_business_x'
OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {
        'name': 'business',
        'cfg': 'configs/min_business_strategy_ultra_smoke.yaml',
        'env_py': 'tinker_atropos/environments/min_business_strategy_tinker.py',
        'ultra_var': 'MIN_BUSINESS_ULTRA_SMOKE',
        'ultra_val': '1',
        'cleanup_patterns': [
            'min_business_strategy_tinker.py serve',
            'launch_training.py --config configs/min_business_strategy',
        ],
    },
    {
        'name': 'x',
        'cfg': 'configs/min_x_strategy_ultra_smoke.yaml',
        'env_py': 'tinker_atropos/environments/min_x_strategy_tinker.py',
        'ultra_var': 'MIN_X_ULTRA_SMOKE',
        'ultra_val': '1',
        'cleanup_patterns': [
            'min_x_strategy_tinker.py serve',
            'launch_training.py --config configs/min_x_strategy',
        ],
    },
]


def kill_port(port: int):
    proc = subprocess.run(
        ['bash', '-lc', f'lsof -tiTCP:{port} -sTCP:LISTEN || true'],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=BASE_ENV,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                os.kill(int(line), signal.SIGKILL)
            except ProcessLookupError:
                pass


def pkill_pattern(pattern: str):
    subprocess.run(
        ['bash', '-lc', f'pkill -f "{pattern}" || true'],
        cwd=ROOT,
        env=BASE_ENV,
        capture_output=True,
        text=True,
    )


def wait_health_ready(timeout=180):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            with urlopen('http://127.0.0.1:8001/health', timeout=3) as resp:
                data = json.loads(resp.read().decode())
                last = data
                if data.get('trainer_ready') is True:
                    return True, data
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, ConnectionResetError, OSError):
            pass
        time.sleep(2)
    return False, last


def wait_done(log_path: Path, proc: subprocess.Popen, success_marker: str, timeout=240):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log_path.exists():
            text = log_path.read_text(errors='ignore')
            if success_marker in text:
                return True, text
        if proc.poll() is not None:
            text = log_path.read_text(errors='ignore') if log_path.exists() else ''
            return False, text
        time.sleep(3)
    text = log_path.read_text(errors='ignore') if log_path.exists() else ''
    return False, text


def grab(pattern: str, text: str):
    import re
    m = re.search(pattern, text)
    return m.group(1) if m else None


def run_case(case: dict, run_idx: int):
    for pattern in case['cleanup_patterns']:
        pkill_pattern(pattern)
    time.sleep(2)
    kill_port(8001)

    env = BASE_ENV.copy()
    env[case['ultra_var']] = case['ultra_val']

    trainer_log = OUT_DIR / f"{case['name']}_run{run_idx}_trainer.log"
    env_log = OUT_DIR / f"{case['name']}_run{run_idx}_env.log"

    with trainer_log.open('w') as tf:
        trainer = subprocess.Popen(
            ['python', '-u', 'launch_training.py', '--config', case['cfg'], '--no-wandb'],
            cwd=ROOT,
            env=env,
            stdout=tf,
            stderr=subprocess.STDOUT,
        )

    ready, health = wait_health_ready()

    with env_log.open('w') as ef:
        env_proc = subprocess.Popen(
            ['python', '-u', case['env_py'], 'serve', '--config', case['cfg']],
            cwd=ROOT,
            env=env,
            stdout=ef,
            stderr=subprocess.STDOUT,
        )

    success, trainer_text = wait_done(trainer_log, trainer, 'Training completed successfully!', timeout=240)

    if env_proc.poll() is None:
        env_proc.kill()
        try:
            env_proc.wait(timeout=5)
        except Exception:
            pass
    if trainer.poll() is None:
        trainer.kill()
        try:
            trainer.wait(timeout=5)
        except Exception:
            pass

    result = {
        'name': case['name'],
        'run': run_idx,
        'health_ready': ready,
        'trainer_success': success,
        'trainer_returncode': trainer.poll(),
        'env_returncode': env_proc.poll(),
        'datum_objects': grab(r'Got (\d+) Datum objects', trainer_text),
        'loss': grab(r'Loss: ([0-9.]+)', trainer_text),
        'reward_mean': grab(r'Reward/mean: ([0-9.]+)', trainer_text),
        'weights': grab(r'Final weights are available here: (tinker://\S+)', trainer_text),
    }
    return result


results = []
for run_idx in range(1, 4):
    for case in CASES:
        results.append(run_case(case, run_idx))

summary = {'results': results}
print(json.dumps(summary, ensure_ascii=False, indent=2))
