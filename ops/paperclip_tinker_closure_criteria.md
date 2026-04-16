# Tinker Atropos Ops 카드 닫힘 기준

작성일: 2026-04-15

## 목적
`Tinker Atropos Ops` 회사의 일일 루틴 카드가 `issue_created` 에서 멈추지 않고, 어떤 조건에서 `done` 으로 닫히고 어떤 조건에서 `todo` 로 유지되는지 명확히 고정한다.

## 공통 원칙
- Paperclip은 관제 보드다.
- 실제 점검은 외부 저장소에서 수행한다.
- 카드 상태는 산출물과 점검 결과로만 판정한다.
- 코멘트 없는 닫힘 금지.
- 상태 변경 전에 반드시 요약 코멘트를 남긴다.

## TIN-15 Daily Full Funnel Reliability Check

### done 조건
아래를 모두 만족할 때만 닫는다.
1. `run_count > 0`
2. `alert_count == 0`
3. `latest_run.latest_final` 이 실제로 존재한다.
4. 최신 점검 코멘트가 카드에 기록된다.

### todo 유지 조건
아래 중 하나라도 참이면 열린 상태로 둔다.
- `run_count == 0`
- `alert_count > 0`
- `best`, `final`, `report`, `one-line` 중 누락이 있다.
- 최신 실행 증거 경로가 비어 있다.

### 해석 메모
- 오래된 summary 폴더 누락도 운영 경고로 본다.
- 즉 최신 실행 하나만 멀쩡해도 전체 경고가 남아 있으면 닫지 않는다.

## TIN-16 Daily Preset Performance Snapshot

### done 조건
아래를 모두 만족할 때만 닫는다.
1. `preset_count > 0`
2. `totals.final_runs > 0`
3. 최고 headline 과 평균 점수 요약 코멘트가 카드에 기록된다.

### todo 유지 조건
아래 중 하나라도 참이면 열린 상태로 둔다.
- `preset_count == 0`
- `totals.final_runs == 0`
- 카드 코멘트가 없다.

### 해석 메모
- 이 카드는 경고 개수보다 `요약 결과가 실제로 생성되었는지` 가 핵심이다.
- 데이터는 있는데 코멘트와 상태 마감이 없으면 미완료다.

## 루틴 상태 해석
- `completed`
  - 카드와 루틴 모두 닫힌 정상 흐름
- `issue_created`
  - 스케줄은 돌았지만 후속 점검 또는 마감 루프가 끝나지 않음
- `never_run`
  - 아직 기준 데이터 없음

## 최신 루틴 카드 매핑 규칙
- routine 이 만든 실행 카드는 같은 제목으로 식별자 번호가 계속 올라갈 수 있다.
- 따라서 동기화 스크립트는 예전 고정 식별자만 믿으면 안 된다.
- 우선순위는 아래처럼 둔다.
  1. 같은 제목의 최신 열린 카드
  2. 없으면 같은 제목의 최신 카드
  3. 그래도 없으면 예전 고정 식별자 fallback

### 현재 확인된 사례
- `Daily Full Funnel Reliability Check`
  - 예전 기준 식별자: `TIN-15`
  - 최신 routine 카드: `TIN-20`
- `Daily Preset Performance Snapshot`
  - 예전 기준 식별자: `TIN-16`
  - 최신 routine 카드: `TIN-22`

### 운영 해석
- 번호가 바뀌어도 제목과 루틴 의미가 같으면 최신 routine 카드를 닫아야 한다.
- 그렇지 않으면 점검은 끝났는데 최신 card 가 `blocked` 또는 `todo` 로 남는 누락이 생긴다.

## 구현 기준
현재 구현 함수
- `ops.tinker_paperclip_sync.determine_full_funnel_issue_status`
- `ops.tinker_paperclip_sync.determine_preset_issue_status`

현재 동기화 스크립트 초안
- `ops/paperclip_tinker_atropos_sync.py`
- 루프백 `local_trusted` 보드에서는 무인증으로 실행 가능
- 인증 모드 또는 원격 보드에서는 `PAPERCLIP_API_KEY` 필요

## 운영 권장 순서
1. 외부 저장소에서 상태 점검 실행
2. 요약 텍스트 생성
3. 카드 코멘트 기록
4. 기준에 따라 `done` 또는 `todo` 갱신
5. 다음 루틴이 중복 코멘트를 남기지 않도록 필요 시 개선
