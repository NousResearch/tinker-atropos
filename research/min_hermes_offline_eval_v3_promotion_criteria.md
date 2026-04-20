# min_hermes_offline_eval_v3 승격 기준 메모

## 목적
v2가 current hardening으로 다시 포화된 뒤에도 patched 승격 신호를 유지하기 위해 마지막 단일 꼬리 과제를 따로 떼어 승격 기준으로 고정한다.

## 대상 과제
- task_id: `landing-live-session-signup-tail`
- env: `min_landing_cro`
- 이유: current와 patched의 남은 차이가 가장 작지만 실제로는 아직 사라지지 않은 마지막 꼬리 과제다.

## 최신 결과
- current_policy
  - mean_total: `0.9750`
  - task_pass_count: `0/1`
  - lane_passed: `no`
- patched_policy
  - mean_total: `0.9800`
  - task_pass_count: `1/1`
  - lane_passed: `yes`

## 실제 차이
### 공통으로 이미 맞춘 것
- `section_coverage = 1.0`
- `copy_quality = 1.0`
- `experiment_quality = 1.0`
- `keyword_coverage = 1.0`

즉 지금은 카피 구조나 실험 문장 문제가 아니라, **지표 문장 완성도 하나만 남은 상태**다.

### current가 아직 못 넘는 것
- `metric_quality = 0.8333`
- 실패 gate
  - `metric_quality >= 1.0`

### patched가 넘는 것
- `metric_quality = 1.0`
- 성공 gate
  - `metric_quality >= 1.0`

## 왜 이런 차이가 나는가
`min_landing_cro` 환경의 지표 품질은 아래 여섯 신호를 얼마나 다 채우는지로 결정된다.
- `클릭률`
- `전환율`
- `신청`
- `%`
- `퍼센트`
- `건`

current 답안은 지금 아래 수준까지는 왔다.
- `신청 전환율 3퍼센트(3%)`
- `참여율 5퍼센트(5%)`
- `리플레이 시청률 7퍼센트(7%)`
- `클릭률 3퍼센트(3%)`

이 답안은 `건` 신호가 없다.
그래서 여섯 신호 중 다섯 개만 잡혀 `metric_quality = 5/6 = 0.8333` 이다.

patched 답안은 아래처럼 `건` 까지 직접 넣는다.
- `신청 전환율 50건`
- `참여율 4퍼센트`
- `리플레이 시청률 20퍼센트`
- `클릭률 3%`
- `20%`

이로써 지표 관련 여섯 신호가 모두 잡혀 `metric_quality = 1.0` 이 된다.

## 승격 기준 해석
앞으로 patched 승격 여부는 아래 한 줄로 판단한다.

- `landing-live-session-signup-tail` 에서 `metric_quality 1.0` 을 current가 아직 못 만들고 patched만 만들면 patched 승격 신호 유지

조금 더 풀어 쓰면:
- current가 이미 운영 품질 면에서는 충분히 좋아도
- 마지막으로 `지표 문장을 완전하게 설계하는가` 에서 patched가 앞서면
- 그 차이는 승격 판단에 쓸 가치가 있다.

## 운영 원칙
- `v1`: 회귀 방지용 만점 세트
- `v2`: current hardening 추적용 세트
- `v3`: 마지막 승격 구분용 단일 꼬리 세트

즉 지금부터는 current를 무조건 더 올리는 것보다,
`v3`의 단일 차이가 정말 민 실무에서 중요한 승격 기준인지 유지·관리하는 것이 더 중요하다.

## 다음에 볼 것
- 랜딩 current를 더 올릴지 여부는 아래 질문으로 결정한다.
  - 정말 `건` 신호까지 current에 넣어야 하나
  - 아니면 이 차이를 patched 승격 기준으로 남겨두는 것이 더 운영적으로 유용한가

현재 기준으로는 후자가 더 유용하다.
