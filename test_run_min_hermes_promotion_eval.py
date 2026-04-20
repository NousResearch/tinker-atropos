from pathlib import Path
import subprocess

from run_min_hermes_promotion_eval import build_report_markdown, save_summary_artifacts


def test_build_report_markdown_lists_v2_and_v3_lane_summaries():
    summary = {
        "benchmarks": {
            "v2": {
                "benchmark_path": "research/min_hermes_offline_eval_v2.json",
                "scoreboard_markdown_path": "research/min_hermes_offline_eval_v2_scoreboard.md",
                "lanes": {
                    "current_policy": {"mean_total": 0.9979, "task_pass_count": 12, "task_count": 12, "lane_passed": True},
                    "patched_policy": {"mean_total": 0.9924, "task_pass_count": 12, "task_count": 12, "lane_passed": True},
                },
            },
            "v3": {
                "benchmark_path": "research/min_hermes_offline_eval_v3.json",
                "scoreboard_markdown_path": "research/min_hermes_offline_eval_v3_scoreboard.md",
                "lanes": {
                    "current_policy": {"mean_total": 0.9750, "task_pass_count": 0, "task_count": 1, "lane_passed": False},
                    "patched_policy": {"mean_total": 0.9800, "task_pass_count": 1, "task_count": 1, "lane_passed": True},
                },
            },
        }
    }

    text = build_report_markdown(summary)

    assert "# Min Hermes Promotion Eval" in text
    assert "## v2" in text
    assert "## v3" in text
    assert "current_policy" in text
    assert "patched_policy" in text
    assert "0.9750" in text
    assert "12/12" in text


def test_save_summary_artifacts_writes_json_and_markdown(tmp_path):
    summary = {
        "benchmarks": {
            "v3": {
                "benchmark_path": "research/min_hermes_offline_eval_v3.json",
                "scoreboard_markdown_path": "research/min_hermes_offline_eval_v3_scoreboard.md",
                "lanes": {
                    "current_policy": {"mean_total": 0.9750, "task_pass_count": 0, "task_count": 1, "lane_passed": False},
                    "patched_policy": {"mean_total": 0.9800, "task_pass_count": 1, "task_count": 1, "lane_passed": True},
                },
            }
        }
    }

    paths = save_summary_artifacts(tmp_path, summary)

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()
    assert "promotion-eval" in paths["json"]
    assert "Min Hermes Promotion Eval" in Path(paths["markdown"]).read_text(encoding="utf-8")


def test_run_min_hermes_promotion_eval_cli_prints_v2_and_v3():
    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'run_min_hermes_promotion_eval.py'],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert 'v2' in proc.stdout
    assert 'v3' in proc.stdout
    assert 'current_policy' in proc.stdout
    assert 'patched_policy' in proc.stdout
