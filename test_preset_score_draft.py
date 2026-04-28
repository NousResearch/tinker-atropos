import subprocess


def test_preset_score_draft_runs_and_mentions_presets():
    proc = subprocess.run(
        ['python', '/Users/heomin/.hermes/hermes-agent/tinker-atropos/generate_preset_score_draft.py'],
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout
    assert '## ordinarybiz' in out
    assert '## youtube' in out
    assert 'suggested_targets:' in out
