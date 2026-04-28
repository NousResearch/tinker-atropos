# Tinker-Atropos 민 전용 Hermes 로드맵

## 현재 위치
검증 기준
- 2026-04-18 기준 오프라인 평가 재실행 완료
- current_policy 15/15, mean_total 1.0000
- patched_policy 15/15, mean_total 1.0000
- human_baseline 14/15, mean_total 0.8928

완주 및 운영 검증 환경
- min_business_strategy
- min_x_strategy
- min_landing_cro
- min_membership_retention
- min_agentic_research

실전 파이프라인
- research -> business (3종 생성 + 점수화 + 저장)
- business -> x (3종 생성 + 점수화 + 저장)
- business -> landing (3종 생성 + 점수화 + 저장)
- business -> retention (3종 생성 + 점수화 + 저장)
- research -> business -> x -> landing -> retention 전체 퍼널 저장

최근 수정 메모
- 랜딩 환경 metric_quality 상한 버그 수정
- 기존 식은 term 6개 기준 최대 0.9라 total 이 0.985에서 막혔음
- 현재는 full term coverage 시 metric_quality 1.0 도달 가능
- 오프라인 승격용 `min_hermes_offline_eval_v2` 생성 완료
- v2는 current와 patched 차이가 남아 있는 tail task 12개만 모은 promotion benchmark
- v2 current 생성 경로 보강 완료
- current는 v2에서 `12/12` 통과까지 회복됨
- 최신 v2 재실행 결과
  - current `mean_total 0.9979`, `12/12`, `lane_passed yes`
  - patched `mean_total 0.9924`, `12/12`, `lane_passed yes`
- v2가 다시 포화되어 promotion signal 이 약해졌기 때문에 단일 꼬리 과제용 `min_hermes_offline_eval_v3` 를 추가함
- 최신 v3 재실행 결과
  - current `mean_total 0.9750`, `0/1`, `lane_passed no`
  - patched `mean_total 0.9800`, `1/1`, `lane_passed yes`
- 남은 승격 기준은 `landing-live-session-signup-tail` 하나로 압축됨
  - current는 `metric_quality 0.8333`
  - patched는 `metric_quality 1.0`
  - 즉 지표 문장에 `건` 신호까지 완전하게 넣는지 여부가 마지막 promotion discriminator
- `run_min_hermes_promotion_eval.py` 추가 완료
  - 한 번 실행으로 `v2`와 `v3` 번들을 재생성하고 scoreboards를 갱신함
  - 요약 아티팩트는 `outputs/YYYY-MM-DD/promotion-eval/summary/` 아래 저장됨
- `quality_comparison_report.md` 를 오늘 마감 산출물로 추가한다.
- 풀 퍼널 운영 스크립트는 `--selection-mode reward` 를 기본으로 사용한다.

## 오늘 마감 기준
- 최소 마감안
  - GraphRAG 계열 error 크론 3종 복구 완료
  - promotion eval 일일 자동화와 Paperclip 동기화 유지 중
  - research -> business -> x -> landing -> retention 저장 경로 실동작 확인
  - `quality_comparison_report.md` 로 샘플 품질 비교를 문서화
- 완성안
  - `OPERATING_MODES.md` 에 reward 기준 운영 모드 반영
  - `run_full_funnel_daily.sh` 와 `run_full_funnel_operational.sh` 를 reward 기준으로 고정
  - 품질 비교 리포트를 outputs 요약에도 같이 저장

## 단계별 현재 판정
- 1단계 완주 환경 확대: 사실상 완료
  - business, x, landing, retention, research 환경 파일과 테스트가 모두 존재
- 2단계 business -> retention 변환기: 완료
  - `build_business_to_retention_loop.py`
- 3단계 샘플 품질 평가 루프: 오늘 마감으로 완료
  - `quality_comparison_report.md`
- 4단계 outputs 구조 정리: 완료
  - `outputs/YYYY-MM-DD/<project>/{business,x,landing,retention,summary}`
- 5단계 research -> strategy 연결기: 완료
  - `build_research_to_business_loop.py`
- 6단계 full funnel 연결: 완료
  - `run_research_to_full_funnel.py`
- 7단계 운영 모드 정의: 완료
  - `OPERATING_MODES.md`

## 이제 남는 것
- 오프라인 승격 마지막 차이 과제 `landing-live-session-signup-tail` 마감 여부 판단
- 대규모 워킹트리 정리와 커밋 묶음 정리

## 다음 7단계

### 1단계. retention 또는 landing 중 하나를 세 번째 완주 성공 환경으로 만들기
목표
- 현재 ultra smoke에서 step 진입만 되는 환경을 하나 더 완주 성공으로 올린다.

완료 기준
- trainer_success true
- final weights 확보
- loss / reward 로그 확보

결과물
- 세 번째 완주 성공 환경
- 안정화된 실행 로그

### 2단계. business -> retention 변환기 만들기
목표
- 전략 초안에서 유지 운영 초안을 자동 생성한다.

예상 출력
- 체크인 문구
- 첫 주 미션
- 재참여 메시지
- 지표

완료 기준
- 3종 초안 생성
- 점수화 / 정렬
- 파일 저장

결과물
- build_business_to_retention_loop.py

### 3단계. business / x 성공 환경으로 샘플 품질 평가 루프 만들기
목표
- 단순 성공 여부가 아니라 실제 산출물 품질을 비교한다.

평가 항목
- 전략 우선순위 명확성
- X 행동 유도 강도
- 초보자 친화성
- 허풍 억제

완료 기준
- 샘플 비교 리포트 생성
- 어떤 환경이 실제 운영에 더 도움 되는지 정리

결과물
- quality_comparison_report.md

### 4단계. outputs 폴더 구조를 실전형으로 정리
목표
- 생성물 관리를 쉽게 만든다.

권장 구조
- outputs/x/YYYY-MM-DD/
- outputs/landing/YYYY-MM-DD/
- outputs/retention/YYYY-MM-DD/

완료 기준
- 저장 경로 자동 분기
- 파일명 규칙 통일

결과물
- 날짜별 산출물 저장 체계

### 5단계. research -> strategy 연결기 만들기
목표
- 조사 결과를 전략 초안으로 연결한다.

완료 기준
- 조사 섹션 입력
- 전략 초안 자동 변환
- business 환경 기준과 잘 맞는지 확인

결과물
- build_research_to_business_loop.py

### 6단계. research -> strategy -> x -> landing -> retention 파이프라인 연결
목표
- 개별 변환기를 하나의 운영 루프로 묶는다.

완료 기준
- 한 입력에서 여러 산출물 생성
- 단계별 저장
- 최소한의 실행 스크립트 확보

결과물
- end_to_end_content_ops_pipeline.py 또는 shell runner

### 7단계. 민 전용 Hermes 운영 모드 정의
목표
- 언제 어떤 루프를 쓸지 명확히 정한다.

예시 모드
- 전략 모드
- X 실행 모드
- 랜딩 전환 모드
- 유지 운영 모드
- 풀 퍼널 모드

완료 기준
- 사용 규칙 문서화
- 샘플 명령어 정리

결과물
- OPERATING_MODES.md

## 가장 가까운 실전 결과물
1. 전략 초안 1개 -> X 초안 3개 + 점수 + 저장
2. 전략 초안 1개 -> 랜딩 초안 3개 + 점수 + 저장
3. 다음: 전략 초안 1개 -> 유지 초안 3개 + 점수 + 저장

## 최종적으로 얻게 될 것
- 민 전용 전략 생성기
- 민 전용 X 실행 생성기
- 민 전용 랜딩 생성기
- 민 전용 유지 운영 생성기
- 조사에서 전략, 전략에서 실행으로 이어지는 운영형 Hermes
