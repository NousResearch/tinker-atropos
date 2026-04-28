import json
import sys

import bootstrap_feedback_entry as mod


def test_bootstrap_feedback_entry_writes_preset_specific_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "FEEDBACK_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bootstrap_feedback_entry.py",
            "demo-youtube",
            "--preset",
            "youtube",
            "--date",
            "2026-01-01",
        ],
    )

    mod.main()

    metrics = (tmp_path / "2026-01-01" / "demo-youtube" / "metrics.md").read_text(encoding="utf-8")
    assert "## 기준 메모" in metrics
    assert "## 실측 입력" in metrics
    assert "- 설명란 클릭률:" in metrics
    assert "- 텔레그램 합류 수:" in metrics


def test_bootstrap_feedback_entry_preserves_existing_selected_and_lessons(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "FEEDBACK_ROOT", tmp_path)
    target = tmp_path / "2026-01-01" / "demo-preserve"
    target.mkdir(parents=True)
    (target / "selected_variant.json").write_text(
        '{"preset": "vip", "project": "demo-preserve", "chosen_business_rank": 2}',
        encoding="utf-8",
    )
    (target / "lessons.md").write_text("# Lessons\n\n- keep me", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bootstrap_feedback_entry.py",
            "demo-preserve",
            "--preset",
            "vip",
            "--date",
            "2026-01-01",
        ],
    )

    mod.main()

    selected = (target / "selected_variant.json").read_text(encoding="utf-8")
    lessons = (target / "lessons.md").read_text(encoding="utf-8")
    metrics = (target / "metrics.md").read_text(encoding="utf-8")
    assert '"chosen_business_rank": 2' in selected
    assert "keep me" in lessons
    assert "- 라이브 신청 수:" in metrics


def test_bootstrap_feedback_entry_includes_final_json_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "FEEDBACK_ROOT", tmp_path)

    final_json = tmp_path / "final.json"
    final_json.write_text(
        json.dumps(
            {
                "selection_mode": "generator",
                "business": {"reward_eval": {"scores": {"total": 0.77}}},
                "x": {
                    "reward_eval": {"scores": {"total": 0.7883}},
                    "scores": {"total": 0.8043},
                },
                "landing": {
                    "reward_eval": {"scores": {"total": 0.4925}},
                    "scores": {"total": 0.6785},
                },
                "retention": {
                    "reward_eval": {"scores": {"total": 0.763}},
                    "scores": {"total": 0.5828},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bootstrap_feedback_entry.py",
            "demo-x-article",
            "--preset",
            "x-article",
            "--date",
            "2026-01-01",
            "--final-json",
            str(final_json),
        ],
    )

    mod.main()

    metrics = (tmp_path / "2026-01-01" / "demo-x-article" / "metrics.md").read_text(encoding="utf-8")
    assert "- selection mode: generator" in metrics
    assert "- business reward max: 0.77" in metrics
    assert "- x generator max: 0.8043" in metrics
    assert "- 랜딩 클릭률:" in metrics
    assert "- 저장 수:" in metrics
