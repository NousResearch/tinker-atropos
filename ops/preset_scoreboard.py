from __future__ import annotations

import json
from pathlib import Path

PRESETS = ['ordinarybiz', 'bootcamp', 'vip', 'ailit', 'youtube', 'x-article']



def infer_preset_from_project(project: str) -> str:
    lowered = project.lower()
    for preset in ['x-article', 'ailit', 'youtube', 'vip', 'bootcamp', 'ordinarybiz']:
        if preset in lowered:
            return preset
    return 'ordinarybiz'



def collect_preset_scoreboard(root: Path) -> dict:
    summary_files = list((root / 'outputs').glob('*/*/summary/*-final-*.json'))
    presets: dict[str, dict] = {}
    for final_file in summary_files:
        project = final_file.parent.parent.name
        preset = infer_preset_from_project(project)
        data = json.loads(final_file.read_text(encoding='utf-8'))
        bucket = presets.setdefault(
            preset,
            {
                'run_count': 0,
                'x_scores': [],
                'landing_scores': [],
                'retention_scores': [],
                'business_scores': [],
                'best_landing_score': -1.0,
                'best_landing_headline': None,
            },
        )
        bucket['run_count'] += 1
        bucket['business_scores'].append(float(data.get('business', {}).get('scores', {}).get('total', 0.0)))
        bucket['x_scores'].append(float(data.get('x', {}).get('scores', {}).get('total', 0.0)))
        landing_score = float(data.get('landing', {}).get('scores', {}).get('total', 0.0))
        bucket['landing_scores'].append(landing_score)
        bucket['retention_scores'].append(float(data.get('retention', {}).get('scores', {}).get('total', 0.0)))
        if landing_score > bucket['best_landing_score']:
            bucket['best_landing_score'] = landing_score
            bucket['best_landing_headline'] = data.get('landing', {}).get('헤드라인')

    result = {}
    for preset, bucket in presets.items():
        result[preset] = {
            'run_count': bucket['run_count'],
            'avg_business_score': round(sum(bucket['business_scores']) / bucket['run_count'], 4),
            'avg_x_score': round(sum(bucket['x_scores']) / bucket['run_count'], 4),
            'avg_landing_score': round(sum(bucket['landing_scores']) / bucket['run_count'], 4),
            'avg_retention_score': round(sum(bucket['retention_scores']) / bucket['run_count'], 4),
            'best_landing_score': round(bucket['best_landing_score'], 4),
            'best_landing_headline': bucket['best_landing_headline'],
        }

    return {
        'preset_count': len(result),
        'totals': {'final_runs': len(summary_files)},
        'presets': result,
    }



def build_comment_body(summary: dict) -> str:
    lines = [f"preset_count: {summary['preset_count']}", f"final_runs: {summary['totals']['final_runs']}", 'presets:']
    for preset, data in sorted(summary['presets'].items()):
        lines.append(
            f"- {preset}: run_count={data['run_count']}, avg_landing_score={data['avg_landing_score']}, avg_x_score={data['avg_x_score']}, best_landing_headline={data['best_landing_headline']}"
        )
    return '\n'.join(lines)


if __name__ == '__main__':
    summary = collect_preset_scoreboard(Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos'))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
