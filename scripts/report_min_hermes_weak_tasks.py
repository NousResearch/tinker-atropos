#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def summarize_scoreboard(scoreboard: dict[str, Any]) -> dict[str, Any]:
    weakest = scoreboard.get('lanes', {}).get('current_policy', {}).get('weakest_tasks', [])
    task_ids = [item['task_id'] for item in weakest]
    stages = [task_id.split('-', 1)[0] for task_id in task_ids]
    return {
        'top_weak_task_ids': task_ids,
        'stage_counts': dict(Counter(stages)),
    }


def build_markdown(summary: dict[str, Any], scoreboard: dict[str, Any]) -> str:
    weakest = scoreboard.get('lanes', {}).get('current_policy', {}).get('weakest_tasks', [])
    lines = [
        '# Min Hermes Weak Task Report',
        '',
        f"- top_weak_task_ids: {', '.join(summary['top_weak_task_ids'])}",
        f"- stage_counts: {summary['stage_counts']}",
        '',
        '## Current policy weakest tasks',
        '',
    ]
    for item in weakest:
        lines.append(f"- {item['task_id']} | {item['title']} | total={item['total']}")
    return '\n'.join(lines) + '\n'


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    scoreboard_path = repo_root / 'research' / 'min_hermes_offline_eval_v1_scoreboard.json'
    scoreboard = load_json(scoreboard_path)
    summary = summarize_scoreboard(scoreboard)
    markdown = build_markdown(summary, scoreboard)
    print(json.dumps({'summary': summary, 'markdown': markdown}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
