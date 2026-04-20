from __future__ import annotations

import json
from pathlib import Path

ENV_SPECS = [
    ('min_business_strategy', 'outputs/business'),
    ('min_x_strategy', 'outputs/x'),
    ('min_landing_cro', 'outputs/landing'),
    ('min_membership_retention', 'outputs/retention'),
    ('min_agentic_research', 'outputs/business'),
]



def _count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob(pattern))



def _latest_file(path: Path, pattern: str) -> str | None:
    if not path.exists():
        return None
    files = list(path.rglob(pattern))
    if not files:
        return None
    latest = max(files, key=lambda item: item.stat().st_mtime)
    return str(latest)



def collect_environment_status(root: Path) -> dict:
    env_root = root / 'tinker_atropos' / 'environments'
    test_root = root / 'tinker_atropos' / 'tests'
    cfg_root = root / 'configs'
    outputs_root = root / 'outputs'
    drafts_root = root / 'feedback' / 'patch_drafts'

    environments = []
    alerts = []
    for name, artifact_dir in ENV_SPECS:
        env_file = env_root / f'{name}_tinker.py'
        test_file = test_root / f'test_{name}_env.py'
        config_count = _count_files(cfg_root, f'{name}*.yaml')
        latest_output = _latest_file(outputs_root / Path(artifact_dir).name, '*.json')
        item = {
            'name': name,
            'env_exists': env_file.exists(),
            'test_exists': test_file.exists(),
            'config_count': config_count,
            'latest_output': latest_output,
        }
        environments.append(item)
        if not item['env_exists']:
            alerts.append(f'missing environment file: {name}')
        if not item['test_exists']:
            alerts.append(f'missing test: {name}')
        if item['config_count'] == 0:
            alerts.append(f'missing config: {name}')

    artifacts = {
        'output_json_count': _count_files(outputs_root, '*.json'),
        'latest_output_json': _latest_file(outputs_root, '*.json'),
        'patch_draft_count': _count_files(drafts_root, '*.patch'),
        'latest_patch_draft': _latest_file(drafts_root, '*.patch'),
    }

    return {
        'root': str(root),
        'environment_count': len(environments),
        'alert_count': len(alerts),
        'alerts': alerts,
        'environments': environments,
        'artifacts': artifacts,
    }



def build_comment_body(summary: dict) -> str:
    lines = [
        f"environment_count: {summary['environment_count']}",
        f"alert_count: {summary['alert_count']}",
        'alerts:',
    ]
    if summary['alerts']:
        lines.extend(f'- {item}' for item in summary['alerts'])
    else:
        lines.append('- none')
    lines.append('artifacts:')
    lines.append(f"- output_json_count: {summary['artifacts']['output_json_count']}")
    lines.append(f"- patch_draft_count: {summary['artifacts']['patch_draft_count']}")
    if summary['artifacts']['latest_output_json']:
        lines.append(f"- latest_output_json: {summary['artifacts']['latest_output_json']}")
    if summary['artifacts']['latest_patch_draft']:
        lines.append(f"- latest_patch_draft: {summary['artifacts']['latest_patch_draft']}")
    return '\n'.join(lines)


if __name__ == '__main__':
    summary = collect_environment_status(Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos'))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
