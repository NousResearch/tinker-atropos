from scripts.report_min_hermes_weak_tasks import summarize_scoreboard


def test_summarize_scoreboard_extracts_top_weak_tasks_and_stage_counts():
    scoreboard = {
        "lanes": {
            "current_policy": {
                "weakest_tasks": [
                    {"task_id": "landing-telegram-join", "title": "텔레그램 채널 합류 랜딩 개선", "total": 0.3950},
                    {"task_id": "retention-bootcamp-first-week", "title": "부트캠프 첫 주 유지 개선", "total": 0.4098},
                    {"task_id": "landing-bootcamp-trial", "title": "부트캠프 체험 신청 랜딩 개선", "total": 0.4700},
                ]
            }
        }
    }

    summary = summarize_scoreboard(scoreboard)

    assert summary["top_weak_task_ids"] == [
        "landing-telegram-join",
        "retention-bootcamp-first-week",
        "landing-bootcamp-trial",
    ]
    assert summary["stage_counts"] == {"landing": 2, "retention": 1}
