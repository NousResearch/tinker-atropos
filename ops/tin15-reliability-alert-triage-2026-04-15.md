# TIN-15 신뢰성 경고 정리

작성일: 2026-04-15
기준 실행: `python3 ops/run_full_funnel_status.py`

## 현재 상태
- 전체 run_count: 55
- 현재 alert_count: 11
- 최신 정상 실행
  - `reliability-smoke-20260415-085832`
- 최신 final 경로
  - `/Users/heomin/.hermes/hermes-agent/tinker-atropos/outputs/2026-04-15/reliability-smoke-20260415-085832/summary/sample_research_strategy-final-20260415-085832.json`

## 경고 목록
### 묶음 하나. 구형 요약 폴더에서 final 과 one-line 둘 다 없음
- ordinarybiz-opsummary
- ordinarybiz-report
- ordinarybiz-summary
- ordinarybiz-summary2
- ordinarybiz-quality2
- ordinarybiz-quality3
- ordinarybiz-quality4
- ordinarybiz-quality5

의미
- 초기 또는 중간 실험 시점에서 summary 체계가 아직 완전하지 않았던 흔적
- 현재 카드 닫힘을 막는 주된 이유

권장 처리
1. 이 경로들을 역사적 구형 산출물로 인정할지 결정
2. 인정하면 `full_funnel_status.py` 에 예외 규칙 또는 기준 날짜 도입
3. 인정하지 않으면 해당 프로젝트를 재생성하거나 최소 placeholder 산출물을 채움

### 묶음 둘. final 은 있는데 one-line 만 없음
- ordinarybiz-quality6
- ordinarybiz-quality7
- ordinarybiz-quality8

의미
- final 단계까지는 갔지만 one-line 산출물이 늦게 도입된 시기 흔적

권장 처리
1. 가장 쉬운 해결은 one-line 재생성
2. 또는 historical exemption 규칙으로 처리

### 묶음 셋. final 확장자 이상 흔적
- ordinarybiz-quality6
- ordinarybiz-quality7
- ordinarybiz-quality8

관찰
- 최신 final 이 `.json` 이 아니라 `.md` 로 남아 있다.

의미
- exporter 출력 규칙이 중간에 바뀐 흔적
- 현재 run 자체는 정상이어도 역사 데이터가 최신 규칙과 불일치

권장 처리
1. historical run 은 확장자 예외 허용 여부 판단
2. 아니면 해당 final json 재생성

## 우선순위 제안
### 빠른 닫힘 우선안
- quality6, quality7, quality8 의 one-line 3개만 먼저 보강
- 나머지 8개는 historical exemption 규칙으로 처리

### 엄격 정리안
- 11개 전부에 대해 final / one-line 재생성 또는 placeholder 채움
- 가장 증거 밀도는 높지만 시간이 많이 듦

## 내 권장안
현재 최신 일일 실행은 정상이라서, 운영 관점에서는 아래가 가장 효율적이다.
1. `ordinarybiz-quality6/7/8` 의 one-line 누락만 보강
2. `opsummary`, `report`, `summary`, `summary2`, `quality2~5` 는 historical exemption 규칙 추가
3. 그 후 `TIN-15` 재판정

## 닫힘 재판정 조건
- alert_count 가 0 이 되어야 함
- 또는 historical exemption 이 반영된 뒤 실제 경고 기준에서 0 이어야 함
- 최신 점검 코멘트가 카드에 남아 있어야 함
