# 민 전용 Hermes 오프라인 평가 결과

- benchmark_version: v2
- primary_bottleneck: policy_discrimination_restored
- task_count: 12

## Lane summary

| lane | mean_total | pass_rate | task_pass_count | lane_passed |
| --- | ---: | ---: | ---: | --- |
| current_policy | 0.9979 | 1.0000 | 12/12 | yes |
| patched_policy | 0.9924 | 1.0000 | 12/12 | yes |

## current_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_business_strategy | 1.0000 | 1.0000 |
| min_landing_cro | 0.9875 | 1.0000 |
| min_x_strategy | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| landing-live-session-signup | 라이브 참여 신청 랜딩 개선 | 0.9750 |
| biz-google-ads-low-risk | 구글 광고 재가동 전 저위험 전략 설계 | 1.0000 |
| biz-youtube-telegram-bridge | 유튜브에서 텔레그램으로 넘어가는 중간 다리 전략 | 1.0000 |

## patched_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_business_strategy | 0.9927 | 1.0000 |
| min_landing_cro | 0.9800 | 1.0000 |
| min_x_strategy | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| biz-google-ads-low-risk | 구글 광고 재가동 전 저위험 전략 설계 | 0.9743 |
| biz-brand-collab-structure | 브랜드 신뢰를 지키는 협업 제안 구조 | 0.9743 |
| landing-brand-collab-inquiry | 기업 협업 문의 랜딩 개선 | 0.9800 |
