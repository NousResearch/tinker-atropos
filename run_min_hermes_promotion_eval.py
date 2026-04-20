#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
VENV_PYTHON = Path('/Users/heomin/.hermes/hermes-agent/venv/bin/python')
BENCHMARKS = {
    'v2': 'research/min_hermes_offline_eval_v2.json',
    'v3': 'research/min_hermes_offline_eval_v3.json',
}


def bundle_paths_for_benchmark(benchmark_path: Path) -> dict[str, Path]:
    stem = benchmark_path.stem
    parent = benchmark_path.parent
    return {
        'current_bundle': parent / f'{stem}_current_policy_template.json',
        'patched_bundle': parent / f'{stem}_patched_policy_template.json',
        'scoreboard_json': parent / f'{stem}_scoreboard.json',
        'scoreboard_markdown': parent / f'{stem}_scoreboard.md',
    }


def load_runtime_tools() -> tuple[Any, Any, Any, Any, Any]:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scripts.evaluate_min_hermes_offline_set import build_markdown_report, evaluate_benchmark, load_json
    from scripts.generate_min_hermes_policy_answers import generate_lane_answers, save_json

    return build_markdown_report, evaluate_benchmark, load_json, generate_lane_answers, save_json


def reexec_with_venv_if_needed() -> None:
    if os.environ.get('HERMES_PROMOTION_EVAL_VENV') == '1':
        return
    if sys.executable == str(VENV_PYTHON):
        return
    if not VENV_PYTHON.exists():
        return
    env = os.environ.copy()
    env['HERMES_PROMOTION_EVAL_VENV'] = '1'
    subprocess.run([str(VENV_PYTHON), __file__, *sys.argv[1:]], check=True, cwd=str(ROOT), env=env)
    raise SystemExit(0)


def build_lane_bundle(benchmark: dict[str, Any], lane_name: str, strong: bool, generate_lane_answers) -> dict[str, Any]:
    profile = 'current_generator_loop_v1' if not strong else 'deterministic_template_v2'
    return {
        'benchmark_version': benchmark['version'],
        'lane': lane_name,
        'policy_profile': profile,
        'answers': generate_lane_answers(benchmark, strong=strong),
    }


def save_scoreboard_files(scoreboard_paths: dict[str, Path], result: dict[str, Any], build_markdown_report) -> None:
    scoreboard_paths['scoreboard_json'].write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    scoreboard_paths['scoreboard_markdown'].write_text(build_markdown_report(result), encoding='utf-8')


def run_single_benchmark(root: Path, benchmark_name: str, benchmark_rel_path: str) -> dict[str, Any]:
    build_markdown_report, evaluate_benchmark, load_json, generate_lane_answers, save_json = load_runtime_tools()
    benchmark_path = root / benchmark_rel_path
    benchmark = load_json(benchmark_path)
    scoreboard_paths = bundle_paths_for_benchmark(benchmark_path)

    current_bundle = build_lane_bundle(benchmark, 'current_policy', strong=False, generate_lane_answers=generate_lane_answers)
    patched_bundle = build_lane_bundle(benchmark, 'patched_policy', strong=True, generate_lane_answers=generate_lane_answers)
    save_json(scoreboard_paths['current_bundle'], current_bundle)
    save_json(scoreboard_paths['patched_bundle'], patched_bundle)

    result = evaluate_benchmark(
        benchmark,
        {
            'current_policy': {**current_bundle, '_path': str(scoreboard_paths['current_bundle'])},
            'patched_policy': {**patched_bundle, '_path': str(scoreboard_paths['patched_bundle'])},
        },
    )
    save_scoreboard_files(scoreboard_paths, result, build_markdown_report)

    return {
        'benchmark_name': benchmark_name,
        'benchmark_path': str(benchmark_path.relative_to(root)),
        'current_bundle_path': str(scoreboard_paths['current_bundle'].relative_to(root)),
        'patched_bundle_path': str(scoreboard_paths['patched_bundle'].relative_to(root)),
        'scoreboard_json_path': str(scoreboard_paths['scoreboard_json'].relative_to(root)),
        'scoreboard_markdown_path': str(scoreboard_paths['scoreboard_markdown'].relative_to(root)),
        'lanes': {
            lane_name: {
                'mean_total': lane['mean_total'],
                'pass_rate': lane['pass_rate'],
                'task_pass_count': lane['task_pass_count'],
                'task_count': lane['task_count'],
                'lane_passed': lane['lane_passed'],
            }
            for lane_name, lane in result['lanes'].items()
        },
    }


def run_all(root: Path = ROOT) -> dict[str, Any]:
    return {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'root': str(root),
        'benchmarks': {
            benchmark_name: run_single_benchmark(root, benchmark_name, rel_path)
            for benchmark_name, rel_path in BENCHMARKS.items()
        },
    }


def build_report_markdown(summary: dict[str, Any]) -> str:
    lines = [
        '# Min Hermes Promotion Eval',
        '',
        f"- root: {summary.get('root')}",
        f"- generated_at: {summary.get('generated_at')}",
    ]
    for benchmark_name, benchmark in summary.get('benchmarks', {}).items():
        lines.extend([
            '',
            f'## {benchmark_name}',
            '',
            f"- benchmark_path: {benchmark['benchmark_path']}",
            f"- scoreboard_markdown_path: {benchmark['scoreboard_markdown_path']}",
            '',
            '| lane | mean_total | task_pass_count | lane_passed |',
            '| --- | ---: | ---: | --- |',
        ])
        for lane_name, lane in benchmark.get('lanes', {}).items():
            lines.append(
                f"| {lane_name} | {lane['mean_total']:.4f} | {lane['task_pass_count']}/{lane['task_count']} | {'yes' if lane['lane_passed'] else 'no'} |"
            )
    return '\n'.join(lines) + '\n'


def save_summary_artifacts(root: Path, summary: dict[str, Any]) -> dict[str, str]:
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    date_folder = time.strftime('%Y-%m-%d')
    summary_dir = root / 'outputs' / date_folder / 'promotion-eval' / 'summary'
    summary_dir.mkdir(parents=True, exist_ok=True)
    json_path = summary_dir / f'min-hermes-promotion-eval-{timestamp}.json'
    markdown_path = summary_dir / f'min-hermes-promotion-eval-{timestamp}.md'
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    markdown_path.write_text(build_report_markdown(summary), encoding='utf-8')
    return {'json': str(json_path), 'markdown': str(markdown_path)}


def main() -> None:
    reexec_with_venv_if_needed()
    parser = argparse.ArgumentParser(description='v2와 v3 승격 평가를 한 번에 재생성한다.')
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--no-save-summary', action='store_true')
    args = parser.parse_args()

    root = Path(args.root)
    summary = run_all(root)
    if not args.no_save_summary:
        summary['summary_artifacts'] = save_summary_artifacts(root, summary)
    print(build_report_markdown(summary))


if __name__ == '__main__':
    main()
