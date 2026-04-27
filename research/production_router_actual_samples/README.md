# production router actual samples

## 목적

이 폴더는 민의 실제 제작 요청에 대한 헤르메스 답변 샘플을 날짜별 실행 단위로 보관한다.
샘플은 v4 제작 라우터 평가선의 실제 회귀 자료로 쓴다.

## 고정 원칙

- `current_policy` 는 기준 정책에 억지로 맞추지 않는다.
- 새 샘플은 새 날짜 런 폴더로 추가한다.
- 기존 샘플 폴더를 덮어쓰지 않는다.
- 실패가 나오면 답변을 고쳐 덮어쓰기보다 실패 패턴을 평가 세트와 스킬에 반영한다.
- 샘플 폴더에는 `manifest.json` 을 반드시 남긴다.

## 새 런 추가 절차

실행 위치:

```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
```

샘플 수집:

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python scripts/collect_production_router_hermes_samples.py   --benchmark research/min_hermes_offline_eval_v4_production_workflow_spec.json   --answer-dir research/production_router_actual_samples/YYYY-MM-DD-hermes-live-guided-full   --lane-name actual_hermes_YYYY_MM_DD   --hermes-command hermes   --timeout 300   --keep-going
```

답변 번들 생성:

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python scripts/build_production_router_sample_bundle.py   --benchmark research/min_hermes_offline_eval_v4_production_workflow_spec.json   --answer-dir research/production_router_actual_samples/YYYY-MM-DD-hermes-live-guided-full   --lane-name actual_hermes_YYYY_MM_DD   --out research/min_hermes_offline_eval_v4_actual_hermes_YYYY_MM_DD.json
```

점수판 생성:

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python scripts/evaluate_min_hermes_offline_set.py   --benchmark research/min_hermes_offline_eval_v4_production_workflow_spec.json   --lane current_policy=research/min_hermes_offline_eval_v4_current_policy_template.json   --lane actual_hermes_YYYY_MM_DD=research/min_hermes_offline_eval_v4_actual_hermes_YYYY_MM_DD.json   --lane production_router_policy=research/min_hermes_offline_eval_v4_production_router_policy_template.json   --lane failure_policy=research/min_hermes_offline_eval_v4_failure_policy_template.json   --markdown-out research/min_hermes_offline_eval_v4_actual_hermes_YYYY_MM_DD_scoreboard.md   > research/min_hermes_offline_eval_v4_actual_hermes_YYYY_MM_DD_scoreboard.json
```

## 실패 패턴 반영 절차

새 점수판에서 실패가 나오면 아래 순서로 닫는다.

1. 실패 과제의 `task_id`, 빠진 용어, 빠진 검증, 실제 답변 경로를 적는다.
2. 같은 실패가 재발 가능한 운영 패턴인지 본다.
3. 재발 가능하면 `research/min_hermes_offline_eval_v4_production_workflow_spec.json` 의 과제나 성공 규칙에 반영한다.
4. 실행 절차나 라우팅 규칙이면 관련 Hermes 스킬에도 반영한다.
5. 평가 세트와 스킬 반영 뒤 좁은 테스트를 실행한다.

권장 테스트:

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python -m pytest   tinker_atropos/tests/test_min_agentic_production_router_env.py   test_evaluate_min_hermes_offline_set.py   test_build_production_router_sample_bundle.py   test_collect_production_router_hermes_samples.py   -q
```
