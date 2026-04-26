# 민 전용 Hermes 오프라인 평가 결과

- benchmark_version: v4_production_workflow
- primary_bottleneck: agentic_production_routing_and_verification
- task_count: 5

## Lane summary

| lane | mean_total | pass_rate | task_pass_count | lane_passed |
| --- | ---: | ---: | ---: | --- |
| current_policy | 0.4251 | 0.0000 | 0/5 | no |
| actual_hermes_current_session | 1.0000 | 1.0000 | 5/5 | yes |
| production_router_policy | 1.0000 | 1.0000 | 5/5 | yes |
| failure_policy | 0.0649 | 0.0000 | 0/5 | no |

## current_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_production_router | 0.4251 | 0.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| production-router-figma-implementation | 피그마 구현 요청 라우팅 | 0.3548 |
| production-router-codex-in-hermes | 헤르메스 안 코덱스 씨엘아이 실행 요청 라우팅 | 0.3848 |
| production-router-landing-build | 웹사이트 제작 요청 라우팅 | 0.4475 |

## actual_hermes_current_session

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_production_router | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| production-router-landing-build | 웹사이트 제작 요청 라우팅 | 1.0000 |
| production-router-image-to-video | 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅 | 1.0000 |
| production-router-figma-implementation | 피그마 구현 요청 라우팅 | 1.0000 |

## production_router_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_production_router | 1.0000 | 1.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| production-router-landing-build | 웹사이트 제작 요청 라우팅 | 1.0000 |
| production-router-image-to-video | 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅 | 1.0000 |
| production-router-figma-implementation | 피그마 구현 요청 라우팅 | 1.0000 |

## failure_policy

### Env summary

| env | mean_total | pass_rate |
| --- | ---: | ---: |
| min_agentic_production_router | 0.0649 | 0.0000 |

### Weakest tasks

| task_id | title | total |
| --- | --- | ---: |
| production-router-landing-build | 웹사이트 제작 요청 라우팅 | 0.0600 |
| production-router-image-to-video | 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅 | 0.0600 |
| production-router-figma-implementation | 피그마 구현 요청 라우팅 | 0.0600 |
