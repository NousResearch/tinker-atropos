# 민 전용 Hermes 운영 모드

## 1. 조사 모드
입력
- 조사 메모
- 경쟁사 비교 메모
- 가설과 다음행동 초안

사용 스크립트
- build_research_to_business_loop.py

목적
- 조사 초안을 전략 초안으로 압축

샘플 명령어
- `python build_research_to_business_loop.py sample_research_strategy.txt`
- `python build_research_to_business_loop.py sample_research_strategy.txt --json`
- `python build_research_to_business_loop.py sample_research_strategy.txt --save`

## 2. 전략 모드
입력
- 사업 상황 초안

사용 환경
- min_business_strategy

목적
- 문제, 고객, 제안, 채널, 실험, 지표 정리

샘플 명령어
- `python build_business_to_x_loop.py sample_business_strategy.txt`
- `python build_business_to_landing_loop.py sample_business_strategy.txt`
- `python build_business_to_retention_loop.py sample_business_strategy.txt`

## 3. 엑스 실행 모드
입력
- 전략 초안

사용 스크립트
- build_business_to_x_loop.py

목적
- X 초안 3종 생성
- 후크/댓글/행동 점수화

샘플 명령어
- `python build_business_to_x_loop.py sample_business_strategy.txt`
- `python build_business_to_x_loop.py sample_business_strategy.txt --json`
- `python build_business_to_x_loop.py sample_business_strategy.txt --save`

## 4. 랜딩 전환 모드
입력
- 전략 초안

사용 스크립트
- build_business_to_landing_loop.py

목적
- 헤드라인, 서브카피, CTA, 실험안 생성

샘플 명령어
- `python build_business_to_landing_loop.py sample_business_strategy.txt`
- `python build_business_to_landing_loop.py sample_business_strategy.txt --json`
- `python build_business_to_landing_loop.py sample_business_strategy.txt --save`

## 5. 유지 운영 모드
입력
- 전략 초안

사용 스크립트
- build_business_to_retention_loop.py

목적
- 체크인 메시지, 첫 주 미션, 재참여 장치 생성

샘플 명령어
- `python build_business_to_retention_loop.py sample_business_strategy.txt`
- `python build_business_to_retention_loop.py sample_business_strategy.txt --json`
- `python build_business_to_retention_loop.py sample_business_strategy.txt --save`

## 6. 조사 → 전략 → 엑스 모드
사용 스크립트
- run_research_to_business_to_x.py

목적
- 조사에서 전략, 전략에서 X 실행 초안까지 한 번에 생성

샘플 명령어
- `python run_research_to_business_to_x.py sample_research_strategy.txt`
- `python run_research_to_business_to_x.py sample_research_strategy.txt --json`
- `python run_research_to_business_to_x.py sample_research_strategy.txt --save --project ordinarybiz-x`

## 7. 조사 → 전략 → 랜딩 모드
사용 스크립트
- run_research_to_business_to_landing.py

목적
- 조사에서 전략, 전략에서 랜딩 전환 초안까지 한 번에 생성

샘플 명령어
- `python run_research_to_business_to_landing.py sample_research_strategy.txt`
- `python run_research_to_business_to_landing.py sample_research_strategy.txt --json`
- `python run_research_to_business_to_landing.py sample_research_strategy.txt --save --project ordinarybiz-landing`

## 8. 조사 → 전략 → 유지 모드
사용 스크립트
- run_research_to_business_to_retention.py

목적
- 조사에서 전략, 전략에서 유지 운영 초안까지 한 번에 생성

샘플 명령어
- `python run_research_to_business_to_retention.py sample_research_strategy.txt`
- `python run_research_to_business_to_retention.py sample_research_strategy.txt --json`
- `python run_research_to_business_to_retention.py sample_research_strategy.txt --save --project ordinarybiz-retention`

## 9. 풀 퍼널 모드
사용 스크립트
- run_research_to_full_funnel.py

목적
- 조사 초안 하나로 전략, X, 랜딩, 유지 초안까지 한 번에 생성
- 품질 우선 운영에서는 `--selection-mode reward` 를 기본으로 쓴다.

권장 사용 상황
- 새 아이디어를 퍼널 전체로 빠르게 펼치고 싶을 때
- 하루치 운영 후보를 한 번에 뽑고 싶을 때

샘플 명령어
- `python run_research_to_full_funnel.py sample_research_strategy.txt --selection-mode reward`
- `python run_research_to_full_funnel.py sample_research_strategy.txt --json --selection-mode reward`
- `python run_research_to_full_funnel.py sample_research_strategy.txt --save --selection-mode reward --project ordinarybiz-final`
- `python run_research_to_full_funnel.py sample_research_strategy.txt --save --all-business --selection-mode reward --project ordinarybiz-batch`

## 기본 권장 흐름
1. 조사 메모가 있으면 조사 모드 또는 풀 퍼널 모드
2. 전략만 다듬고 싶으면 전략 모드
3. 이미 전략이 있으면 X, 랜딩, 유지 모드 중 하나 선택
4. 프로젝트 단위 산출물 저장이 필요하면 `--save --project 프로젝트명` 사용
