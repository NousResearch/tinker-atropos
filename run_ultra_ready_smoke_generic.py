import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
ENV = os.environ.copy()


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


def pkill_pattern(pattern: str):
    subprocess.run(
        ['bash', '-lc', f'pkill -f "{pattern}" || true'],
        cwd=ROOT,
        env=ENV,
        capture_output=True,
        text=True,
    )


def restart_run_api():
    pkill_pattern('/Users/heomin/.hermes/hermes-agent/venv/bin/run-api')
    subprocess.run(['bash', '-lc', 'lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true'], cwd=ROOT, env=ENV, capture_output=True, text=True)
    proc = subprocess.Popen(
        ['bash', '-lc', 'source /Users/heomin/.hermes/hermes-agent/venv/bin/activate && PYTHONUNBUFFERED=1 run-api'],
        cwd=ROOT,
        env=ENV,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    return proc


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


def main():
    if len(sys.argv) not in (6, 7):
        print(
            'usage: python run_ultra_ready_smoke_generic.py <name> <env_py> <cfg> <env_var_name> <env_var_value> [timeout_seconds]',
            file=sys.stderr,
        )
        sys.exit(2)

    name, env_py, cfg, env_var_name, env_var_value = sys.argv[1:6]
    timeout_seconds = int(sys.argv[6]) if len(sys.argv) == 7 else 240
    trainer_log = ROOT / 'smoke_logs' / f'{name}_trainer.log'
    env_log = ROOT / 'smoke_logs' / f'{name}_env.log'
    trainer_log.parent.mkdir(parents=True, exist_ok=True)

    pkill_pattern(f'{Path(env_py).name} serve')
    pkill_pattern(f'launch_training.py --config {cfg}')
    time.sleep(2)
    kill_port(8001)
    run_api_proc = restart_run_api()

    run_env = ENV.copy()
    run_env[env_var_name] = env_var_value

    with trainer_log.open('w') as tf:
        trainer = subprocess.Popen(
            ['python', '-u', 'launch_training.py', '--config', cfg, '--no-wandb'],
            cwd=ROOT,
            env=run_env,
            stdout=tf,
            stderr=subprocess.STDOUT,
        )

    ready, health = wait_health_ready()

    with env_log.open('w') as ef:
        env_proc = subprocess.Popen(
            ['python', '-u', env_py, 'serve', '--config', cfg],
            cwd=ROOT,
            env=run_env,
            stdout=ef,
            stderr=subprocess.STDOUT,
        )

    success, trainer_text = wait_done(trainer_log, trainer, 'Training completed successfully!', timeout=timeout_seconds)

    summary = {
        'name': name,
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
    if run_api_proc.poll() is None:
        run_api_proc.kill()
        try:
            run_api_proc.wait(timeout=5)
        except Exception:
            pass

    summary['trainer_returncode_final'] = trainer.poll()
    summary['env_returncode_final'] = env_proc.poll()
    summary['run_api_returncode_final'] = run_api_proc.poll()
    summary['trainer_log_tail'] = '\n'.join(trainer_text.splitlines()[-20:]) if trainer_text else ''
    summary['env_log_tail'] = '\n'.join(env_log.read_text(errors='ignore').splitlines()[-20:]) if env_log.exists() else ''
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
