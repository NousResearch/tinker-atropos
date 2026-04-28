# v4 production router operating policy

작성 시각: 2026-04-28 09:21:33 AEST

## 결론

v4 제작 라우터 평가선은 운영 유지 상태다.
`current_policy` 를 `production_router_policy` 에 억지로 맞추지 않는다.

## 이유

`current_policy` 의 낮은 점수는 열린 버그가 아니라 기존 일반 퍼널 정책의 한계를 보여주는 기준선이다.
이 기준선이 남아 있어야 실제 헤르메스 라우팅과 제작 라우터 정책의 개선 폭을 계속 볼 수 있다.

## 고정 기준

- `current_policy` 는 비교 기준선으로 보존한다.
- `production_router_policy` 는 목표 기준선으로 보존한다.
- `failure_policy` 는 평가기가 헐거워졌는지 확인하는 음성 대조군으로 보존한다.
- 실제 헤르메스 샘플은 날짜별 새 레인으로만 추가한다.
- 새 실패 패턴은 답변 하나를 수동 보정하는 방식이 아니라 평가 세트와 스킬에 반영한다.

## 새 실제 샘플 위치

`research/production_router_actual_samples/`

새 런은 아래 이름 규칙을 쓴다.

`YYYY-MM-DD-hermes-live-guided-full`

## 실패 패턴 반영 기준

아래 조건 중 하나라도 맞으면 평가 세트 또는 스킬을 갱신한다.

- 선행 경로를 빠뜨린다.
- 실행 표면을 잘못 고른다.
- 산출물 경로가 없다.
- 검증 없이 완료 보고한다.
- 옵시디언, 스킬, 평가 세트 중 어디에도 학습 기록을 남기지 않는다.

## 검증 명령

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python -m pytest   tinker_atropos/tests/test_min_agentic_production_router_env.py   test_evaluate_min_hermes_offline_set.py   test_build_production_router_sample_bundle.py   test_collect_production_router_hermes_samples.py   -q
```
