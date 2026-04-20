from pathlib import Path

import run_feedback_patch_cycle as mod


FILLED_METRICS = """# Metrics

## 기준 메모
- project: sample
- preset: youtube
- selection mode: reward

## 실측 입력
- X 클릭률: 3퍼센트
- X 댓글 수: 12건
- 설명란 클릭률: 미집계
- 텔레그램 합류 수: 15건

## 운영 메모
- 배포 날짜: 2026-04-17
- 실측 기간: 2026-04-17 ~ 2026-04-20
- 채널 메모:
- 다음 액션: 수치 들어오면 patch 체인 실행
"""


def test_collect_missing_lines_from_metrics_file(tmp_path):
    metrics = tmp_path / "metrics.md"
    metrics.write_text(
        FILLED_METRICS.replace("- 텔레그램 합류 수: 15건", "- 텔레그램 합류 수:"),
        encoding="utf-8",
    )

    missing = mod.find_missing_entries(metrics)

    assert "텔레그램 합류 수" in missing


def test_metrics_ready_when_values_or_mijipgye_are_present(tmp_path):
    metrics = tmp_path / "metrics.md"
    metrics.write_text(FILLED_METRICS, encoding="utf-8")

    missing = mod.find_missing_entries(metrics)

    assert missing == []


def test_execute_chain_runs_all_commands_when_ready(tmp_path, monkeypatch):
    feedback_root = tmp_path / "feedback" / "2026-04-17" / "demo"
    feedback_root.mkdir(parents=True)
    (feedback_root / "metrics.md").write_text(FILLED_METRICS, encoding="utf-8")

    calls = []

    def fake_run(cmd, check, cwd=None):
        calls.append((tuple(cmd), cwd))
        class Result:
            returncode = 0
        return Result()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    mod.run_patch_cycle(tmp_path, "2026-04-17")

    assert [cmd for cmd, _ in calls] == [
        ("python", str(tmp_path / "extract_feedback_hints.py")),
        ("python", str(tmp_path / "generate_preset_score_draft.py")),
        ("python", str(tmp_path / "generate_score_patch_draft.py")),
        ("python", str(tmp_path / "generate_score_patch_file_draft.py")),
        ("python", str(tmp_path / "generate_score_patch_v4a.py")),
    ]
