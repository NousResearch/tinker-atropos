# 2026-04-15 티커 페이퍼클립 외부 실행 정렬 점검

## 한줄 결론
티커 아트로포스 옵스 회사는 운영 보드와 루틴과 전용 화면까지 이미 갖췄다. 다만 공용 외부 래퍼 계층에는 아직 티커 회사 전용 프로필과 실행 흔적이 없고, 페이퍼클립 동기화도 인증된 컬 표준으로 통일되지 않았다.

## 옴엑스와 코덱스는 외부인가 내부인가
현재 설계 기준으로는 외부로 보는 것이 맞다.

근거
- `ops/README.md`
  - 페이퍼클립 안에서 무거운 코드 실행을 직접 돌리지 않고 외부 저장소에서 `rp-cli` 와 `codex` 와 테스트를 실행한 뒤 결과만 회사 카드로 동기화한다고 적혀 있다.
- `ops/hermes-standard-instruction.md`
  - 페이퍼클립은 관제와 승인과 실패 감시만 맡고 실제 코드 실행은 `/Users/heomin/.hermes/hermes-agent/tinker-atropos` 에서만 한다고 적혀 있다.
- `ops/external_execution.py`
  - 실제 실행 단계가 `codex exec` 로 만들어지고, 작업 경로 아래 `.omx` 와 `logs` 를 만든다.

정리
- 실제 저장소에서 `codex` 와 `omx` 를 돌리면 외부 실행이다.
- 페이퍼클립 관리 체크아웃 안에서 에이전트가 직접 돌리면 내부 실행이다.
- 지금 티커 운영 설계는 전자를 목표로 한다.

## 티커 회사용 공용 외부 프로필 초안
작성 파일
- `/Users/heomin/.hermes/scripts/paperclip-external-profiles.tinker-atropos-draft.json`

초안 핵심
- 회사 아이디: `162e6af8-809e-4d24-b270-213f5603cf7b`
- 모드: `control_board_with_external_execution`
- 기본 작업 경로: `/Users/heomin/.hermes/hermes-agent/tinker-atropos`
- 제안 scope
  - `tinker-atropos`
  - `tinker-ops`
  - `paperclip-ui`
  - `paperclip-root`
  - `luna-system`
  - `hermes-scripts`

주의
- 이 파일은 초안이다.
- 아직 공용 본파일 `paperclip-external-profiles.json` 에 병합하지 않았다.
- 제안된 회사 동기화 스크립트 경로는 아직 구현 전일 수 있다.

## 틴 열다섯 추적
이슈
- `TIN-15`
- 제목: `Daily Full Funnel Reliability Check`
- 상태: `todo`
- 우선순위: `high`
- 최근 갱신: `2026-04-14T00:33:40.570Z`

루틴 상태
- 루틴 마지막 상태: `issue_created`
- 연결 이슈가 아직 열려 있다.

코멘트 추적
- 코멘트 수: 2
- 최신 코멘트에는 아래가 적혀 있다.
  - full funnel 점검 결과 `run_count 53`
  - 경고 `11`
  - 최신 정상 실행은 `ordinarybiz-daily`
  - 오래된 summary 폴더들에서 `final` 또는 `one-line` 누락
  - 일부 `ordinarybiz-quality6/7/8` 에서 `final` 이 `.json` 이 아니라 `.md`
  - 기대 launchd 로그가 없고 로드된 작업도 확인되지 않음
  - 그래서 이슈를 닫지 않고 열어둠

산출물 근거
- `python3 ops/run_full_funnel_status.py` 결과에서 실제로 `alert_count: 11`
- 최신 정상 산출물
  - `/Users/heomin/.hermes/hermes-agent/tinker-atropos/outputs/2026-04-14/ordinarybiz-daily/summary/sample_research_strategy-final-20260414-083227.json`

판정
- 틴 열다섯은 방치가 아니라 의도적으로 열린 상태다.
- 이유는 오래된 summary 산출물 누락과 실행 로그 신뢰성 문제가 아직 남아 있기 때문이다.

## 틴 열여섯 추적
이슈
- `TIN-16`
- 제목: `Daily Preset Performance Snapshot`
- 상태: `todo`
- 우선순위: `medium`
- 최근 갱신: `2026-04-14T00:34:08.077Z`

루틴 상태
- 루틴 마지막 상태: `issue_created`
- 마지막 실행 이슈는 생성됐지만 완료로 넘어가지 않았다.

코멘트 추적
- 코멘트 수: `0`
- 즉 점수 스냅샷 자체를 읽고 결과를 카드에 써준 후속 실행이 아직 없다.

산출물 근거
- `python3 ops/run_preset_scoreboard.py` 는 지금도 정상 동작한다.
- 현재 결과
  - `preset_count: 5`
  - `final_runs: 47`
- 즉 데이터는 있는데 카드 마감 루프가 비어 있다.

보조 근거
- `Tinker Atropos Ops Coordinator` 마지막 하트비트
  - `2026-04-14T00:34:08.081Z`
- 현재 시각 기준으로 거의 하루 가까이 지나 있어, 이슈 생성 뒤 실제 처리 단계가 이어지지 않은 흔적이다.

판정
- 틴 열여섯은 근거 데이터 부족 때문이 아니라 후속 처리 미실행 때문에 열려 있다.
- 즉 루틴이 이슈를 만들기만 하고 코멘트와 상태 마감까지 닫지 못했다.

## 티커 저장소 경로와 공용 래퍼 경로의 동기화 차이

### 티커 저장소 안 경로
파일
- `ops/run_task.py`
- `ops/external_execution.py`
- `ops/sync_result_to_paperclip.py`

특징
- 작업 경로는 티커 저장소 기준이다.
- `.omx` 와 `logs` 를 저장소 안에 만든다.
- `codex exec` 기반 계획 생성과 실행이 들어 있다.
- 카드 동기화는 `patch_issue()` 로 바로 패치한다.
- 현재는 `urllib` 로 로컬 `http://127.0.0.1:3100` 를 직접 친다.
- 인증 헤더를 붙이지 않는다.

### 공용 외부 래퍼 경로
파일
- `~/.hermes/scripts/paperclip-external-runner.py`
- `~/.hermes/scripts/paperclip-external-profiles.json`
- `~/.hermes/scripts/paperclip-external-standard-check.py`

특징
- 프로필과 scope 기반으로 여러 회사를 공용 처리한다.
- 실행 기록을 `~/.hermes/scripts/external-runs/<profile>/...` 아래에 남긴다.
- rp 작업공간 전환, git 경계 감지, scope 강제, summary 기록이 있다.
- 현재도 `urllib` 로 로컬 `http://127.0.0.1:3100/api` 를 직접 친다.
- 여기 역시 인증 헤더를 붙이지 않는다.

### 핵심 차이
- 티커 저장소 경로는 프로젝트 안쪽 전용 실행 도구다.
- 공용 래퍼는 회사별 프로필과 scope 를 관리하는 상위 실행기다.
- 티커 회사는 아직 공용 프로필 본파일에 등록되지 않았다.
- 그래서 지금 티커는 저장소 안 도구는 있는데 공용 외부 래퍼 생태계에는 아직 완전히 편입되지 않은 상태다.

## 인증된 컬 표준과의 차이
현재 두 경로 모두 아래와 어긋난다.
- 페이퍼클립 호출은 인증된 컬 표준 사용
- 권장 형태는 `Authorization: Bearer <키값>` 헤더를 명시하는 컬

현재 문제
- 티커 저장소 동기화 경로도 비인증 `urllib`
- 공용 외부 래퍼 경로도 비인증 `urllib`

정리 방향
1. 공용 래퍼의 페이퍼클립 호출을 인증된 컬 표준으로 바꾼다.
2. 티커 저장소의 `ops/sync_result_to_paperclip.py` 도 같은 표준으로 맞춘다.
3. 둘 다 같은 인증 주입 방식과 에러 포맷을 쓰게 한다.
4. 최종적으로 티커 회사를 공용 프로필 본파일에 병합한다.

## 옴엑스 학습과 관리 에이전트에 대한 판단
판단
- 필요하다.
- 다만 처음부터 무거운 실행 에이전트보다는 `학습과 운영 기준을 관리하는 가벼운 코디네이터` 가 더 맞다.

이유
- 옴엑스는 민이 명시적으로 요청할 때만 써야 한다.
- 작업 방식이 일반 코덱스 흐름과 다르고 승인 규칙과 검증 규칙이 따로 있다.
- 실전에서 중요한 것은 실행 자체보다
  - 언제 옴엑스를 쓰는지
  - 어떤 모드를 고르는지
  - 결과를 어떻게 검증하는지
  - 기존 더티 상태와 이번 변경을 어떻게 구분하는지
  이다.

추천 형태
- 이름 예시: `옴엑스 운영 코디네이터`
- 역할
  - 옴엑스 사용 기준 관리
  - 학습 메모와 실험 로그 축적
  - 저장소별 안전 기본값 관리
  - 옴엑스 결과 검증 체크리스트 유지
  - 필요할 때만 실제 실행 카드 발행

즉
- 상시 구현 에이전트보다
- `언제 옴엑스를 써야 하는지와 어떻게 검증할지를 관리하는 운영 에이전트`
가 먼저 필요하다.

## 바로 다음 권장 순서
1. 공용 본파일에 티커 프로필 병합 전 검토
2. 티커 회사 전용 동기화 스크립트 초안 작성
3. 틴 열다섯과 틴 열여섯을 외부 실행 기준으로 닫을지 유지할지 판정 규칙 작성
4. 티커 저장소 경로와 공용 래퍼 경로를 인증된 컬 표준으로 통일
