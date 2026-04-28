from pathlib import Path
import json
import tempfile
import subprocess


def test_feedback_templates_exist():
    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos/feedback/templates')
    assert (root / 'selected_variant.json').exists()
    assert (root / 'metrics.md').exists()
    assert (root / 'lessons.md').exists()


def test_extract_feedback_hints_runs():
    proc = subprocess.run(
        ['python', '/Users/heomin/.hermes/hermes-agent/tinker-atropos/extract_feedback_hints.py'],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    assert 'preset_usage' in data
    assert 'chosen_ranks' in data
    assert 'top_strengthen_hints' in data
