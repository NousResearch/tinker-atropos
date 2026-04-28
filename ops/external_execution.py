from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shlex
import re

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
OMX_DIR = ROOT / '.omx'
LOG_DIR = ROOT / 'logs'


@dataclass(slots=True)
class ExecutionSpec:
    title: str
    task_type: str
    prompt: str
    targets: list[str] | None = None
    use_rp: bool = False
    test_command: str | None = None
    workdir: Path = ROOT



def slugify(text: str) -> str:
    lowered = text.strip().lower()
    slug = re.sub(r'[^a-z0-9가-힣]+', '-', lowered)
    return slug.strip('-') or 'task'



def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def _repo_prompt_builder_instruction(prompt: str, targets: list[str]) -> str:
    target_text = ', '.join(targets)
    return (
        'Build a focused plan/context for this Hermes external execution task. '
        f'Task prompt: {prompt}. '
        f'Relevant targets: {target_text}. '
        'Keep the output concise and useful for a downstream codex exec stdin context run.'
    )


def _repo_prompt_quote(value: str) -> str:
    compact = ' '.join(value.split())
    return '"' + compact.replace('\\', '\\\\').replace('"', '\\"') + '"'



def build_execution_plan(spec: ExecutionSpec) -> dict:
    stamp = _timestamp()
    slug = slugify(spec.title)
    context_path = OMX_DIR / f'context-{slug}-{stamp}.md'
    log_path = LOG_DIR / f'{stamp}-{slug}.log'
    steps: list[dict[str, str]] = []

    targets = spec.targets or []
    if spec.use_rp and targets:
        builder_command = (
            'builder '
            f'{_repo_prompt_quote(_repo_prompt_builder_instruction(spec.prompt, targets))} '
            f'--type plan > {shlex.quote(str(context_path.relative_to(spec.workdir)))}'
        )
        steps.append(
            {
                'kind': 'rp',
                'command': f'rp-cli -e {shlex.quote(builder_command)}',
            }
        )

    codex_parts = ['codex exec']
    if spec.use_rp and targets:
        context_arg = shlex.quote(str(context_path.relative_to(spec.workdir)))
    else:
        context_arg = None
    codex_parts.append(shlex.quote(spec.prompt))
    if context_arg:
        codex_parts.append(f'< {context_arg}')
    steps.append({'kind': 'codex', 'command': ' '.join(codex_parts)})

    if spec.test_command:
        steps.append({'kind': 'test', 'command': spec.test_command})

    return {
        'title': spec.title,
        'task_type': spec.task_type,
        'workdir': str(spec.workdir),
        'context_path': str(context_path.relative_to(spec.workdir)),
        'log_path': str(log_path.relative_to(spec.workdir)),
        'steps': steps,
    }



def render_shell_script(plan: dict) -> str:
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        '',
        f'cd {shlex.quote(plan["workdir"])}',
        'mkdir -p .omx logs',
        f'LOG_PATH={shlex.quote(plan["log_path"])}',
        'touch "$LOG_PATH"',
        '',
    ]
    for step in plan['steps']:
        lines.append(f'echo ">>> {step["kind"]}: {step["command"]}" | tee -a "$LOG_PATH"')
        lines.append(f'{step["command"]} 2>&1 | tee -a "$LOG_PATH"')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'
