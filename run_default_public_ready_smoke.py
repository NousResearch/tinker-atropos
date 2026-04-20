import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
ENV = os.environ.copy()
DEFAULT_CONFIG = 'configs/default.yaml'
DEFAULT_ENV_PY = 'tinker_atropos/environments/gsm8k_tinker.py'
RUN_API_PATTERN = '/Users/heomin/.hermes/hermes-agent/venv/bin/run-api'


def load_run_settings() -> dict:
    config = os.environ.get('DEFAULT_PUBLIC_READY_CONFIG', DEFAULT_CONFIG)
    env_py = os.environ.get('DEFAULT_PUBLIC_READY_ENV_PY', DEFAULT_ENV_PY)
    timeout_seconds = int(os.environ.get('DEFAULT_PUBLIC_READY_TIMEOUT', '180'))
    config_stem = Path(config).stem
    return {
        'config': config,
        'env_py': env_py,
        'timeout_seconds': timeout_seconds,
        'config_stem': config_stem,
        'trainer_pattern': f'launch_training.py --config {config}',
        'env_pattern': f'{Path(env_py).name} serve --config {config}',
    }


def grab(pattern: str, text: str):
    match = re.search(pattern, text)
    return match.group(1) if match else None


def grab_last(pattern: str, text: str):
    matches = re.findall(pattern, text)
    if not matches:
        return None
    last = matches[-1]
    if isinstance(last, tuple):
        return last[0]
    return last


def summarize_trainer_text(text: str) -> dict:
    reward = grab_last(r'Reward/mean: ([0-9.]+)', text)
    datum = grab_last(r'Got (\d+) Datum objects', text)
    loss = grab_last(r'Loss: ([0-9.]+)', text)
    return {
        'registered': 'Registered as trainer:' in text,
        'last_step': grab_last(r'Step (\d+/\d+)', text),
        'got_datum_objects': int(datum) if datum else None,
        'loss': float(loss) if loss else None,
        'reward_mean': float(reward) if reward else None,
        'completed': 'Training completed successfully!' in text,
        'final_weights': grab(r'Final weights are available here: (tinker://\S+)', text),
        'killed_9': 'Killed: 9' in text or 'exit_code": 137' in text,
    }


def has_useful_progress(text: str) -> bool:
    summary = summarize_trainer_text(text)
    if summary['completed']:
        return True
    if (summary['got_datum_objects'] or 0) > 0:
        return True
    if summary['reward_mean'] is not None and summary['reward_mean'] > 0:
        return True
    return False


def summarize_env_text(text: str) -> dict:
    return {
        'started': 'BaseEnvConfig(' in text,
        'connect_8000_failed': 'Cannot connect to host localhost:8000' in text,
        'traceback': 'Traceback (most recent call last):' in text,
        'collect_trajectories_retry_error': 'Error in collect_trajectories: RetryError' in text,
        'worker_done_count': len(re.findall(r'worker_done:', text)),
    }


def assess_run(health_ready: bool, trainer_progress_seen: bool, trainer_summary: dict, env_summary: dict) -> dict:
    if env_summary.get('connect_8000_failed'):
        return {
            'working': False,
            'status': 'run_api_disconnect',
            'reason': 'environment lost connection to rollout server on localhost:8000',
        }
    if env_summary.get('traceback') and not trainer_progress_seen:
        return {
            'working': False,
            'status': 'environment_traceback',
            'reason': 'environment raised a traceback before useful trainer progress was observed',
        }
    if not health_ready:
        return {
            'working': False,
            'status': 'trainer_not_ready',
            'reason': 'trainer health endpoint never reached trainer_ready=true',
        }
    if trainer_progress_seen and trainer_summary.get('registered') and env_summary.get('started'):
        return {
            'working': True,
            'status': 'working',
            'reason': 'trainer registered, useful progress was observed, and environment started without rollout disconnect',
        }
    return {
        'working': False,
        'status': 'insufficient_progress',
        'reason': 'runner did not observe enough evidence to mark the default path healthy',
    }


def build_report_markdown(summary: dict) -> str:
    trainer = summary.get('trainer', {})
    env_summary = summary.get('environment_summary', {})
    assessment = summary.get('assessment', {})
    cleanup = summary.get('cleanup_applied', {})
    lines = [
        '# Default Public Ready Smoke Report',
        '',
        f"- config: {summary.get('config')}",
        f"- environment: {summary.get('environment')}",
        f"- status: {assessment.get('status')}",
        f"- working: {assessment.get('working')}",
        f"- reason: {assessment.get('reason')}",
        f"- health_ready: {summary.get('health_ready')}",
        f"- trainer_progress_seen: {summary.get('trainer_progress_seen')}",
        f"- trainer_registered: {trainer.get('registered')}",
        f"- trainer_last_step: {trainer.get('last_step')}",
        f"- trainer_got_datum_objects: {trainer.get('got_datum_objects')}",
        f"- trainer_reward_mean: {trainer.get('reward_mean')}",
        f"- env_started: {env_summary.get('started')}",
        f"- env_connect_8000_failed: {env_summary.get('connect_8000_failed')}",
        f"- env_traceback: {env_summary.get('traceback')}",
        '',
        '## Cleanup distinction',
        '',
        f"- trainer_active_before_cleanup: {summary.get('trainer_active_before_cleanup')}",
        f"- env_active_before_cleanup: {summary.get('env_active_before_cleanup')}",
        f"- run_api_active_before_cleanup: {summary.get('run_api_active_before_cleanup')}",
        f"- cleanup_applied: {cleanup}",
        '',
        '## Log paths',
        '',
        f"- trainer_log_path: {summary.get('trainer_log_path')}",
        f"- env_log_path: {summary.get('env_log_path')}",
    ]
    return '\n'.join(lines) + '\n'


def save_summary_artifacts(summary: dict, config_stem: str) -> dict:
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    date_folder = time.strftime('%Y-%m-%d')
    summary_dir = ROOT / 'outputs' / date_folder / 'default-public-ready' / 'summary'
    summary_dir.mkdir(parents=True, exist_ok=True)
    json_path = summary_dir / f'{config_stem}-proof-{timestamp}.json'
    md_path = summary_dir / f'{config_stem}-proof-{timestamp}.md'
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    md_path.write_text(build_report_markdown(summary), encoding='utf-8')
    return {
        'json': str(json_path),
        'markdown': str(md_path),
    }


def pkill_pattern(pattern: str):
    subprocess.run(
        ['bash', '-lc', f'pkill -f "{pattern}" || true'],
        cwd=ROOT,
        env=ENV,
        capture_output=True,
        text=True,
    )


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


def restart_run_api():
    pkill_pattern(RUN_API_PATTERN)
    kill_port(8000)
    proc = subprocess.Popen(
        ['bash', '-lc', 'source /Users/heomin/.hermes/hermes-agent/venv/bin/activate && set -a && source /Users/heomin/.hermes/.env && set +a && PYTHONUNBUFFERED=1 run-api'],
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


def wait_for_progress(log_path: Path, proc: subprocess.Popen, timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        text = log_path.read_text(errors='ignore') if log_path.exists() else ''
        if has_useful_progress(text):
            return True, text
        if proc.poll() is not None:
            return False, text
        time.sleep(3)
    text = log_path.read_text(errors='ignore') if log_path.exists() else ''
    return has_useful_progress(text), text


def cleanup_process(proc: subprocess.Popen | None):
    if not proc:
        return False
    if proc.poll() is None:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
        return True
    return False


def main():
    settings = load_run_settings()
    config = settings['config']
    env_py = settings['env_py']
    timeout_seconds = settings['timeout_seconds']
    trainer_pattern = settings['trainer_pattern']
    env_pattern = settings['env_pattern']
    config_stem = settings['config_stem']
    trainer_log = ROOT / 'smoke_logs' / f'{config_stem}_trainer.log'
    env_log = ROOT / 'smoke_logs' / f'{config_stem}_env.log'
    trainer_log.parent.mkdir(parents=True, exist_ok=True)

    pkill_pattern(env_pattern)
    pkill_pattern(trainer_pattern)
    kill_port(8001)
    run_api_proc = restart_run_api()

    with trainer_log.open('w') as tf:
        trainer = subprocess.Popen(
            ['bash', '-lc', f'source /Users/heomin/.hermes/hermes-agent/venv/bin/activate && set -a && source /Users/heomin/.hermes/.env && set +a && PYTHONUNBUFFERED=1 python -u launch_training.py --config {config} --no-wandb'],
            cwd=ROOT,
            env=ENV,
            stdout=tf,
            stderr=subprocess.STDOUT,
        )

    ready, health = wait_health_ready()

    with env_log.open('w') as ef:
        env_proc = subprocess.Popen(
            ['bash', '-lc', f'source /Users/heomin/.hermes/hermes-agent/venv/bin/activate && set -a && source /Users/heomin/.hermes/.env && set +a && PYTHONUNBUFFERED=1 python -u {env_py} serve --config {config}'],
            cwd=ROOT,
            env=ENV,
            stdout=ef,
            stderr=subprocess.STDOUT,
        )

    progress_ok, trainer_text = wait_for_progress(trainer_log, trainer, timeout=timeout_seconds)
    env_text = env_log.read_text(errors='ignore') if env_log.exists() else ''

    trainer_summary = summarize_trainer_text(trainer_text)
    env_summary = summarize_env_text(env_text)
    assessment = assess_run(ready, progress_ok, trainer_summary, env_summary)

    summary = {
        'config': config,
        'environment': env_py,
        'health_ready': ready,
        'health_payload': health,
        'trainer_progress_seen': progress_ok,
        'trainer_returncode': trainer.poll(),
        'env_returncode': env_proc.poll(),
        'run_api_returncode': run_api_proc.poll(),
        'trainer': trainer_summary,
        'environment_summary': env_summary,
        'assessment': assessment,
        'trainer_log_path': str(trainer_log),
        'env_log_path': str(env_log),
        'trainer_log_tail': '\n'.join(trainer_text.splitlines()[-20:]) if trainer_text else '',
        'env_log_tail': '\n'.join(env_text.splitlines()[-20:]) if env_text else '',
    }

    summary['env_active_before_cleanup'] = env_proc.poll() is None
    summary['trainer_active_before_cleanup'] = trainer.poll() is None
    summary['run_api_active_before_cleanup'] = run_api_proc.poll() is None
    summary['cleanup_applied'] = {
        'environment': cleanup_process(env_proc),
        'trainer': cleanup_process(trainer),
        'run_api': cleanup_process(run_api_proc),
    }

    summary['trainer_returncode_final'] = trainer.poll()
    summary['env_returncode_final'] = env_proc.poll()
    summary['run_api_returncode_final'] = run_api_proc.poll()
    summary['saved_artifacts'] = save_summary_artifacts(summary, config_stem)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
