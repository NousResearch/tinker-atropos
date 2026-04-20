import json
import subprocess
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')
OUT_DIR = ROOT / 'feedback' / 'patch_drafts'

TARGETS = {
    'headline': str(ROOT / 'build_business_to_landing_loop.py'),
    'cta': str(ROOT / 'build_business_to_landing_loop.py'),
    'action': str(ROOT / 'build_business_to_x_loop.py'),
    'body': str(ROOT / 'build_business_to_x_loop.py'),
    'retention': str(ROOT / 'build_business_to_retention_loop.py'),
}

SUGGESTED_REPLACEMENTS = {
    'headline': (
        'weights = {\n        "headline_strength": 0.41,\n        "cta_strength": 0.19,\n        "beginner_friendliness": 0.16,\n        "brevity": 0.24,\n    }',
        'weights = {\n        "headline_strength": 0.44,\n        "cta_strength": 0.18,\n        "beginner_friendliness": 0.15,\n        "brevity": 0.23,\n    }',
    ),
    'cta': (
        'weights = {\n        "headline_strength": 0.41,\n        "cta_strength": 0.19,\n        "beginner_friendliness": 0.16,\n        "brevity": 0.24,\n    }',
        'weights = {\n        "headline_strength": 0.39,\n        "cta_strength": 0.23,\n        "beginner_friendliness": 0.16,\n        "brevity": 0.22,\n    }',
    ),
    'action': (
        'weights = {\n        "hook_strength": 0.29,\n        "comment_strength": 0.17,\n        "action_clarity": 0.28,\n        "beginner_friendliness": 0.16,\n        "body_brevity": 0.1,\n    }',
        'weights = {\n        "hook_strength": 0.27,\n        "comment_strength": 0.16,\n        "action_clarity": 0.32,\n        "beginner_friendliness": 0.16,\n        "body_brevity": 0.09,\n    }',
    ),
    'body': (
        'body_brevity = 1.0 if 40 <= len(body) <= 110 else 0.45 if len(body) <= 150 else 0.1',
        'body_brevity = 1.0 if 40 <= len(body) <= 96 else 0.4 if len(body) <= 135 else 0.1',
    ),
    'retention': (
        'brevity = 1.0 if len(checkin) <= 80 else 0.5 if len(checkin) <= 140 else 0.1',
        'brevity = 1.0 if len(checkin) <= 72 else 0.45 if len(checkin) <= 120 else 0.1',
    ),
}

RULES = {
    '신뢰 근거를 먼저 보여주는 headline': {
        'old': 'HEADLINE_PATTERNS = [\n    "{customer_label}를 위한 {offer_label}",\n    "지금 신뢰를 붙이는 {offer_label}",\n    "{customer_label}가 바로 이해하는 {offer_label}",\n]\n',
        'new': 'HEADLINE_PATTERNS = [\n    "{customer_label}를 위한 {offer_label}",\n    "신뢰 근거를 먼저 보여주는 {offer_label}",\n    "{customer_label}가 바로 이해하는 {offer_label}",\n]\n',
        'comment': 'landing headline sales copy 강화',
    },
    '브랜드 중복 없는 Ailit headline': {
        'old': 'suffix = strip_repeated_brand(suffix_after_marker(headline, "바로 이해하는 "), "Ailit")\nitem["헤드라인"] = "Ailit 상담으로 이어지는 " + suffix\nitem["CTA"] = "지금 진단 신청하기"\n',
        'new': 'suffix = strip_repeated_brand(suffix_after_marker(headline, "부담 없이 신청으로 이어지는 "), "Ailit")\nitem["헤드라인"] = "Ailit 상담 신청으로 이어지는 " + suffix\nitem["CTA"] = "부담 없이 신청하기"\n',
        'comment': 'Ailit headline에서 브랜드 중복 제거와 상담 전환 직결 문구 강화',
    },
    '상담 전환을 바로 말하는 headline': {
        'old': 'item["헤드라인"] = "Ailit 상담으로 이어지는 " + suffix\nitem["CTA"] = "지금 진단 신청하기"\n',
        'new': 'item["헤드라인"] = "Ailit 상담 신청으로 이어지는 " + suffix\nitem["CTA"] = "부담 없이 신청하기"\n',
        'comment': '상담 전환 목적을 헤드라인과 CTA 둘 다에서 직접 노출',
    },
    'landing에서 유입 채널이 바로 보이는 headline': {
        'old': 'item["헤드라인"] = "유튜브 시청자를 위한 " + strip_customer_intro(headline)\n',
        'new': 'item["헤드라인"] = "유튜브 시청자가 바로 이해하는 " + suffix_after_marker(headline, "바로 이해하는 ")\n',
        'comment': '채널 맥락이 헤드라인 첫머리에서 바로 보이게 보강',
    },
    '유튜브 시청자용 헤드라인': {
        'old': 'item["헤드라인"] = "유튜브 시청자를 위한 " + strip_customer_intro(headline)\n',
        'new': 'item["헤드라인"] = "유튜브 시청자가 바로 이해하는 " + suffix_after_marker(headline, "바로 이해하는 ")\n',
        'comment': '유튜브 유입형 헤드라인 고정 패턴 강화',
    },
    '추상적인 CTA': {
        'old': 'CTA_PATTERNS = [\n    "지금 진단 신청하기",\n    "지금 핵심 제안 보기",\n    "오늘 바로 시작하기",\n]\n',
        'new': 'CTA_PATTERNS = [\n    "지금 진단 신청하기",\n    "지금 핵심 제안 확인하기",\n    "오늘 바로 시작하기",\n]\n',
        'comment': 'CTA를 더 직접적 행동 문구로 강화',
    },
    '두 단계로 읽히는 CTA': {
        'old': 'TERTIARY_CTA_PATTERNS = [\n    "부담 없이 신청하기",\n    "먼저 확인 후 신청하기",\n    "지금 가볍게 바꿔보기",\n]\n',
        'new': 'TERTIARY_CTA_PATTERNS = [\n    "부담 없이 신청하기",\n    "지금 바로 신청하기",\n    "지금 가볍게 바꿔보기",\n]\n',
        'comment': '두 단계 CTA를 한 단계 행동형 CTA로 단순화',
    },
    '행동이 선명한 문장': {
        'old': 'BODY_PATTERNS = [\n    "핵심은 {offer}이고, 지금은 {summary}",\n    "지금 필요한 건 {offer} 같은 한 가지 제안이고, 이유는 {summary}",\n    "여기서 중요한 건 {offer}에 초점을 모으는 것이고, 오늘 할 일은 {experiment}",\n]\n',
        'new': 'BODY_PATTERNS = [\n    "핵심은 {offer}이고, 지금은 {summary}",\n    "지금 필요한 건 {offer} 같은 한 가지 제안이고, 이유는 {summary}",\n    "여기서 중요한 건 {offer}에 초점을 모으는 것이고, 오늘 할 일은 {experiment}. 설명란 첫 문장도 같이 바꾼다.",\n]\n',
        'comment': 'x 본문의 행동 선명도 강화',
    },
    '설명란과 이어지는 행동 문장': {
        'old': 'item["본문"] += " 유튜브 설명란과 함께 읽히게 연결한다."\n',
        'new': 'item["본문"] += " 유튜브 설명란 첫 문장과 바로 이어지게 연결한다."\n',
        'comment': '유튜브 행동 문장을 설명란 연결형으로 더 직접화',
    },
    'x에서 설명란 연결 문장': {
        'old': 'item["본문"] += " 유튜브 설명란과 함께 읽히게 연결한다."\n',
        'new': 'item["본문"] += " 유튜브 설명란 첫 문장과 바로 이어지게 연결한다."\n',
        'comment': '유튜브 설명란 연결 문장을 실행 지시형으로 보강',
    },
    '긴 설명형 본문': {
        'old': 'body_brevity = 1.0 if 40 <= len(body) <= 110 else 0.45 if len(body) <= 150 else 0.1\n',
        'new': 'body_brevity = 1.0 if 40 <= len(body) <= 96 else 0.4 if len(body) <= 135 else 0.1\n',
        'comment': '장문 본문 감점을 더 빠르게 주도록 보수 조정',
    },
    '바로 행동이 안 보이는 마무리 문장': {
        'old': '"여기서 중요한 건 {offer}에 초점을 모으는 것이고, 오늘 할 일은 {experiment}"\n',
        'new': '"여기서 중요한 건 {offer}에 초점을 모으는 것이고, 오늘 할 일은 {experiment}. 끝나면 바로 댓글로 남긴다."\n',
        'comment': '마무리 문장을 즉시 행동형으로 보강',
    },
    '체크인 문구가 약하다': {
        'old': 'CHECKIN_PATTERNS = [\n    "오늘은 이 한 가지만 끝내면 됩니다: {mission}",\n    "지금 멈추지 않게 먼저 이것부터 해봅시다: {mission}",\n    "부담 없이 오늘 체크할 한 가지는 이것입니다: {mission}",\n]\n',
        'new': 'CHECKIN_PATTERNS = [\n    "오늘은 이 한 가지만 끝내면 됩니다: {mission}",\n    "지금 멈추지 않게 먼저 이것부터 해봅시다: {mission}",\n    "부담 없이 오늘 체크할 한 가지는 이것입니다: {mission}. 끝나면 바로 체크인합니다.",\n]\n',
        'comment': 'retention 체크인 강도 보강',
    },
    '장황한 체크인 문구': {
        'old': 'brevity = 1.0 if len(checkin) <= 80 else 0.5 if len(checkin) <= 140 else 0.1\n',
        'new': 'brevity = 1.0 if len(checkin) <= 72 else 0.45 if len(checkin) <= 120 else 0.1\n',
        'comment': '체크인 문구 길이 감점을 더 빠르게 반영',
    },
    '길게 이어지는 retention 미션 문장': {
        'old': 'MISSION_PATTERNS = [\n    "첫 주에는 {mission}, 하나만 완료한다.",\n    "오늘 첫 행동은 {mission}, 여기서 끝낸다.",\n    "먼저 {mission}, 그리고 결과를 남긴다.",\n]\n',
        'new': 'MISSION_PATTERNS = [\n    "첫 주에는 {mission}, 하나만 완료한다.",\n    "오늘 첫 행동은 {mission}. 여기서 끝낸다.",\n    "먼저 {mission}. 끝나면 결과만 남긴다.",\n]\n',
        'comment': 'retention 미션 문장을 짧은 운영 지시문으로 압축',
    },
    'Ailit 체크인 문구': {
        'old': 'item["체크인메시지"] = "Ailit 체크인: " + item["체크인메시지"]\n',
        'new': 'item["체크인메시지"] = "Ailit 상담 체크인: " + item["체크인메시지"]\n',
        'comment': 'Ailit 유지 문구를 상담 전환 맥락과 맞춤',
    },
}


CATEGORY_KEYWORDS = OrderedDict(
    [
        ('headline', ['headline', '헤드라인']),
        ('cta', ['cta']),
        ('body', ['본문']),
        ('action', ['행동', '설명란', '마무리 문장', '후크']),
        ('retention', ['체크인', '재방문', 'retention', '미션']),
    ]
)


KEYWORD_RULES = [
    (['brand', 'ailit', 'headline'], '브랜드 중복 없는 Ailit headline'),
    (['ailit', 'headline'], '상담 전환을 바로 말하는 headline'),
    (['youtube', 'headline'], '유튜브 시청자용 헤드라인'),
    (['설명란', '행동'], '설명란과 이어지는 행동 문장'),
    (['설명란'], 'x에서 설명란 연결 문장'),
    (['cta'], '두 단계로 읽히는 CTA'),
    (['본문'], '긴 설명형 본문'),
    (['체크인'], '장황한 체크인 문구'),
    (['미션'], '길게 이어지는 retention 미션 문장'),
]


def get_hints():
    proc = subprocess.run(
        ['python', str(ROOT / 'extract_feedback_hints.py')],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)



def classify_hint(text: str) -> str:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered or keyword in text for keyword in keywords):
            return category
    return 'headline'



def suggest_rule(text: str):
    lowered = text.lower()
    for key, rule in RULES.items():
        if key in text or text in key:
            return rule
    for keywords, rule_key in KEYWORD_RULES:
        if all(keyword in lowered or keyword in text for keyword in keywords):
            return RULES[rule_key]
    category = classify_hint(text)
    fallback_map = {
        'headline': '신뢰 근거를 먼저 보여주는 headline',
        'cta': '두 단계로 읽히는 CTA',
        'action': '설명란과 이어지는 행동 문장',
        'body': '긴 설명형 본문',
        'retention': '장황한 체크인 문구',
    }
    return RULES.get(fallback_map[category])



def collect_patch_entries(data: dict) -> list[dict]:
    entries = []
    for intent, hints in [('strengthen', data.get('top_strengthen_hints', [])), ('penalize', data.get('top_penalize_hints', []))]:
        for text, count in hints[:5]:
            category = classify_hint(text)
            old_weight, new_weight = SUGGESTED_REPLACEMENTS.get(category, ('', ''))
            entries.append(
                {
                    'intent': intent,
                    'phrase': text,
                    'count': count,
                    'category': category,
                    'file': TARGETS[category],
                    'rule': suggest_rule(text),
                    'weight_old': old_weight,
                    'weight_new': new_weight,
                }
            )
    return entries



def build_patch(data: dict) -> str:
    entries = collect_patch_entries(data)
    grouped: dict[str, list[dict]] = OrderedDict()
    if not entries:
        entries = [
            {
                'intent': 'observe',
                'phrase': '아직 강한 힌트가 없음',
                'count': 0,
                'category': 'headline',
                'file': TARGETS['headline'],
                'rule': None,
                'weight_old': '',
                'weight_new': '',
            }
        ]
    for entry in entries:
        grouped.setdefault(entry['file'], []).append(entry)

    lines = ['*** Begin Patch']
    for path, items in grouped.items():
        lines.append(f'*** Update File: {path}')
        lines.append('@@')
        seen_categories = set()
        for entry in items:
            lines.append(f"# {entry['intent']} candidate: {entry['phrase']} ({entry['count']}회)")
            lines.append(f"# category: {entry['category']}")
            rule = entry['rule']
            if rule:
                lines.append(f"# comment: {rule['comment']}")
                lines.append(f"# suggested_old: {rule['old']}")
                lines.append(f"# suggested_new: {rule['new']}")
            if entry['category'] not in seen_categories and entry['weight_old'] and entry['weight_new']:
                lines.append(f"# weight_old: {entry['weight_old']}")
                lines.append(f"# weight_new: {entry['weight_new']}")
                seen_categories.add(entry['category'])
    lines.append('*** End Patch')
    return '\n'.join(lines)



def main():
    data = get_hints()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = OUT_DIR / f'score-patch-v4a-{stamp}.patch'
    out.write_text(build_patch(data), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
