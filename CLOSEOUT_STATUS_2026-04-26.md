# Tinker Atropos closeout status 2026-04-26

## 범위

오늘 이어서 닫은 범위는 민 전용 헤르메스 제작 라우터 평가선이다.
기존 full funnel 이 헤르메스 제작 운영 요청을 일반 콘텐츠 전환 문제로 압축하는 한계를 확인했고, 그 한계를 별도 평가 환경으로 분리했다.

## 오늘 확인한 사실

- 새 환경 파일: `tinker_atropos/environments/min_agentic_production_router_tinker.py`
- 새 평가 세트: `research/min_hermes_offline_eval_v4_production_workflow_spec.json`
- 새 평가 설명: `research/min_hermes_offline_eval_v4_production_workflow_spec.md`
- 평가기 연결: `scripts/evaluate_min_hermes_offline_set.py`
- 실제 헤르메스 샘플 수집기: `scripts/collect_production_router_hermes_samples.py`
- 실제 답변 번들러: `scripts/build_production_router_sample_bundle.py`
- 실제 샘플 폴더: `research/production_router_actual_samples/2026-04-26-hermes-live-guided-full`

## 점수판 결과

파일: `research/min_hermes_offline_eval_v4_actual_hermes_live_guided_full_scoreboard.md`

| lane | mean_total | pass_rate | task_pass_count | lane_passed |
| --- | ---: | ---: | ---: | --- |
| current_policy | 0.4251 | 0.0000 | 0/5 | no |
| actual_hermes_live_guided_full | 1.0000 | 1.0000 | 5/5 | yes |
| production_router_policy | 1.0000 | 1.0000 | 5/5 | yes |
| failure_policy | 0.0649 | 0.0000 | 0/5 | no |

## 실제 샘플 수집 결과

파일: `research/production_router_actual_samples/2026-04-26-hermes-live-guided-full/manifest.json`

- task_count_requested: 5
- written_count: 5
- failed_task_ids: []
- skipped_task_ids: []

## 검증 명령과 결과

실행 위치: `/Users/heomin/.hermes/hermes-agent/tinker-atropos`

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python -m pytest tinker_atropos/tests/test_min_agentic_production_router_env.py test_evaluate_min_hermes_offline_set.py test_build_production_router_sample_bundle.py test_collect_production_router_hermes_samples.py -q
```

결과:

```text
16 passed in 3.98s
```

## 운영 판정

- 기능 판정: 제작 라우터 평가선은 사용 가능 상태다.
- 남은 성격: 기능 구현보다 저장소 정리와 커밋 묶음 성격이다.
- 다음 운영 기준: 헤르메스 제작 요청의 품질은 일반 full funnel 점수보다 v4 production router 평가선으로 우선 점검한다.
- 유의점: 실제 헤르메스 평가는 답변 품질 자체보다 과제별 라우팅 지시문 고정 여부가 점수에 큰 영향을 준다.

## 다음 권장 작업

1. v4 production router 변경분을 하나의 기능 커밋으로 묶는다.
2. 별도 요청이 오기 전까지 current 를 억지로 production_router_policy 에 맞추지 않는다.
3. 이후 민의 실제 제작 요청 샘플이 쌓이면 `research/production_router_actual_samples/` 아래에 새 런으로 추가 수집한다.
4. 새 실패 패턴이 생기면 평가 세트와 스킬에 함께 반영한다.
