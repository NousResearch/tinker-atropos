# Paperclip 인증 모드 운영 기준

## 목적
Tinker Atropos 운영 스크립트가 Paperclip 에 붙을 때 언제 인증키가 필요하고, 언제 로컬 무인증이 허용되는지 한 장으로 정리한다.

## 기본 원칙
- 먼저 `PAPERCLIP_API_KEY` 가 있으면 그 값을 사용한다.
- 키가 없으면 대상 주소가 루프백인지 확인한다.
- 루프백 주소면 `/api/health` 에서 `deploymentMode` 를 읽는다.
- `deploymentMode=local_trusted` 일 때만 무인증 요청을 허용한다.
- 그 외에는 인증이 필요하다.

## 허용되는 무인증 경로
다음 조건을 모두 만족할 때만 무인증 허용
- 주소가 `http://127.0.0.1:3100` 또는 `localhost` 계열
- `/api/health` 응답에 `deploymentMode=local_trusted`
- 작업 목적이 로컬 보드 수준 읽기 또는 상태 갱신

예
- `ops/paperclip_tinker_atropos_sync.py`
- `ops/hide_patch_sync_verification_cards.py`
- `ops/sync_result_to_paperclip.py` 를 경유하는 로컬 운영 스크립트

## 반드시 인증이 필요한 경우
- 원격 주소
- 루프백이 아닌 주소
- `deploymentMode=authenticated`
- 에이전트 귀속 행동을 증명해야 하는 경우
- 로컬 보드가 아니라 특정 에이전트 권한으로 기록해야 하는 경우

## 현재 구현 경로
### 파이썬 공통 경로
- `ops/paperclip_curl.py`
- 동작
  - `build_curl_command(...)` 가 먼저 `PAPERCLIP_API_KEY` 를 확인
  - 키가 없으면 `is_local_trusted_mode(url)` 검사
  - 조건 충족 시 인증 헤더 없이 `curl` 수행
  - 조건 미충족 시 예외 발생

### 운영 셸 래퍼
- `run_full_funnel_operational.sh`
- 동작
  - `PAPERCLIP_API_URL` 또는 기본값 `http://127.0.0.1:3100` 사용
  - 키가 있거나 로컬 `local_trusted` 면 Paperclip 동기화 실행
  - 아니면 `paperclip auth required` 로 스킵 결과 저장

## 스캔 결과 요약
2026-04-16 기준 운영 스크립트 전수 스캔 결과
- 별도 `PAPERCLIP_API_KEY` 하드 게이트가 남아 있던 셸 래퍼는 `run_full_funnel_operational.sh` 하나였고 이미 수정됨
- 나머지 파이썬 운영 스크립트는 `ops/sync_result_to_paperclip.py` 또는 `ops/paperclip_curl.py` 를 통해 공통 규칙을 사용함

해당 스크립트 예
- `ops/run_review_queue.py`
- `ops/run_preset_scoreboard.py`
- `ops/run_full_funnel_status.py`
- `ops/run_environment_status.py`
- `ops/run_weekly_tinker_summary.py`
- `ops/run_task.py`

## 점검 순서
문제가 생기면 아래 순서로 확인
1. `curl -sS http://127.0.0.1:3100/api/health`
2. `deploymentMode` 가 `local_trusted` 인지 확인
3. 호출 주소가 루프백인지 확인
4. 여전히 실패하면 `PAPERCLIP_API_KEY` 를 넣고 재현
5. 에이전트 귀속 액션이 필요한 작업인지 구분

## 권장 규칙
- 로컬 개발과 운영 복구는 가능하면 공통 경로 `ops/paperclip_curl.py` 를 사용
- 새 운영 스크립트는 직접 `curl` 하지 말고 공통 경로를 재사용
- 셸 래퍼에서 인증 분기가 필요하면 파이썬 쪽과 같은 기준을 쓴다
- 문서에는 로컬 `local_trusted` 예외를 반드시 적고, 원격/인증 모드 예외도 같이 적는다
