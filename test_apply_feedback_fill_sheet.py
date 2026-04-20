from pathlib import Path

import apply_feedback_fill_sheet as mod


SHEET_TEXT = """# feedback bulk fill

## actual-youtube-description-conversion
- X 클릭률: 3퍼센트
- X 댓글 수: 12건
- 설명란 클릭률: 4퍼센트
- 텔레그램 합류 수: 15건
- 합류 전환율: 8퍼센트
- 첫 주 체크인 수: 11건
- 첫 주 재방문 수: 7건
- 배포 날짜: 2026-04-17
- 실측 기간: 2026-04-17 ~ 2026-04-20
- 채널 메모: 설명란 첫 문장 교체본 적용
- 다음 액션: 유지 문구 비교
"""

METRICS_TEXT = """# Metrics

## 기준 메모
- project: actual-youtube-description-conversion
- preset: youtube
- selection mode: reward

## 실측 입력
- X 클릭률:
- X 댓글 수:
- 설명란 클릭률:
- 텔레그램 합류 수:
- 합류 전환율:
- 첫 주 체크인 수:
- 첫 주 재방문 수:

## 운영 메모
- 배포 날짜:
- 실측 기간:
- 채널 메모:
- 다음 액션:
"""


def test_parse_fill_sheet_by_project_and_label():
    data = mod.parse_fill_sheet(SHEET_TEXT)

    assert data["actual-youtube-description-conversion"]["X 클릭률"] == "3퍼센트"
    assert data["actual-youtube-description-conversion"]["채널 메모"] == "설명란 첫 문장 교체본 적용"


def test_apply_values_to_metrics_file(tmp_path):
    metrics = tmp_path / "metrics.md"
    metrics.write_text(METRICS_TEXT, encoding="utf-8")
    data = mod.parse_fill_sheet(SHEET_TEXT)

    mod.apply_project_values(metrics, data["actual-youtube-description-conversion"])

    text = metrics.read_text(encoding="utf-8")
    assert "- X 클릭률: 3퍼센트" in text
    assert "- 텔레그램 합류 수: 15건" in text
    assert "- 배포 날짜: 2026-04-17" in text
    assert "- 채널 메모: 설명란 첫 문장 교체본 적용" in text


def test_apply_sheet_updates_feedback_folder_metrics(tmp_path):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "actual-youtube-description-conversion"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(METRICS_TEXT, encoding="utf-8")
    sheet = tmp_path / "sheet.md"
    sheet.write_text(SHEET_TEXT, encoding="utf-8")

    mod.apply_fill_sheet(root=tmp_path, date="2026-04-17", sheet_path=sheet)

    text = (feedback_root / "metrics.md").read_text(encoding="utf-8")
    assert "- 다음 액션: 유지 문구 비교" in text
