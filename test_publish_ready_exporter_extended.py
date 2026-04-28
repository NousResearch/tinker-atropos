import json
from pathlib import Path
import subprocess



def test_publish_ready_exporter_save_writes_extended_channel_files(tmp_path):
    payload = {
        'business_variants': [{'rank': 1, '한줄결론': '전략'}],
        'funnel_results': [{
            'x_variants': [{'rank': 1, '후크': '후크', '본문': '본문', '행동유도': '행동', '댓글유도': '댓글'}],
            'landing_variants': [{'rank': 1, '헤드라인': '헤드라인', 'CTA': 'CTA', '서브카피': '서브카피'}],
            'retention_variants': [{'rank': 1, '체크인메시지': '체크인', '첫주미션': '미션', '재참여장치': '재참여'}],
        }],
    }
    input_path = tmp_path / 'full-funnel.json'
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

    root = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
    proc = subprocess.run(
        ['python', 'publish_ready_exporter.py', str(input_path), '--save', '--preset', 'youtube'],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    out_dir = input_path.parent / 'publish_ready'
    files = {p.name for p in out_dir.iterdir()}
    assert any(name.startswith('youtube-description-') for name in files)
    assert any(name.startswith('telegram-notice-') for name in files)
    assert any(name.startswith('youtube-hook-pack-') for name in files)
    assert any(name.startswith('followup-comment-') for name in files)
