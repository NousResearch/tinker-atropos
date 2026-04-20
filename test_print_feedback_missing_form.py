from pathlib import Path

import print_feedback_missing_form as mod


METRICS_TEXT = """# Metrics

## 기준 메모
- project: actual-youtube-description-conversion
- preset: youtube
- selection mode: reward

## 실측 입력
- X 클릭률:
- X 댓글 수: 12건
- 설명란 클릭률:
- 텔레그램 합류 수: 15건
- 합류 전환율: 미집계
- 첫 주 체크인 수:
- 첫 주 재방문 수: 7건

## 운영 메모
- 배포 날짜:
- 실측 기간: 2026-04-17 ~ 2026-04-20
- 채널 메모:
- 다음 액션:
"""


def test_collect_missing_only_lines(tmp_path):
    metrics = tmp_path / "metrics.md"
    metrics.write_text(METRICS_TEXT, encoding="utf-8")

    lines = mod.collect_missing_lines(metrics)

    assert lines == [
        "- X 클릭률:",
        "- 설명란 클릭률:",
        "- 첫 주 체크인 수:",
        "- 배포 날짜:",
        "- 다음 액션:",
    ]


def test_build_missing_form_text_from_feedback_tree(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-youtube-description-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")

    text = mod.build_missing_form_text(root=tmp_path, date="2026-04-17")

    assert "## actual-youtube-description-conversion" in text
    assert "- X 클릭률:" in text
    assert "- 설명란 클릭률:" in text
    assert "- 첫 주 체크인 수:" in text
    assert "- 배포 날짜:" in text
    assert "- 다음 액션:" in text
    assert "- X 댓글 수: 12건" not in text
    assert "- 합류 전환율: 미집계" not in text
