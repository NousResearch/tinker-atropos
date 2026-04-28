# 2026-04-16 local_trusted 동기화 복구 기록

## 문제
- `paperclipai auth login` 을 전역 명령처럼 실행했지만 `zsh: command not found: paperclipai` 발생
- 티커 운영 동기화는 `PAPERCLIP_API_KEY` 부재로 보류 상태였음

## 확인한 사실
- Paperclip CLI 전역 설치가 아니라 저장소 루트 스크립트로 실행하는 구조
- 근거
  - `cli/package.json` → `bin.paperclipai = ./dist/index.js`
  - 루트 `package.json` → `scripts.paperclipai = node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts`
- 현재 로컬 서버는 `local_trusted` 모드
  - 확인 명령: `curl -sS http://127.0.0.1:3100/api/health`
  - 핵심 응답: `"deploymentMode":"local_trusted"`
- 서버 인증 미들웨어는 `local_trusted` 에서 기본 actor 를 `local-board` 로 시작
  - 근거 파일: `server/src/middleware/auth.ts`

## 실행 경로
### CLI 확인
```bash
cd /Users/heomin/Projects/paperclip
pnpm paperclipai auth --help
```

정상 출력 확인.

### 실제 동기화
처음에는 안전하게 PAPERCLIP_API_KEY 값을 넣어 실행해 성공 확인 후,
이후 코드 수정 뒤에는 환경 변수 없이 재실행해서도 성공 확인.

```bash
unset PAPERCLIP_API_KEY
python3 /Users/heomin/.hermes/hermes-agent/tinker-atropos/ops/paperclip_tinker_atropos_sync.py \
  --root /Users/heomin/.hermes/hermes-agent/tinker-atropos
```

## 코드 변경
### 파일
- `ops/paperclip_curl.py`
- `test_sync_result_to_paperclip.py`
- `ops/README.md`
- `ops/paperclip_tinker_closure_criteria.md`

### 핵심 변경
- `build_curl_command(...)` 가 먼저 `PAPERCLIP_API_KEY` 를 사용
- 키가 없으면 루프백 주소인지 확인
- 루프백 주소면 `/api/health` 로 `deploymentMode=local_trusted` 확인
- 이 경우 인증 헤더 없이 curl 허용
- 원격 주소나 인증 모드면 기존대로 예외 발생

## 테스트
```bash
pytest -o addopts='' -q \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/test_sync_result_to_paperclip.py \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/test_tinker_paperclip_sync.py
```

결과
- `9 passed in 0.03s`

## 실동기화 결과
동기화 실행 결과
- `TIN-18` → `done`
- `TIN-15` → `done`
- `TIN-16` → `done`

검증 결과
- 각 카드 상태 `done`
- 동기화 코멘트 존재 확인
- 작성자 `authorUserId = local-board`
- `authorAgentId = null`

### 코멘트 수 검증
- `TIN-18` sync comment count: `3`
- `TIN-15` sync comment count: `2`
- `TIN-16` sync comment count: `2`

## 운영 규칙
- 로컬 루프백 `http://127.0.0.1:3100` 또는 `localhost` 에서 `deploymentMode=local_trusted` 이면 외부 보드 자동화 스크립트는 무인증 허용 가능
- 에이전트 귀속 액션이 필요하거나 원격/인증 모드 서버면 반드시 `PAPERCLIP_API_KEY` 사용
- 전역 `paperclipai` 가 없으면 저장소 루트에서 `pnpm paperclipai ...` 로 실행
