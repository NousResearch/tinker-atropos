# Tinker Atropos worktree commit grouping 2026-04-26

## 현재 브랜치

`feat/patch-sync-ops-followup`

## Repo Prompt gate

`rp-cli -e 'windows'` 실행 결과 RepoPrompt 앱 또는 MCP 서버 연결 실패가 났다.
따라서 이번 점검은 명시적 fallback 으로 Hermes 파일 도구와 터미널을 사용했다.

## 현재 남은 변경 축

### 묶음 일. 제작 라우터 평가 환경과 점수판

포함 후보:

- `tinker_atropos/environments/min_agentic_production_router_tinker.py`
- `tinker_atropos/tests/test_min_agentic_production_router_env.py`
- `scripts/evaluate_min_hermes_offline_set.py`
- `test_evaluate_min_hermes_offline_set.py`
- `research/min_hermes_offline_eval_v4_production_workflow_spec.json`
- `research/min_hermes_offline_eval_v4_production_workflow_spec.md`
- `research/min_hermes_offline_eval_v4_current_policy_template.json`
- `research/min_hermes_offline_eval_v4_production_router_policy_template.json`
- `research/min_hermes_offline_eval_v4_failure_policy_template.json`
- `research/min_hermes_offline_eval_v4_scoreboard.json`
- `research/min_hermes_offline_eval_v4_scoreboard.md`

권장 커밋 메시지:

`feat: add min hermes production router evaluation lane`

### 묶음 이. 실제 헤르메스 샘플 수집과 번들러

포함 후보:

- `scripts/collect_production_router_hermes_samples.py`
- `scripts/build_production_router_sample_bundle.py`
- `test_collect_production_router_hermes_samples.py`
- `test_build_production_router_sample_bundle.py`
- `research/production_router_actual_samples/2026-04-26-hermes-live-guided-full/`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_guided_full.json`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_guided_full_scoreboard.json`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_guided_full_scoreboard.md`

권장 커밋 메시지:

`feat: collect and score live hermes production router samples`

### 묶음 삼. 실험 산출물과 마감 문서

포함 후보:

- `inputs/hermes-agent-production-upgrade-2026-04-26.txt`
- `research/min_hermes_offline_eval_v4_actual_hermes_current_session.json`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_smoke.json`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_smoke_scoreboard.json`
- `research/min_hermes_offline_eval_v4_actual_hermes_live_smoke_scoreboard.md`
- `research/min_hermes_offline_eval_v4_actual_scoreboard.json`
- `research/min_hermes_offline_eval_v4_actual_scoreboard.md`
- `CLOSEOUT_STATUS_2026-04-26.md`
- `WORKTREE_COMMIT_GROUPING_2026-04-26.md`

권장 커밋 메시지:

`docs: record production router evaluation closeout`

## 기본 제외

- `outputs/` 는 이번 커밋 범위에서 제외한다.
- `daily-full-funnel-reliability-report-2026-04-22.md` 는 오늘 v4 production router 작업과 직접 연결되지 않으므로 별도 판단 대상으로 둔다.

## 오늘 검증

```bash
/Users/heomin/.hermes/hermes-agent/venv/bin/python -m pytest tinker_atropos/tests/test_min_agentic_production_router_env.py test_evaluate_min_hermes_offline_set.py test_build_production_router_sample_bundle.py test_collect_production_router_hermes_samples.py -q
```

결과:

```text
16 passed in 3.98s
```

## 지금 판정

기능은 닫혔고 남은 일은 커밋 단위 정리다.
