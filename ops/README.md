# 외부 실행 래퍼

목적
- Paperclip 안에서 무거운 코드 실행을 직접 돌리지 않고, 외부 저장소에서 `rp-cli` 와 `codex` 와 테스트를 실행한 뒤 결과만 다시 회사 카드로 동기화한다.

핵심 원칙
- Hermes는 조종석이다.
- Paperclip은 승인, 우선순위, 실패 감시, 요약만 맡는다.
- `rp-cli` 는 복잡한 코드 조사 카드에서만 선택적으로 쓴다.
- 장시간 학습은 항상 외부 백그라운드로 돌린다.
- Paperclip API 호출은 인증된 컬 표준으로 통일한다.

파일
- `run_task.py` : 외부 실행 계획 생성 또는 실제 실행
- `run_task.sh` : 빠른 쉘 진입점
- `run_apply_patch.py` : patch draft 실제 적용 + 승인 게이트 확인 + 테스트 + 상태 판단
- `hide_patch_sync_verification_cards.py` : 검증용 Patch Sync Verification 임시 카드를 자동 숨김 처리
- `run_apply_patch.sh` : patch 적용용 빠른 쉘 진입점
- `run_review_queue.py` : patch draft review queue 요약 + Paperclip 동기화
- `run_review_queue.sh` : review queue 빠른 쉘 진입점
- `run_environment_status.py` : 환경 파일, 테스트, 설정, 산출물 상태 요약 + Paperclip 동기화
- `run_environment_status.sh` : 환경 상태 점검 빠른 쉘 진입점
- `run_full_funnel_status.py` : 최근 full funnel summary 산출물 점검 + Paperclip 동기화
- `run_full_funnel_status.sh` : full funnel 상태 점검 빠른 쉘 진입점
- `run_preset_scoreboard.py` : preset 별 점수와 최고 headline 집계 + Paperclip 동기화
- `run_preset_scoreboard.sh` : preset scoreboard 빠른 쉘 진입점
- `sync_result_to_paperclip.py` : 이슈 코멘트와 상태 동기화
- `paperclip_tinker_atropos_sync.py` : Tinker Atropos Ops 회사 카드 동기화 초안, 제목 기준 최신 routine 카드 매핑 포함
- `paperclip_tinker_closure_criteria.md` : TIN-15, TIN-16 닫힘 기준 문서
- `external_execution.py` : 계획 생성과 쉘 스크립트 렌더링 로직
- `apply_patch_draft.py` : generated patch draft 파싱과 실제 파일 적용
- `review_patch_queue.py` : patch draft 최신성, 적용 상태, 검토 우선순위 요약
- `patch-draft-archive-policy.md` : archived patch draft 운영 규칙 문서
- `environment_status.py` : 환경 다섯 개의 파일, 테스트, 설정, 산출물 상태 요약
- `full_funnel_status.py` : recent summary 디렉터리의 best/final/report/one-line 상태 요약
- `preset_scoreboard.py` : preset 별 평균 점수와 최고 landing headline 집계
- `hermes-standard-instruction.md` : Hermes에게 줄 표준 지시문

가장 자주 쓰는 예시

계획만 출력
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_task.py \
  --title "Feedback Patch Draft Review Queue" \
  --task-type patch-review \
  --prompt "feedback patch 분류 로직 개선" \
  --target generate_score_patch_v4a.py \
  --target test_patch_precision.py \
  --use-rp \
  --test-command "pytest test_patch_precision.py -q"
```

실제 실행
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_task.py \
  --title "Feedback Patch Draft Review Queue" \
  --task-type patch-review \
  --prompt "feedback patch 분류 로직 개선" \
  --target generate_score_patch_v4a.py \
  --target test_patch_precision.py \
  --use-rp \
  --test-command "pytest test_patch_precision.py -q" \
  --execute
```

Paperclip 카드에 결과 동기화
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python -m ops.sync_result_to_paperclip \
  --issue-id 4bc07c36-9a5d-43ba-b38d-16cf574a5f85 \
  --comment "외부 실행 래퍼 기본 골격과 테스트를 추가했다." \
  --status todo
```

Tinker routine 카드 상태 일괄 동기화
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
PAPERCLIP_API_KEY=*** python3 ops/paperclip_tinker_atropos_sync.py --base-url http://127.0.0.1:3100
```

Patch draft 실제 적용
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_apply_patch.py \
  feedback/patch_drafts/score-patch-v4a-20260413-210049.patch \
  --test-command "pytest test_build_business_to_x_loop.py -q" \
  --test-command "pytest test_build_business_to_landing_loop.py -q" \
  --test-command "pytest test_build_business_to_retention_loop.py -q"
```

기본 승인 게이트
- `run_apply_patch.py` 코멘트는 첫 줄에 `[상태 · 우선순위] 요약` 형식을 먼저 두고, 아래에 `결과 요약`, `적용 결과`, `테스트`, `롤백` 섹션을 이어 붙인다.
- `run_apply_patch.py` 는 기본적으로 patch file 이 같은 drafts 디렉터리의 `summarize_patch_queue(...)` 결과에서 현재 `top_review_candidate` 일 때만 적용한다.
- 승인되지 않은 patch 는 파일 변경도 하지 않고 테스트도 실행하지 않으며, 결과 코멘트에 `approved`, `approval_status`, `approval_reason`, `next_action` 을 남긴다.
- 검토 대기 순서를 무시하고 강제로 실행해야 할 때만 `--skip-approval-check` 를 사용한다.

승인 게이트 우회 실행
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_apply_patch.py \
  feedback/patch_drafts/score-patch-v4a-20260413-200417.patch \
  --skip-approval-check \
  --test-command "pytest test_build_business_to_x_loop.py -q"
```

검증용 Patch Sync Verification 임시 카드 자동 숨김
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
PAPERCLIP_API_KEY=*** python ops/hide_patch_sync_verification_cards.py
```

Patch draft review queue 요약
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python3 ops/run_review_queue.py --drafts-dir feedback/patch_drafts
```

비실행 patch draft 자동 보관
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python3 ops/run_review_queue.py --drafts-dir feedback/patch_drafts --archive-nonactionable
```

Environment status monitor
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_environment_status.py
```

Full funnel run monitor
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_full_funnel_status.py
```

Preset performance scoreboard
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python ops/run_preset_scoreboard.py
```

권장 운영 방식
1. Paperclip 카드 하나를 고른다.
2. Hermes가 외부 실행 프롬프트를 만든다.
3. 필요할 때만 `--use-rp` 를 켠다.
4. 코덱스와 테스트를 외부에서 실행한다.
5. 결과만 Paperclip 이슈에 반영한다.
