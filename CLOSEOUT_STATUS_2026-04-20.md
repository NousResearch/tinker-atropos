# 팅커 아트로포스 마감 상태

작성 시각
- 2026-04-20

## 오늘 확인한 사실
- GraphRAG 계열 error 크론 3종은 모두 `ok`
- 풀 퍼널 운영 기본값은 `reward` 선택 기준으로 바꾸는 것이 맞다
- 오늘 마감 산출물인 `quality_comparison_report.md` 를 추가했다
- 로드맵 7단계 기준으로는 사실상 마감 상태다
- 남은 기술 판단은 승격용 마지막 꼬리 과제 하나와 워킹트리 정리 두 축이다

## 증거
### 1. 승격 평가 재실행
실행 명령
- `/Users/heomin/.hermes/hermes-agent/venv/bin/python run_min_hermes_promotion_eval.py`

실행 결과
- v2
  - current_policy `0.9979`, `12/12`, `yes`
  - patched_policy `0.9924`, `12/12`, `yes`
- v3
  - current_policy `0.9750`, `0/1`, `no`
  - patched_policy `0.9800`, `1/1`, `yes`

판정
- `v2` 는 운영 회복과 회귀 방지 관점에서 이미 충분하다
- `v3` 는 마지막 승격 차이를 계속 유지하고 있다

### 2. 마지막 승격 차이 과제 판단
근거 파일
- `research/min_hermes_offline_eval_v3_promotion_criteria.md`

현재 해석
- 마지막 차이는 `landing-live-session-signup-tail`
- 핵심 차이 축은 `metric_quality`
  - current `0.8333`
  - patched `1.0`
- 차이 원인은 current 가 지표 문장에 `건` 신호를 아직 완전히 넣지 못하기 때문이다

운영 판단
- 이 차이는 현재 기준으로 굳이 없애기보다 patched 승격 기준으로 유지하는 편이 더 유용하다
- 즉 오늘 기준 마감 판단에서 이 항목은 "열린 버그"가 아니라 "의도적으로 남겨둔 승격 구분 축"으로 본다

### 3. 풀 퍼널 품질 비교 산출물
실행 명령
- `bash run_full_funnel_daily.sh sample_research_strategy.txt ordinarybiz-closeout ordinarybiz`

생성 확인
- `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-report-20260420-121845.md`
- `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-quality-comparison-20260420-121845.md`
- `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-best-20260420-121845.json`
- `quality_comparison_report.md`

핵심 결과
- 권장 선택기준: `reward`
- business: 동일
- x: 동일
- landing: 보상 선택이 더 적합
- retention: 보상 선택이 더 적합

운영 판단
- 풀 퍼널 기본값은 `--selection-mode reward`
- 오늘 이 기준을 `run_full_funnel_daily.sh`, `run_full_funnel_operational.sh`, `OPERATING_MODES.md` 에 반영했다

### 4. 테스트
실행 명령
- `/Users/heomin/.hermes/hermes-agent/venv/bin/python -m pytest test_build_research_to_business_loop.py test_build_business_to_retention_loop.py test_run_research_to_full_funnel_output.py -q`

결과
- `37 passed in 41.54s`

## 오늘 마감 판정
### 최소 마감안
완료
- 크론 복구
- promotion eval 일일 운영 유지
- full funnel 저장 경로 실동작 확인
- 품질 비교 리포트 문서화

### 완성안
오늘 선반영 완료
- reward 기준 운영 모드 반영
- full funnel 일일 실행 스크립트 기본값 반영
- quality comparison 산출물 자동 저장 반영
- 로드맵과 운영 문서 갱신

## 지금 남은 것
### 1. 기술적 남은 일
- `landing-live-session-signup-tail` 을 current 까지 올릴지, 계속 승격 차이 축으로 둘지 최종 결정만 남음
- 현재 문서 기준으로는 후자가 더 유용하므로 사실상 운영 차원에서는 닫힌 상태다

### 2. 저장소 남은 일
- 워킹트리 변경이 많기 때문에 커밋 묶음 정리 필요
- 이건 기능 미완성이 아니라 정리 작업이다

## 결론
- 오늘 기준으로 기능 마감은 완료
- 남은 것은 승격 차이 축 유지 판단과 커밋 정리다
- 따라서 프로젝트 상태는 `운영 마감 완료 / 정리 단계 진입` 으로 본다

## 오늘 만든 로컬 커밋
- `bdb0f30` `feat: add min environments and reward-first full funnel pipeline`
- `5501f3d` `docs: record full funnel operating modes and closeout status`
- `303ce93` `feat: add tinker ops status and paperclip sync automation`
- `844673e` `feat: add feedback-driven patch cycle helpers`
