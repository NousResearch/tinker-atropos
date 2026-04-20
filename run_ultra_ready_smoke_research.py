import json
import os
import signal
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
ENV = os.environ.copy()
TRAINER_LOG = ROOT / 'smoke_logs' / 'ultra_ready_research_trainer.log'
ENV_LOG = ROOT / 'smoke_logs' / 'ultra_ready_research_env.log'
CFG = 'configs/min_agentic_research_ultra_smoke.yaml'
ENV_PY = 'tinker_atropos/environments/min_agentic_research_tinker.py'


def kill_port(port: int):
    proc = subprocess.run(
        ['bash', '-lc', f'lsof -tiTCP:{port} -sTCP:LISTEN || true'],
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


def kill_stale_research_processes():
    subprocess.run(
        ['bash', '-lc', 'pkill -f "min_agentic_research_tinker.py serve" || true; pkill -f "launch_training.py --config configs/min_agentic_research" || true'],
        cwd=ROOT,
        env=ENV,
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


def wait_done(proc: subprocess.Popen, success_marker: str, timeout=240):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if TRAINER_LOG.exists():
            text = TRAINER_LOG.read_text(errors='ignore')
            if success_marker in text:
                return True, text
        if proc.poll() is not None:
            text = TRAINER_LOG.read_text(errors='ignore') if TRAINER_LOG.exists() else ''
            return False, text
        time.sleep(3)
    text = TRAINER_LOG.read_text(errors='ignore') if TRAINER_LOG.exists() else ''
    return False, text


(TRAINER_LOG.parent).mkdir(parents=True, exist_ok=True)
kill_stale_research_processes()
time.sleep(2)
kill_port(8001)

with TRAINER_LOG.open('w') as tf:
    trainer = subprocess.Popen(
        ['python', '-u', 'launch_training.py', '--config', CFG, '--no-wandb'],
        cwd=ROOT,
        env=ENV,
        stdout=tf,
        stderr=subprocess.STDOUT,
    )

ready, health = wait_health_ready()

with ENV_LOG.open('w') as ef:
    env_proc = subprocess.Popen(
        ['python', '-u', ENV_PY, 'serve', '--config', CFG],
        cwd=ROOT,
        env=ENV,
        stdout=ef,
        stderr=subprocess.STDOUT,
    )

success, trainer_text = wait_done(trainer, 'Training completed successfully!')

summary = {
    'health_ready': ready,
    'health_payload': health,
    'trainer_success': success,
    'trainer_returncode': trainer.poll(),
    'env_returncode': env_proc.poll(),
}

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

summary['trainer_returncode_final'] = trainer.poll()
summary['env_returncode_final'] = env_proc.poll()
summary['trainer_log_tail'] = '\n'.join(trainer_text.splitlines()[-20:]) if trainer_text else ''
summary['env_log_tail'] = '\n'.join(ENV_LOG.read_text(errors='ignore').splitlines()[-20:]) if ENV_LOG.exists() else ''
print(json.dumps(summary, ensure_ascii=False, indent=2))
