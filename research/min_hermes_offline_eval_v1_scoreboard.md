# 민 전용 Hermes 오프라인 평가 결과

- benchmark_version: v1
- primary_bottleneck: offline_evaluation_missing
- task_count: 15

## Lane summary

| lane | mean_total | pass_rate | task_pass_count | lane_passed |
| --- | ---: | ---: | ---: | --- |
| current_policy | 1.0000 | 1.0000 | 15/15 | yes |
| patched_policy | 1.0000 | 1.0000 | 15/15 | yes |
| human_baseline | 0.8928 | 0.9333 | 14/15 | yes |

## current_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_research | 1.0000 | 1.0000 |
| min_business_strategy | 1.0000 | 1.0000 |
| min_landing_cro | 1.0000 | 1.0000 |
| min_membership_retention | 1.0000 | 1.0000 |
| min_x_strategy | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| research-ailit-competitor-homepage | Ailit 경쟁사 비교와 첫 화면 수정안 | 1.0000 |
| research-bootcamp-free-paid-bridge | 부트캠프 무료에서 유료 전환 장치 비교 조사 | 1.0000 |
| research-youtube-description-benchmark | 유튜브 설명란 전환 사례 비교 조사 | 1.0000 |

## patched_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_research | 1.0000 | 1.0000 |
| min_business_strategy | 1.0000 | 1.0000 |
| min_landing_cro | 1.0000 | 1.0000 |
| min_membership_retention | 1.0000 | 1.0000 |
| min_x_strategy | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| research-ailit-competitor-homepage | Ailit 경쟁사 비교와 첫 화면 수정안 | 1.0000 |
| research-bootcamp-free-paid-bridge | 부트캠프 무료에서 유료 전환 장치 비교 조사 | 1.0000 |
| research-youtube-description-benchmark | 유튜브 설명란 전환 사례 비교 조사 | 1.0000 |

## human_baseline

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_research | 0.8552 | 1.0000 |
| min_business_strategy | 0.9733 | 1.0000 |
| min_landing_cro | 0.8417 | 0.6667 |
| min_membership_retention | 0.8824 | 1.0000 |
| min_x_strategy | 0.9112 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| landing-bootcamp-trial | 부트캠프 체험 신청 랜딩 개선 | 0.7800 |
| landing-telegram-join | 텔레그램 채널 합류 랜딩 개선 | 0.8050 |
| research-youtube-description-benchmark | 유튜브 설명란 전환 사례 비교 조사 | 0.8192 |
