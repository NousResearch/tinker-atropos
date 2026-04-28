import argparse
import json
from datetime import datetime
from pathlib import Path


def build_publish_ready_bundle(payload: dict) -> dict:
    business = payload.get("business_variants", [{}])[0]
    funnel = payload.get("funnel_results", [{}])[0]
    x = funnel.get("x_variants", [{}])[0]
    landing = funnel.get("landing_variants", [{}])[0]
    retention = funnel.get("retention_variants", [{}])[0]
    return {
        "strategy": business,
        "x": x,
        "landing": landing,
        "retention": retention,
    }


def render_bundle(bundle: dict, preset: str = "ordinarybiz") -> str:
    title_map = {
        "ordinarybiz": "# Publish Ready Bundle",
        "bootcamp": "# Publish Ready Bundle - Bootcamp",
        "vip": "# Publish Ready Bundle - VIP",
        "ailit": "# Publish Ready Bundle - Ailit",
        "youtube": "# Publish Ready Bundle - YouTube",
        "x-article": "# Publish Ready Bundle - X Article",
    }
    lines = [title_map.get(preset, title_map["ordinarybiz"])]
    strategy = bundle.get("strategy", {})
    x = bundle.get("x", {})
    landing = bundle.get("landing", {})
    retention = bundle.get("retention", {})
    if strategy:
        lines += ["\n## Strategy", strategy.get("한줄결론", "")]
    if x:
        lines += ["\n## X", x.get("후크", ""), x.get("본문", ""), x.get("행동유도", "")]
    if landing:
        lines += ["\n## Landing", landing.get("헤드라인", ""), landing.get("서브카피", ""), landing.get("CTA", "")]
    if retention:
        lines += ["\n## Retention", retention.get("체크인메시지", ""), retention.get("첫주미션", ""), retention.get("재참여장치", "")]
    return "\n".join(lines)


def render_x_post(bundle: dict, preset: str = "ordinarybiz") -> str:
    x = bundle.get("x", {})
    prefix = {
        "ordinarybiz": "",
        "bootcamp": "[부트캠프] ",
        "vip": "[VIP] ",
        "ailit": "[Ailit] ",
        "youtube": "[YouTube] ",
        "x-article": "[X Article] ",
    }.get(preset, "")
    closing = {
        "ordinarybiz": x.get("행동유도", ""),
        "bootcamp": x.get("행동유도", "") + " 오늘 과제로 바로 써보자.",
        "vip": x.get("행동유도", "") + " 가장 빠른 실행안부터 적용하자.",
        "ailit": x.get("행동유도", "") + " 이 흐름을 Ailit 상담 전환으로 잇자.",
        "youtube": x.get("행동유도", "") + " 유튜브 설명란까지 같이 점검하자.",
        "x-article": x.get("행동유도", "") + " 이 문장을 긴 글 아티클 첫 단락으로 확장하자.",
    }.get(preset, x.get("행동유도", ""))
    return "\n".join([
        prefix + x.get("후크", ""),
        x.get("본문", ""),
        closing,
    ]).strip()


def render_landing_brief(bundle: dict, preset: str = "ordinarybiz") -> str:
    landing = bundle.get("landing", {})
    header = {
        "ordinarybiz": "Landing Brief",
        "bootcamp": "Bootcamp Landing Brief",
        "vip": "VIP Landing Brief",
        "ailit": "Ailit Landing Brief",
        "youtube": "YouTube Landing Brief",
        "x-article": "X Article Landing Brief",
    }.get(preset, "Landing Brief")
    note = {
        "ordinarybiz": "핵심 제안을 바로 보여준다.",
        "bootcamp": "참가자가 바로 이해하게 만든다.",
        "vip": "빠른 신뢰 형성이 우선이다.",
        "ailit": "상담 전환 흐름이 끊기지 않게 본다.",
        "youtube": "설명란과 헤드라인 연결을 먼저 본다.",
        "x-article": "긴 글 논리를 랜딩 헤드라인과 맞춘다.",
    }.get(preset, "핵심 제안을 바로 보여준다.")
    return "\n".join([
        f"[{header}]",
        f"메모: {note}",
        f"헤드라인: {landing.get('헤드라인', '')}",
        f"서브카피: {landing.get('서브카피', '')}",
        f"CTA: {landing.get('CTA', '')}",
    ]).strip()


def render_retention_notice(bundle: dict, preset: str = "ordinarybiz") -> str:
    retention = bundle.get("retention", {})
    header = {
        "ordinarybiz": "Retention Notice",
        "bootcamp": "Bootcamp Retention Notice",
        "vip": "VIP Retention Notice",
        "ailit": "Ailit Retention Notice",
        "youtube": "YouTube Retention Notice",
        "x-article": "X Article Retention Notice",
    }.get(preset, "Retention Notice")
    note = {
        "ordinarybiz": "체크인과 재방문을 짧게 유지한다.",
        "bootcamp": "과제 체크인을 바로 이어간다.",
        "vip": "빠른 응답과 고급 톤을 유지한다.",
        "ailit": "상담 전환 뒤 후속 대화를 놓치지 않는다.",
        "youtube": "유입 직후 체크인 타이밍을 짧게 잡는다.",
        "x-article": "긴 글 유입 독자의 후속 관심을 이어간다.",
    }.get(preset, "체크인과 재방문을 짧게 유지한다.")
    return "\n".join([
        f"[{header}]",
        f"메모: {note}",
        f"체크인: {retention.get('체크인메시지', '')}",
        f"첫주미션: {retention.get('첫주미션', '')}",
        f"재참여: {retention.get('재참여장치', '')}",
    ]).strip()


def render_youtube_description(bundle: dict, preset: str = "youtube") -> str:
    strategy = bundle.get("strategy", {})
    x = bundle.get("x", {})
    landing = bundle.get("landing", {})
    return "\n".join([
        "[YouTube Description]",
        strategy.get("한줄결론", ""),
        x.get("행동유도", ""),
        f"랜딩: {landing.get('헤드라인', '')}",
        f"CTA: {landing.get('CTA', '')}",
    ]).strip()


def render_telegram_summary(bundle: dict, preset: str = "ordinarybiz") -> str:
    x = bundle.get("x", {})
    landing = bundle.get("landing", {})
    prefix = {
        "ordinarybiz": "[Telegram Summary]",
        "bootcamp": "[Telegram Summary - Bootcamp]",
        "vip": "[Telegram Summary - VIP]",
        "ailit": "[Telegram Summary - Ailit]",
        "youtube": "[Telegram Summary - YouTube]",
        "x-article": "[Telegram Summary - X Article]",
    }.get(preset, "[Telegram Summary]")
    return "\n".join([
        prefix,
        x.get("행동유도", ""),
        f"랜딩: {landing.get('헤드라인', '')}",
    ]).strip()


def render_telegram_notice(bundle: dict, preset: str = "ordinarybiz") -> str:
    strategy = bundle.get("strategy", {})
    landing = bundle.get("landing", {})
    retention = bundle.get("retention", {})
    prefix = {
        "ordinarybiz": "[Telegram Notice]",
        "bootcamp": "[Bootcamp Telegram Notice]",
        "vip": "[VIP Telegram Notice]",
        "ailit": "[Ailit Telegram Notice]",
        "youtube": "[YouTube Telegram Notice]",
        "x-article": "[X Article Telegram Notice]",
    }.get(preset, "[Telegram Notice]")
    return "\n".join([
        prefix,
        "텔레그램 공지문",
        strategy.get("한줄결론", ""),
        f"핵심 제안: {landing.get('헤드라인', '')}",
        f"지금 할 일: {retention.get('체크인메시지', '')}",
    ]).strip()


def render_youtube_hook_pack(bundle: dict, preset: str = "youtube") -> str:
    x = bundle.get("x", {})
    landing = bundle.get("landing", {})
    return "\n".join([
        "[YouTube Hook Pack]",
        f"오프닝 훅: {x.get('후크', '')}",
        f"설명란 연결: {landing.get('헤드라인', '')}",
        f"행동 문장: {x.get('행동유도', '')}",
    ]).strip()


def render_followup_comment(bundle: dict, preset: str = "ordinarybiz") -> str:
    x = bundle.get("x", {})
    retention = bundle.get("retention", {})
    return "\n".join([
        "[Follow-up Comment]",
        f"댓글 후속문: {x.get('댓글유도', '')}",
        f"재참여 문장: {retention.get('재참여장치', '')}",
    ]).strip()


def render_x_article_outline(bundle: dict, preset: str = "x-article") -> str:
    strategy = bundle.get("strategy", {})
    x = bundle.get("x", {})
    landing = bundle.get("landing", {})
    return "\n".join([
        "[X Article Outline]",
        f"핵심 논지: {strategy.get('한줄결론', '')}",
        f"후크: {x.get('후크', '')}",
        f"본문 초안: {x.get('본문', '')}",
        f"전환 연결: {landing.get('헤드라인', '')}",
    ]).strip()


def render_landing_edit_memo(bundle: dict, preset: str = "ordinarybiz") -> str:
    landing = bundle.get("landing", {})
    label = {
        "ordinarybiz": "[Landing Edit Memo]",
        "vip": "[Landing Edit Memo - VIP]",
        "youtube": "[Landing Edit Memo - YouTube]",
        "ailit": "[Landing Edit Memo - Ailit]",
        "bootcamp": "[Landing Edit Memo - Bootcamp]",
        "x-article": "[Landing Edit Memo - X Article]",
    }.get(preset, "[Landing Edit Memo]")
    return "\n".join([
        label,
        f"헤드라인 유지: {landing.get('헤드라인', '')}",
        f"서브카피 유지: {landing.get('서브카피', '')}",
        f"CTA 유지: {landing.get('CTA', '')}",
    ]).strip()


def main():
    parser = argparse.ArgumentParser(description="Export top-ranked publish-ready bundle from full funnel JSON.")
    parser.add_argument("input", help="Path to full funnel JSON output")
    parser.add_argument("--preset", choices=["ordinarybiz", "bootcamp", "vip", "ailit", "youtube", "x-article"], default="ordinarybiz")
    parser.add_argument("--save", action="store_true", help="Save publish-ready bundle next to input under publish_ready/")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    bundle = build_publish_ready_bundle(payload)
    if args.save:
        out_dir = Path(args.input).resolve().parent / "publish_ready"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        text_path = out_dir / f"bundle-{stamp}.md"
        json_path = out_dir / f"bundle-{stamp}.json"
        x_path = out_dir / f"x-post-{stamp}.txt"
        landing_path = out_dir / f"landing-brief-{stamp}.txt"
        retention_path = out_dir / f"retention-notice-{stamp}.txt"
        youtube_desc_path = out_dir / f"youtube-description-{stamp}.txt"
        telegram_path = out_dir / f"telegram-summary-{stamp}.txt"
        telegram_notice_path = out_dir / f"telegram-notice-{stamp}.txt"
        youtube_hook_pack_path = out_dir / f"youtube-hook-pack-{stamp}.txt"
        followup_comment_path = out_dir / f"followup-comment-{stamp}.txt"
        x_article_path = out_dir / f"x-article-outline-{stamp}.txt"
        landing_memo_path = out_dir / f"landing-edit-memo-{stamp}.txt"
        text_path.write_text(render_bundle(bundle, preset=args.preset), encoding="utf-8")
        json_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        x_path.write_text(render_x_post(bundle, preset=args.preset), encoding="utf-8")
        landing_path.write_text(render_landing_brief(bundle, preset=args.preset), encoding="utf-8")
        retention_path.write_text(render_retention_notice(bundle, preset=args.preset), encoding="utf-8")
        youtube_desc_path.write_text(render_youtube_description(bundle, preset='youtube'), encoding='utf-8')
        telegram_path.write_text(render_telegram_summary(bundle, preset=args.preset), encoding='utf-8')
        telegram_notice_path.write_text(render_telegram_notice(bundle, preset=args.preset), encoding='utf-8')
        youtube_hook_pack_path.write_text(render_youtube_hook_pack(bundle, preset='youtube'), encoding='utf-8')
        followup_comment_path.write_text(render_followup_comment(bundle, preset=args.preset), encoding='utf-8')
        x_article_path.write_text(render_x_article_outline(bundle, preset='x-article'), encoding='utf-8')
        landing_memo_path.write_text(render_landing_edit_memo(bundle, preset=args.preset), encoding='utf-8')
        print(f"saved_text={text_path}")
        print(f"saved_json={json_path}")
        print(f"saved_x_post={x_path}")
        print(f"saved_landing_brief={landing_path}")
        print(f"saved_retention_notice={retention_path}")
        print(f"saved_youtube_description={youtube_desc_path}")
        print(f"saved_telegram_summary={telegram_path}")
        print(f"saved_telegram_notice={telegram_notice_path}")
        print(f"saved_youtube_hook_pack={youtube_hook_pack_path}")
        print(f"saved_followup_comment={followup_comment_path}")
        print(f"saved_x_article_outline={x_article_path}")
        print(f"saved_landing_edit_memo={landing_memo_path}")
    else:
        print(render_bundle(bundle, preset=args.preset))


if __name__ == '__main__':
    main()
