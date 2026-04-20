# Score Patch File Draft

suggested_changes:
  strengthen:
    - phrase: "신뢰 근거를 먼저 보여주는 headline"
      reason: "selected 1 times as strengthen hint"
    - phrase: "행동이 선명한 문장"
      reason: "selected 1 times as strengthen hint"
  penalize:
    - phrase: "긴 설명형 서브카피"
      reason: "selected 1 times as penalize hint"
    - phrase: "추상적인 CTA"
      reason: "selected 1 times as penalize hint"

target_weights:
  landing: [headline_strength, brevity]
  x: [action_clarity, beginner_friendliness]
  retention: [checkin_strength, retention_strength]