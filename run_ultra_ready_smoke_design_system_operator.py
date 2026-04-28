import subprocess
import sys
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
GENERIC = ROOT / 'run_ultra_ready_smoke_generic.py'
NAME = 'min_design_system_operator_ultra_smoke'
ENV_PY = 'tinker_atropos/environments/min_design_system_operator_tinker.py'
CFG = 'configs/min_design_system_operator_ultra_smoke.yaml'
ENV_VAR = 'MIN_DESIGN_SYSTEM_OPERATOR_ULTRA_SMOKE'
ENV_VALUE = '1'
DEFAULT_TIMEOUT = 360


def build_command(timeout_seconds: int = DEFAULT_TIMEOUT) -> list[str]:
    return [
        sys.executable,
        str(GENERIC),
        NAME,
        ENV_PY,
        CFG,
        ENV_VAR,
        ENV_VALUE,
        str(timeout_seconds),
    ]


def main() -> int:
    timeout_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TIMEOUT
    proc = subprocess.run(build_command(timeout_seconds), cwd=ROOT)
    return proc.returncode


if __name__ == '__main__':
    raise SystemExit(main())
