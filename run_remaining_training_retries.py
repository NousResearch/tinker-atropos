import json
import subprocess
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
CASES = [
    ('landing', 'tinker_atropos/environments/min_landing_cro_tinker.py', 'configs/min_landing_cro_ultra_smoke.yaml', 'MIN_LANDING_CRO_ULTRA_SMOKE'),
    ('retention', 'tinker_atropos/environments/min_membership_retention_tinker.py', 'configs/min_membership_retention_ultra_smoke.yaml', 'MIN_RETENTION_ULTRA_SMOKE'),
    ('research', 'tinker_atropos/environments/min_agentic_research_tinker.py', 'configs/min_agentic_research_ultra_smoke.yaml', 'MIN_RESEARCH_ULTRA_SMOKE'),
]
results = []
for name, env_py, cfg, env_var in CASES:
    cmd = [
        'python', 'run_ultra_ready_smoke_generic.py',
        f'{name}_retry', env_py, cfg, env_var, '1', '480'
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = json.loads(proc.stdout)
    results.append(payload)
print(json.dumps(results, ensure_ascii=False, indent=2))
