# 민 전용 Hermes 고정 오프라인 평가 세트 v1

## 왜 지금 이걸 먼저 고정해야 하는가

- 가장 큰 병목은 아직도 오프라인 평가 기준 부재다.
- 지금까지는 환경 구현과 스모크 완주 증거는 쌓였지만, 정책 변경 전후를 같은 세트로 비교하는 고정 벤치마크가 없었다.
- 그래서 보상 함수 조정, 모델 변경, 비용 최적화, OMX 운영 자동화 중 무엇이 실제 개선인지 판정하기 어려웠다.

## 이 세트가 답하는 질문

1. 현재 정책이 민의 실전 업무 스타일에 맞는 답을 얼마나 안정적으로 내는가
2. 패치 적용 정책이 현재 정책보다 실제 점수와 통과 개수를 올리는가
3. 사람 기준선과의 간극이 어느 환경에서 가장 큰가

## 평가 구성

- 총 과제 수: 15
- 환경별 분배: business 3, x 3, landing 3, retention 3, research 3
- 비교 lane: current_policy, patched_policy, human_baseline
- task 통과 기준: total 0.80 이상 + gate metric 전부 통과
- lane 통과 기준: mean_total 0.82 이상 + pass_rate 0.80 이상 + 모든 env mean 0.78 이상

## 대표 과제 목록

| task_id | env | title | 왜 중요한가 |
| --- | --- | --- | --- |
| biz-ailit-youtube-conversion | min_business_strategy | 유튜브 유입에서 Ailit 상담 전환 설계 | 현재 민 비즈니스에서 바로 돈으로 연결되는 핵심 병목이다. |
| biz-bootcamp-paid-conversion | min_business_strategy | 부트캠프 무료에서 유료 전환 설계 | 콘텐츠 소비를 결제로 잇는 구조를 검증하는 대표 과제다. |
| biz-vip-first-week-onboarding | min_business_strategy | VIP 첫 칠 일 온보딩 재설계 | 잔존율과 운영 효율을 동시에 보는 전략 과제다. |
| x-ai-tools-sales-structure | min_x_strategy | AI 도구 많이 써도 매출이 안 오르는 이유 X 글 | 민의 핵심 세계관을 가장 잘 드러내는 X 과제다. |
| x-bootcamp-free-to-paid | min_x_strategy | 부트캠프 무료에서 유료 전환 X 글 | 무료 소비자에게 첫 행동을 유도하는지 본다. |
| x-youtube-description-conversion | min_x_strategy | 유튜브 설명란 전환 개선 X 글 | 콘텐츠에서 상담 전환으로 이어지는 단일 행동 유도를 본다. |
| landing-ailit-consult-home | min_landing_cro | Ailit 상담 랜딩 첫 화면 개선 | 첫 화면 병목과 카피 실험 설계를 동시에 검증한다. |
| landing-bootcamp-trial | min_landing_cro | 부트캠프 체험 신청 랜딩 개선 | 무료와 유료 사이 간극을 줄이는 카피 감각을 본다. |
| landing-telegram-join | min_landing_cro | 텔레그램 채널 합류 랜딩 개선 | 콘텐츠 채널 유입과 보상 설계를 점검한다. |
| retention-vip-first-week | min_membership_retention | VIP 신규 멤버 첫 칠 일 리텐션 개선 | 민 전용 멤버십 운영 감각을 직접 측정한다. |
| retention-bootcamp-first-week | min_membership_retention | 부트캠프 첫 주 유지 개선 | 초보자 친화 운영 문구와 미션 설계를 본다. |
| retention-ailit-followup | min_membership_retention | Ailit 입문 상품 후속 리텐션 개선 | 저가 입문에서 업셀로 이어지는 유지 구조를 본다. |
| research-ailit-competitor-homepage | min_agentic_research | Ailit 경쟁사 비교와 첫 화면 수정안 | 조사 설계가 전략 수정으로 이어지는지 보는 대표 과제다. |
| research-bootcamp-free-paid-bridge | min_agentic_research | 부트캠프 무료에서 유료 전환 장치 비교 조사 | 무료와 유료 브리지 장치의 조사 품질을 본다. |
| research-youtube-description-benchmark | min_agentic_research | 유튜브 설명란 전환 사례 비교 조사 | 설명란 문장 실험의 비교 기준이 서는지 본다. |

## 환경별 성공 규칙

### min_business_strategy

gate metric
- section_coverage >= 1.0
- keyword_coverage >= 0.5
- actionability >= 1.0
- priority_clarity >= 0.25

성공 신호
- 모든 섹션을 빠짐없이 채운다.
- 이번 주 또는 일주일 같은 실행 시점이 보인다.
- 전환 지표와 우선순위 한 가지가 분명하다.

실패 신호
- 허풍만 있고 채널, 실험, 지표가 비어 있다.
- 무엇을 먼저 할지 드러나지 않는다.

### min_x_strategy

gate metric
- section_coverage >= 1.0
- hook_strength >= 0.6
- engagement >= 0.6
- actionability >= 0.5
- single_action_clarity >= 0.5

성공 신호
- 후크가 문제를 바로 찌른다.
- 댓글유도와 행동유도가 각각 따로 살아 있다.
- 오늘 할 한 가지 행동이 명확하다.

실패 신호
- 동기부여성 문장만 있고 질문이 약하다.
- 행동유도가 여러 개라서 초점이 흐린다.

### min_landing_cro

gate metric
- section_coverage >= 1.0
- specificity >= 0.5
- copy_quality >= 0.6
- experiment_quality >= 0.5
- metric_quality >= 0.5

성공 신호
- 첫 화면 병목을 구체적으로 짚는다.
- 바꿀 카피 한 줄이 실제 문장으로 나온다.
- 반반 비교와 지표가 함께 설계된다.

실패 신호
- 카피수정이 추상적이거나 비어 있다.
- 실험과 지표가 분리되지 않는다.

### min_membership_retention

gate metric
- section_coverage >= 1.0
- specificity >= 0.5
- retention_mechanism >= 0.5
- metric_quality >= 0.5
- beginner_friendliness >= 0.2

성공 신호
- 이탈 구간이 날짜와 행동으로 보인다.
- 체크인이나 미션 같은 유지 장치가 실제 운영 단위로 나온다.
- 쉬운 말 톤과 지표가 함께 있다.

실패 신호
- 격려만 있고 운영 장치가 없다.
- 재방문과 이탈률을 어떻게 볼지 없다.

### min_agentic_research

gate metric
- section_coverage >= 1.0
- comparison_quality >= 0.5
- actionability >= 0.5
- specificity >= 0.5
- keyword_coverage >= 0.5

성공 신호
- 찾을정보와 비교기준이 따로 분리된다.
- 비교 표나 첫 화면 수정 같은 바로 다음 행동이 있다.
- 무엇을 보면 결론을 낼지 기준이 선다.

실패 신호
- 조사 계획이 아니라 요약 감상문처럼 쓴다.
- 다음행동이 나중에 보자 수준으로 흐린다.

## 삼자 비교 운영 규칙

1. current_policy와 patched_policy는 반드시 같은 task_id 순서로 답안을 채운다.
2. human_baseline은 이미 작성된 기준 답안을 그대로 둔다.
3. 정책 승격은 patched_policy가 current_policy보다 mean_total과 task_pass_count를 모두 올렸을 때만 검토한다.
4. 사람 기준선 대비 가장 낮은 env가 다음 보상 함수 또는 rollout 설계 병목 후보가 된다.

## 바로 다음 실행

1. current_policy 템플릿에 현재 정책 출력물을 채운다.
2. 패치 후보를 적용한 뒤 patched_policy 템플릿을 채운다.
3. `/Users/heomin/.hermes/hermes-agent/venv/bin/python scripts/evaluate_min_hermes_offline_set.py --lane current_policy=research/min_hermes_offline_eval_v1_current_policy_template.json --lane patched_policy=research/min_hermes_offline_eval_v1_patched_policy_template.json --lane human_baseline=research/min_hermes_offline_eval_v1_human_baseline.json` 형식으로 세 lane을 함께 채점한다.
4. env mean이 가장 낮은 축부터 보상 함수 또는 rollout 수정 실험으로 들어간다.

## 생성된 파일

- research/min_hermes_offline_eval_v1.json
- research/min_hermes_offline_eval_v1_human_baseline.json
- research/min_hermes_offline_eval_v1_current_policy_template.json
- research/min_hermes_offline_eval_v1_patched_policy_template.json
- scripts/evaluate_min_hermes_offline_set.py
