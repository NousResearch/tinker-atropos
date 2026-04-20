# Score Patch File Draft

suggested_changes:
  strengthen:
    - phrase: "설명란과 이어지는 행동 문장"
      reason: "selected 1 times as strengthen hint"
    - phrase: "유튜브 시청자용 헤드라인"
      reason: "selected 1 times as strengthen hint"
    - phrase: "상담 전환을 바로 말하는 headline"
      reason: "selected 1 times as strengthen hint"
    - phrase: "Ailit 체크인 문구"
      reason: "selected 1 times as strengthen hint"
    - phrase: "논리 흐름이 보이는 후크"
      reason: "selected 1 times as strengthen hint"
  penalize:
    - phrase: "긴 설명형 본문"
      reason: "selected 1 times as penalize hint"
    - phrase: "두 단계로 읽히는 CTA"
      reason: "selected 1 times as penalize hint"
    - phrase: "추상적인 신뢰 표현"
      reason: "selected 1 times as penalize hint"
    - phrase: "길게 이어지는 retention 미션 문장"
      reason: "selected 1 times as penalize hint"
    - phrase: "저장 가치가 약한 headline"
      reason: "selected 1 times as penalize hint"

target_weights:
  landing: [headline_strength, brevity]
  x: [action_clarity, beginner_friendliness]
  retention: [checkin_strength, retention_strength]