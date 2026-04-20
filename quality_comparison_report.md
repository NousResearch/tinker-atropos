# 품질 비교 리포트

기준 실행
- 입력: `sample_research_strategy.txt`
- 프로젝트: `ordinarybiz-closeout`
- 실행 명령:
  - `bash run_full_funnel_daily.sh sample_research_strategy.txt ordinarybiz-closeout ordinarybiz`
- 실행 시각 기준 산출물
  - `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-report-20260420-121845.md`
  - `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-quality-comparison-20260420-121845.md`
  - `outputs/2026-04-20/ordinarybiz-closeout/summary/sample_research_strategy-best-20260420-121845.json`

## 결론
- 권장 선택기준은 `reward`
- business 와 x 는 생성기 기준과 보상 기준이 같았다.
- landing 과 retention 은 생성기 기준보다 보상 기준이 더 좋았다.
- 따라서 풀 퍼널 운영 기본값은 `--selection-mode reward` 로 고정하는 것이 맞다.

## 단계별 비교
- business
  - 생성기: rank 1 / variant 2 / generator 0.51 / reward 0.77
  - 보상: rank 1 / variant 2 / generator 0.51 / reward 0.77
  - 판정: 동일
- x
  - 생성기: rank 1 / variant 3 / generator 0.69 / reward 0.70
  - 보상: rank 1 / variant 3 / generator 0.69 / reward 0.70
  - 판정: 동일
- landing
  - 생성기: rank 1 / variant 3 / generator 0.55 / reward 0.65
  - 보상: rank 2 / variant 1 / generator 0.51 / reward 0.71
  - 판정: 보상 선택이 더 적합
- retention
  - 생성기: rank 1 / variant 3 / generator 0.51 / reward 0.34
  - 보상: rank 3 / variant 1 / generator 0.40 / reward 0.50
  - 판정: 보상 선택이 더 적합

## 해석
- 생성기 점수만 보면 랜딩과 유지는 겉으로 더 강해 보이는 문장이 먼저 올라온다.
- 하지만 실제 보상 기준으로 다시 보면 더 운영 친화적인 랜딩안과 유지안이 따로 있었다.
- 이 차이를 무시하면 일일 운영에서 보기 좋은 문장을 뽑고 실제 맞는 답을 놓칠 수 있다.

## 오늘 반영한 운영 수정
- `run_research_to_full_funnel.py`
  - 품질 비교 리포트 생성 기능 추가
  - 저장 시 summary 폴더에 `quality-comparison` 리포트도 같이 저장
  - reward 선택 모드에서도 실행 리포트가 실제 선택된 최고 안을 반영하도록 수정
- `run_full_funnel_daily.sh`
  - `--selection-mode reward` 기본 반영
- `run_full_funnel_operational.sh`
  - `--selection-mode reward` 기본 반영
- `OPERATING_MODES.md`
  - 풀 퍼널 모드 기본 예시를 reward 기준으로 갱신

## 현재 판정
- 오늘 끝낼 최소 마감안: 완료
- 이번 주 안에 닫는 완성안: 오늘 선반영 완료
- 이제 남은 것은 운영 품질 정리가 아니라
  - 마지막 승격 차이 과제 판단
  - 워킹트리와 커밋 묶음 정리
  두 가지다.
