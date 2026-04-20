from pathlib import Path

import refresh_feedback_three_line_note as mod


METRICS_TEXT = """# Metrics

## 기준 메모
- project: actual-youtube-description-conversion
- preset: youtube

## 실측 입력
- X 클릭률:
- X 댓글 수: 미집계
- 설명란 클릭률:
- 텔레그램 합류 수: 15건
- 합류 전환율:
- 첫 주 체크인 수:

## 운영 메모
- 배포 날짜:
- 실측 기간: 2026-04-17 ~ 2026-04-20
- 채널 메모:
- 다음 액션:
"""


def test_build_project_summary_groups_metrics_and_ops(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-youtube-description-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")

    text = mod.build_note_text(root=tmp_path, date="2026-04-17")

    assert "## actual-youtube-description-conversion" in text
    assert "- 실측: X 클릭률, 설명란 클릭률, 합류 전환율, 첫 주 체크인 수" in text
    assert "- 운영: 배포 날짜, 다음 액션" in text
    assert "- 입력판: [[Tinker-Atropos 2026-04-17 실측 feedback 초간단 복붙 폼]]" in text
    assert "X 댓글 수" not in text
    assert "텔레그램 합류 수" not in text


def test_write_note_creates_three_line_summary_note(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-youtube-description-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")
    output = tmp_path / "three-line.md"

    mod.write_note(root=tmp_path, date="2026-04-17", output_path=output)

    text = output.read_text(encoding="utf-8")
    assert "# Tinker-Atropos 2026-04-17 실측 feedback 남은 빈칸 세 줄 요약" in text
    assert "## actual-youtube-description-conversion" in text
