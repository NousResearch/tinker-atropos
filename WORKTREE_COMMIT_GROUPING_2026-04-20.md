# 워킹트리 커밋 묶음 정리

브랜치
- `feat/patch-sync-ops-followup`

현재 상태
- `git status --short` 기준 변경 항목 약 190개
- 한 번에 커밋하면 리뷰도 어렵고 다음 작업도 꼬인다
- 따라서 기능 축 기준으로 분리해야 한다

## 원칙
- 산출물과 코드 커밋을 분리한다
- `outputs/` 는 기본적으로 커밋하지 않는다
- 먼저 재현 가능한 코드와 테스트를 묶고, 문서는 그다음에 묶는다
- 지금 브랜치는 이미 여러 축이 섞여 있으므로 필요하면 깨끗한 워크트리에서 묶는 편이 안전하다

## 권장 커밋 순서

### 묶음 1. 풀 퍼널과 변환기 핵심
목적
- 오늘 실제 마감에 직접 연결되는 코드 축

포함 후보
- `build_business_to_landing_loop.py`
- `build_business_to_retention_loop.py`
- `build_business_to_x_loop.py`
- `build_research_to_business_loop.py`
- `run_research_to_business_to_landing.py`
- `run_research_to_business_to_retention.py`
- `run_research_to_business_to_x.py`
- `run_research_to_full_funnel.py`
- `run_full_funnel_daily.sh`
- `run_full_funnel_operational.sh`
- `publish_ready_exporter.py`
- 관련 테스트
  - `test_build_business_to_landing_loop.py`
  - `test_build_business_to_retention_loop.py`
  - `test_build_business_to_x_loop.py`
  - `test_build_research_to_business_loop.py`
  - `test_run_research_to_full_funnel_output.py`

권장 커밋 메시지
- `feat: add reward-first full funnel loop and quality comparison`

### 묶음 2. 운영 문서와 마감 문서
목적
- 오늘 마감 판단과 운영 규칙을 문서로 고정

포함 후보
- `OPERATING_MODES.md`
- `NEXT_7_STEPS_ROADMAP.md`
- `quality_comparison_report.md`
- `CLOSEOUT_STATUS_2026-04-20.md`
- 루프 설명 문서
  - `business_to_landing_loop.md`
  - `business_to_retention_loop.md`
  - `business_to_x_loop.md`
  - `research_to_business_loop.md`
  - `research_to_business_to_landing_loop.md`
  - `research_to_business_to_retention_loop.md`
  - `research_to_business_to_x_loop.md`
  - `research_to_full_funnel_loop.md`

권장 커밋 메시지
- `docs: record full funnel operating modes and closeout status`

### 묶음 3. 민 전용 환경과 오프라인 평가
목적
- 환경 정의와 승격 기준 축을 따로 보존

포함 후보
- `tinker_atropos/environments/min_*`
- `configs/min_*`
- `research/`
- `run_min_hermes_promotion_eval.py`
- 관련 테스트
  - `test_generate_min_hermes_policy_answers.py`
  - `test_evaluate_min_hermes_offline_set.py`
  - `test_min_hermes_offline_eval_v2.py`
  - `test_min_hermes_offline_eval_v3.py`
  - `tinker_atropos/tests/test_min_*`

권장 커밋 메시지
- `feat: add min environments and layered offline promotion eval`

### 묶음 4. 운영 상태와 페이퍼클립 동기화
목적
- promotion eval, environment status, full funnel status 같은 운영 자동화 축 분리

포함 후보
- `ops/README.md`
- `ops/full_funnel_status.py`
- `ops/environment_status.py`
- `ops/promotion_eval_daily.py`
- `ops/promotion_eval_status.py`
- `ops/paperclip_issue_matcher.py`
- `ops/paperclip_tinker_atropos_sync.py`
- `ops/tinker_paperclip_sync.py`
- `ops/run_full_funnel_status.py`
- `ops/run_environment_status.py`
- `ops/run_promotion_eval_daily.py`
- `ops/run_promotion_eval_status.py`
- `ops/paperclip_tinker_closure_criteria.md`
- 관련 테스트
  - `test_full_funnel_status.py`
  - `test_environment_status.py`
  - `test_promotion_eval_daily.py`
  - `test_promotion_eval_status.py`
  - `test_run_full_funnel_status.py`
  - `test_run_environment_status.py`
  - `test_run_promotion_eval_status.py`
  - `test_tinker_paperclip_sync.py`

권장 커밋 메시지
- `feat: add tinker ops status and paperclip sync automation`

### 묶음 5. 피드백 패치 사이클
목적
- 지금 당장 마감과 직접 관계 없는 보조 자동화 축 분리

포함 후보
- `feedback/`
- `inputs/`
- `apply_feedback_fill_sheet.py`
- `bootstrap_feedback_entry.py`
- `extract_feedback_hints.py`
- `generate_adjustment_draft.py`
- `generate_preset_score_draft.py`
- `generate_score_patch_draft.py`
- `generate_score_patch_file_draft.py`
- `generate_score_patch_v4a.py`
- `print_feedback_missing_form.py`
- `refresh_feedback_missing_note.py`
- `refresh_feedback_three_line_note.py`
- `run_feedback_patch_cycle.py`
- 관련 테스트
  - `test_apply_feedback_fill_sheet.py`
  - `test_apply_patch_draft.py`
  - `test_bootstrap_feedback_entry.py`
  - `test_feedback_hints.py`
  - `test_generate_score_patch_draft.py`
  - `test_generate_score_patch_file_draft.py`
  - `test_patch_precision.py`
  - `test_print_feedback_missing_form.py`
  - `test_refresh_feedback_missing_note.py`
  - `test_refresh_feedback_three_line_note.py`

권장 커밋 메시지
- `feat: add feedback-driven patch cycle helpers`

### 묶음 6. 나머지 기반 인프라 실험 축
목적
- 기본 설정, 훈련 런처, 스모크 러너, 범용 스크립트 같은 혼합 축 정리

포함 후보
- `.gitignore`
- `configs/default.yaml`
- `configs/default_public_normal_lite.yaml`
- `configs/quick_test.yaml`
- `configs/smoke_qwen*.yaml`
- `launch_training.py`
- `tinker_atropos/config.py`
- `tinker_atropos/trainer.py`
- `tinker_atropos/environments/gsm8k_tinker.py`
- `tinker_atropos/tests/test_managed_server.py`
- 범용 실행기
  - `run_min_env_smokes.py`
  - `run_remaining_micro_training_retries.py`
  - `run_remaining_training_retries.py`
  - `run_repeat_generic.py`
  - `run_ultra_ready_smoke*.py`
  - `run_default_public_ready_*.py`
  - `run_compare_business_x.py`
- `scripts/`

권장 커밋 메시지
- `refactor: organize generic smoke and training utilities`

## 당장 커밋하지 말아야 할 것
- `outputs/`
- `prompt-exports/`
- `data/`
- `temp.json`
- 필요 없으면 `sample_*` 입력 파일도 마지막 문서 커밋으로 보내거나 제외

## 추천 실행 방식
### 안전한 방식
1. 지금 브랜치에서는 문서만 남기고 직접 대량 커밋하지 않는다
2. 깨끗한 워크트리를 만든다
3. 위 묶음 순서대로 필요한 파일만 골라 staged diff 를 만든다
4. 각 묶음마다 좁은 테스트만 돌리고 커밋한다

### 최소 실행 순서
1. 묶음 1
2. 묶음 2
3. 묶음 4
4. 묶음 3
5. 묶음 5
6. 묶음 6

이 순서가 좋은 이유
- 오늘 마감에 직접 필요한 코드와 문서를 먼저 고정할 수 있다
- 운영 자동화 축을 앞쪽으로 당겨서 실제 사용 가치가 높은 묶음을 먼저 분리할 수 있다
- 민 전용 환경 대규모 축은 그다음에 분리해도 된다

## 현재 판단
- 기능 미완성보다 정리 미완성이 크다
- 따라서 다음 실작업 우선순위는 새 기능 추가가 아니라 커밋 묶음 분리다
