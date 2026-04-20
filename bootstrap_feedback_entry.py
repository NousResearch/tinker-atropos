import argparse
import copy
import json
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
FEEDBACK_ROOT = ROOT / 'feedback'

SELECTED_TEMPLATE = {
    "preset": "ordinarybiz",
    "project": "example-project",
    "chosen_business_rank": 1,
    "chosen_x_rank": 1,
    "chosen_landing_rank": 1,
    "chosen_retention_rank": 1,
    "final_edits": [
        "헤드라인 문장 1개 수정",
        "CTA 문장 1개 수정"
    ],
    "published_assets": {
        "x": "",
        "landing": "",
        "retention": ""
    }
}

LESSONS_TEMPLATE = """# Lessons

## 무엇이 먹혔는가
- 

## 무엇이 덜 먹혔는가
- 

## 다음 번 자동 생성에서 강화할 포인트
- 

## 다음 번 자동 생성에서 감점할 포인트
- 
"""

PRESET_METRIC_LINES = {
    "ordinarybiz": [
        "- X 클릭률:",
        "- X 댓글 수:",
        "- 랜딩 클릭률:",
        "- 신청 수:",
        "- 전환율:",
        "- retention 체크인 수:",
        "- 재방문 수:",
    ],
    "ailit": [
        "- X 클릭률:",
        "- X 댓글 수:",
        "- 랜딩 클릭률:",
        "- 상담 신청 수:",
        "- 상담 전환율:",
        "- 후속 클릭 수:",
        "- 업셀 문의 수:",
    ],
    "youtube": [
        "- X 클릭률:",
        "- X 댓글 수:",
        "- 설명란 클릭률:",
        "- 텔레그램 합류 수:",
        "- 합류 전환율:",
        "- 첫 주 체크인 수:",
        "- 첫 주 재방문 수:",
    ],
    "vip": [
        "- X 클릭률:",
        "- X 댓글 수:",
        "- 랜딩 클릭률:",
        "- 라이브 신청 수:",
        "- 리플레이 시청 수:",
        "- 첫 주 체크인 수:",
        "- 재참여 수:",
    ],
    "bootcamp": [
        "- X 클릭률:",
        "- X 댓글 수:",
        "- 설명란 클릭률:",
        "- 체험 신청 수:",
        "- 유료 전환 수:",
        "- 유료 전환율:",
        "- 첫 주 체크인 수:",
    ],
    "x-article": [
        "- X 클릭률:",
        "- 저장 수:",
        "- 프로필 클릭 수:",
        "- 랜딩 클릭률:",
        "- 장문 반응 수:",
        "- 후속 응답 수:",
        "- 재방문 수:",
    ],
}


def get_nested(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def metric_lines_for_preset(preset):
    return PRESET_METRIC_LINES.get(preset, PRESET_METRIC_LINES['ordinarybiz'])


def load_summary_data(final_json_path):
    if not final_json_path:
        return None
    return json.loads(Path(final_json_path).read_text(encoding='utf-8'))


def render_metrics_template(preset, project, summary_data=None, final_json_path=None):
    lines = ["# Metrics", "", "## 기준 메모", f"- project: {project}", f"- preset: {preset}"]

    selection_mode = get_nested(summary_data, 'selection_mode') if summary_data else None
    lines.append(f"- selection mode: {selection_mode or '미정'}")
    lines.append(f"- summary final json: {final_json_path or ''}")

    if summary_data:
        lines.extend(
            [
                f"- business reward max: {get_nested(summary_data, 'business', 'reward_eval', 'scores', 'total')}",
                f"- x reward max: {get_nested(summary_data, 'x', 'reward_eval', 'scores', 'total')}",
                f"- landing reward max: {get_nested(summary_data, 'landing', 'reward_eval', 'scores', 'total')}",
                f"- retention reward max: {get_nested(summary_data, 'retention', 'reward_eval', 'scores', 'total')}",
            ]
        )

        x_generator = get_nested(summary_data, 'x', 'scores', 'total')
        landing_generator = get_nested(summary_data, 'landing', 'scores', 'total')
        retention_generator = get_nested(summary_data, 'retention', 'scores', 'total')
        if x_generator is not None:
            lines.append(f"- x generator max: {x_generator}")
        if landing_generator is not None:
            lines.append(f"- landing generator max: {landing_generator}")
        if retention_generator is not None:
            lines.append(f"- retention generator max: {retention_generator}")

    lines.extend(["", "## 실측 입력"])
    lines.extend(metric_lines_for_preset(preset))
    lines.extend(
        [
            "",
            "## 운영 메모",
            "- 배포 날짜:",
            "- 실측 기간:",
            "- 채널 메모:",
            "- 다음 액션:",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Create a new feedback entry scaffold.')
    parser.add_argument('project')
    parser.add_argument('--preset', default='ordinarybiz')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--final-json')
    args = parser.parse_args()

    target = FEEDBACK_ROOT / args.date / args.project
    target.mkdir(parents=True, exist_ok=True)

    selected = copy.deepcopy(SELECTED_TEMPLATE)
    selected['preset'] = args.preset
    selected['project'] = args.project

    summary_data = load_summary_data(args.final_json)
    metrics_text = render_metrics_template(
        preset=args.preset,
        project=args.project,
        summary_data=summary_data,
        final_json_path=args.final_json,
    )

    selected_path = target / 'selected_variant.json'
    metrics_path = target / 'metrics.md'
    lessons_path = target / 'lessons.md'

    if not selected_path.exists():
        selected_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding='utf-8')
    metrics_path.write_text(metrics_text, encoding='utf-8')
    if not lessons_path.exists():
        lessons_path.write_text(LESSONS_TEMPLATE, encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
