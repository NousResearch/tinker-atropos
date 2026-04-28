# 민 전용 Hermes 오프라인 평가 결과

- benchmark_version: v3
- primary_bottleneck: single_tail_delta_promotion_gate
- task_count: 1

## Lane summary

| lane | mean_total | pass_rate | task_pass_count | lane_passed |
| --- | ---: | ---: | ---: | --- |
| current_policy | 0.9750 | 0.0000 | 0/1 | no |
| patched_policy | 0.9800 | 1.0000 | 1/1 | yes |

## current_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_landing_cro | 0.9750 | 0.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| landing-live-session-signup-tail | 라이브 참여 신청 랜딩 마지막 꼬리 과제 | 0.9750 |

## patched_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_landing_cro | 0.9800 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| landing-live-session-signup-tail | 라이브 참여 신청 랜딩 마지막 꼬리 과제 | 0.9800 |
