# 2026-04-16 local_trusted sync 커밋 묶음 정리

## 목표
- local_trusted 로컬 Paperclip 보드에서는 무인증 동기화가 되도록 코드와 운영 셸을 묶음
- 운영 문서와 복구 기록은 별도 문서 커밋으로 분리

## 현재 관련 변경 파일
### 코드/테스트
- `ops/paperclip_curl.py`
- `test_sync_result_to_paperclip.py`
- `run_full_funnel_operational.sh`
- `test_automation_files.py`

### 문서/운영 기록
- `ops/README.md`
- `automation_examples.md`
- `ops/paperclip_tinker_closure_criteria.md`
- `ops/2026-04-16-local-trusted-sync-recovery.md`
- `ops/2026-04-16-local-trusted-sync-commit-bundles.md`

## 권장 커밋 묶음

### 커밋 1
제목
- `fix(ops): allow local_trusted paperclip sync without api key`

포함 파일
- `ops/paperclip_curl.py`
- `test_sync_result_to_paperclip.py`
- `run_full_funnel_operational.sh`
- `test_automation_files.py`

의도
- `ops/paperclip_curl.py` 에서 루프백 + `local_trusted` 감지 시 무인증 curl 허용
- `run_full_funnel_operational.sh` 에서 `PAPERCLIP_API_KEY` 없더라도 로컬 `local_trusted` 면 동기화 실행
- 셸 래퍼가 더 이상 `paperclip_sync=skipped_missing_api_key` 에 묶이지 않음
- 회귀 테스트 추가

스테이징 명령
```bash
git -C /Users/heomin/.hermes/hermes-agent/tinker-atropos add \
  ops/paperclip_curl.py \
  test_sync_result_to_paperclip.py \
  run_full_funnel_operational.sh \
  test_automation_files.py
```

커밋 명령
```bash
git -C /Users/heomin/.hermes/hermes-agent/tinker-atropos commit -m "fix(ops): allow local_trusted paperclip sync without api key"
```

검증 명령
```bash
pytest -o addopts='' -q \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/test_automation_files.py \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/test_sync_result_to_paperclip.py \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/test_tinker_paperclip_sync.py
bash -n /Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh
```

### 커밋 2
제목
- `docs(ops): document local_trusted paperclip sync workflow`

포함 파일
- `ops/README.md`
- `automation_examples.md`
- `ops/paperclip_tinker_closure_criteria.md`
- `ops/2026-04-16-local-trusted-sync-recovery.md`
- `ops/2026-04-16-local-trusted-sync-commit-bundles.md`

의도
- local_trusted 환경에서 키 없이 동기화되는 운영 규칙 문서화
- 복구 과정과 증거 기록 보존
- 다음 작업자가 바로 같은 흐름을 재사용 가능하게 함

스테이징 명령
```bash
git -C /Users/heomin/.hermes/hermes-agent/tinker-atropos add \
  ops/README.md \
  automation_examples.md \
  ops/paperclip_tinker_closure_criteria.md \
  ops/2026-04-16-local-trusted-sync-recovery.md \
  ops/2026-04-16-local-trusted-sync-commit-bundles.md
```

커밋 명령
```bash
git -C /Users/heomin/.hermes/hermes-agent/tinker-atropos commit -m "docs(ops): document local_trusted paperclip sync workflow"
```

## 한 번에 묶고 싶을 때
로컬 복구와 문서화까지 하나로 끝내려면 아래 단일 커밋도 가능
- `fix(ops): recover local_trusted paperclip sync and docs`

하지만 추천은 위의 2커밋 분리다.
- 이유: 코드 회귀 추적이 쉬움
- 이유: 문서만 cherry-pick 하거나 되돌리기 쉬움

## 실제 검증 결과
- `pytest -o addopts='' -q ...` → `13 passed`
- `bash -n run_full_funnel_operational.sh` → 통과
- 운영 문서 재스캔 결과
  - PAPERCLIP_API_KEY 별표 예시 없음
  - paperclip_sync=skipped_missing_api_key 없음
  - PAPERCLIP_API_KEY missing 문구 없음
  - 모두 문서에서 제거됨
