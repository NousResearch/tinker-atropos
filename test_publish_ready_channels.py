from publish_ready_exporter import render_bundle, render_x_post, render_landing_brief, render_retention_notice, render_youtube_description, render_telegram_summary, render_x_article_outline, render_landing_edit_memo


def test_render_bundle_changes_title_by_preset():
    bundle = {
        'strategy': {'한줄결론': '전략'},
        'x': {'후크': '후크', '본문': '본문', '행동유도': '행동'},
        'landing': {'헤드라인': '헤드라인', '서브카피': '서브카피', 'CTA': 'CTA'},
        'retention': {'체크인메시지': '체크인', '첫주미션': '미션', '재참여장치': '재참여'},
    }
    assert 'YouTube' in render_bundle(bundle, preset='youtube')
    assert 'VIP' in render_bundle(bundle, preset='vip')


def test_channel_outputs_change_tone_by_preset():
    bundle = {
        'strategy': {'한줄결론': '전략'},
        'x': {'후크': '후크', '본문': '본문', '행동유도': '행동'},
        'landing': {'헤드라인': '헤드라인', '서브카피': '서브카피', 'CTA': 'CTA'},
        'retention': {'체크인메시지': '체크인', '첫주미션': '미션', '재참여장치': '재참여'},
    }
    assert '유튜브 설명란까지 같이 점검하자.' in render_x_post(bundle, preset='youtube')
    assert 'Ailit Landing Brief' in render_landing_brief(bundle, preset='ailit')
    assert 'VIP Retention Notice' in render_retention_notice(bundle, preset='vip')
    assert 'YouTube Description' in render_youtube_description(bundle, preset='youtube')
    assert 'Telegram Summary' in render_telegram_summary(bundle, preset='bootcamp')
    assert 'X Article Outline' in render_x_article_outline(bundle, preset='x-article')
    assert 'Landing Edit Memo' in render_landing_edit_memo(bundle, preset='vip')
