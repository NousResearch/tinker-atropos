from publish_ready_exporter import (
    build_publish_ready_bundle,
    render_landing_brief,
    render_retention_notice,
    render_x_post,
    render_youtube_description,
    render_telegram_summary,
    render_x_article_outline,
    render_landing_edit_memo,
    render_telegram_notice,
    render_youtube_hook_pack,
    render_followup_comment,
)


def test_build_publish_ready_bundle_picks_top_items():
    payload = {
        "business_variants": [
            {"rank": 1, "한줄결론": "전략 결론"}
        ],
        "funnel_results": [
            {
                "x_variants": [{"rank": 1, "후크": "후크", "본문": "본문", "행동유도": "행동"}],
                "landing_variants": [{"rank": 1, "헤드라인": "헤드라인", "CTA": "CTA", "서브카피": "서브카피"}],
                "retention_variants": [{"rank": 1, "체크인메시지": "체크인", "첫주미션": "미션", "재참여장치": "재참여"}],
            }
        ]
    }
    result = build_publish_ready_bundle(payload)

    assert result["strategy"]["한줄결론"] == "전략 결론"
    assert result["x"]["후크"] == "후크"
    assert result["landing"]["헤드라인"] == "헤드라인"
    assert result["retention"]["체크인메시지"] == "체크인"



def test_platform_specific_renderers_output_expected_sections():
    bundle = {
        "strategy": {"한줄결론": "전략"},
        "x": {"후크": "후크", "본문": "본문", "행동유도": "행동", "댓글유도": "댓글"},
        "landing": {"헤드라인": "헤드라인", "서브카피": "서브카피", "CTA": "CTA"},
        "retention": {"체크인메시지": "체크인", "첫주미션": "미션", "재참여장치": "재참여"},
    }
    assert "후크" in render_x_post(bundle)
    assert "헤드라인:" in render_landing_brief(bundle)
    assert "체크인:" in render_retention_notice(bundle)
    assert "텔레그램 공지문" in render_telegram_notice(bundle)
    assert "YouTube Hook Pack" in render_youtube_hook_pack(bundle)
    assert "댓글 후속문" in render_followup_comment(bundle)



def test_platform_specific_renderers_change_with_preset():
    bundle = {
        "strategy": {"한줄결론": "전략"},
        "x": {"후크": "후크", "본문": "본문", "행동유도": "행동", "댓글유도": "댓글"},
        "landing": {"헤드라인": "헤드라인", "서브카피": "서브카피", "CTA": "CTA"},
        "retention": {"체크인메시지": "체크인", "첫주미션": "미션", "재참여장치": "재참여"},
    }
    assert "Ailit" in render_x_post(bundle, preset="ailit")
    assert "YouTube Landing Brief" in render_landing_brief(bundle, preset="youtube")
    assert "VIP Retention Notice" in render_retention_notice(bundle, preset="vip")
    assert "YouTube Description" in render_youtube_description(bundle, preset="youtube")
    assert "Telegram Summary" in render_telegram_summary(bundle, preset="bootcamp")
    assert "X Article Outline" in render_x_article_outline(bundle, preset="x-article")
    assert "Landing Edit Memo" in render_landing_edit_memo(bundle, preset="vip")
    assert "Ailit Telegram Notice" in render_telegram_notice(bundle, preset="ailit")
    assert "YouTube Hook Pack" in render_youtube_hook_pack(bundle, preset="youtube")
    assert "Follow-up Comment" in render_followup_comment(bundle, preset="ordinarybiz")
