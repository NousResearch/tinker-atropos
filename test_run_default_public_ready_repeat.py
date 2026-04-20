from run_default_public_ready_repeat import aggregate_runs


def test_aggregate_runs_counts_working_runs_and_collects_metrics():
    runs = [
        {
            "assessment": {"working": True, "status": "working"},
            "trainer": {"last_step": "1/12", "got_datum_objects": 4, "reward_mean": 0.0625},
        },
        {
            "assessment": {"working": True, "status": "working"},
            "trainer": {"last_step": "2/12", "got_datum_objects": 8, "reward_mean": 0.125},
        },
        {
            "assessment": {"working": False, "status": "run_api_disconnect"},
            "trainer": {"last_step": None, "got_datum_objects": None, "reward_mean": None},
        },
    ]

    summary = aggregate_runs(runs)

    assert summary["run_count"] == 3
    assert summary["working_count"] == 2
    assert summary["working_rate"] == 0.6667
    assert summary["max_last_step"] == "2/12"
    assert summary["datum_objects_observed"] == [4, 8]
    assert summary["reward_means"] == [0.0625, 0.125]
