import sys
from pathlib import Path

import run_ultra_ready_smoke_design_system_operator as smoke


def test_build_command_uses_generic_runner_and_design_operator_paths():
    cmd = smoke.build_command(timeout_seconds=123)

    assert cmd[0] == sys.executable
    assert cmd[1] == str(Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_ultra_ready_smoke_generic.py'))
    assert 'min_design_system_operator_ultra_smoke' in cmd
    assert 'tinker_atropos/environments/min_design_system_operator_tinker.py' in cmd
    assert 'configs/min_design_system_operator_ultra_smoke.yaml' in cmd
    assert 'MIN_DESIGN_SYSTEM_OPERATOR_ULTRA_SMOKE' in cmd
    assert cmd[-1] == '123'


def test_default_timeout_is_long_enough_for_tinker_smoke():
    assert smoke.DEFAULT_TIMEOUT >= 300
