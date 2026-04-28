# Score Patch File Draft

suggested_changes:
  strengthen:
    - phrase: "설명란과 이어지는 행동 문장"
      reason: "selected 2 times as strengthen hint"
    - phrase: "브랜드 중복 없는 Ailit headline"
      reason: "selected 2 times as strengthen hint"
    - phrase: "landing에서 유입 채널이 바로 보이는 headline"
      reason: "selected 1 times as strengthen hint"
    - phrase: "x에서 설명란 연결 문장"
      reason: "selected 1 times as strengthen hint"
    - phrase: "유튜브 시청자용 헤드라인"
      reason: "selected 1 times as strengthen hint"
  penalize:
    - phrase: "장황한 체크인 문구"
      reason: "selected 2 times as penalize hint"
    - phrase: "상담 연결이 약한 채널 일반 표현"
      reason: "selected 1 times as penalize hint"
    - phrase: "긴 설명형 본문"
      reason: "selected 1 times as penalize hint"
    - phrase: "두 단계로 읽히는 CTA"
      reason: "selected 1 times as penalize hint"
    - phrase: "추상적인 신뢰 표현"
      reason: "selected 1 times as penalize hint"

target_weights:
  landing: [headline_strength, brevity]
  x: [action_clarity, beginner_friendliness]
  retention: [checkin_strength, retention_strength]