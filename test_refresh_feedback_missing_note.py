from pathlib import Path

import refresh_feedback_missing_note as mod


METRICS_TEXT = """# Metrics

## 기준 메모
- project: actual-ailit-consult-conversion
- preset: ailit

## 실측 입력
- X 클릭률:
- X 댓글 수: 미집계
- 랜딩 클릭률:

## 운영 메모
- 배포 날짜:
- 실측 기간: 2026-04-17 ~ 2026-04-20
- 채널 메모:
- 다음 액션:
"""


def test_build_note_text_contains_missing_only_form(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-ailit-consult-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")

    text = mod.build_note_text(root=tmp_path, date="2026-04-17")

    assert "# Tinker-Atropos 2026-04-17 실측 feedback 초간단 복붙 폼" in text
    assert "## actual-ailit-consult-conversion" in text
    assert "- X 클릭률:" in text
    assert "- 랜딩 클릭률:" in text
    assert "- 배포 날짜:" in text
    assert "- 다음 액션:" in text
    assert "- X 댓글 수: 미집계" not in text


def test_write_note_creates_file(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-ailit-consult-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")
    output = tmp_path / "missing-form.md"

    mod.write_note(root=tmp_path, date="2026-04-17", output_path=output)

    text = output.read_text(encoding="utf-8")
    assert "# Tinker-Atropos 2026-04-17 실측 feedback 초간단 복붙 폼" in text
    assert "## actual-ailit-consult-conversion" in text
