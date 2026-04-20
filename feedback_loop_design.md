# 운영 결과 → 학습 데이터 피드백 루프 설계

## 목적
실제 운영에서 나온 결과를 다시 Tinker-Atropos 학습 재료로 되먹여 민 전용 Hermes 품질을 계속 올린다.

## 입력 소스
- summary/final.md
- summary/one-line.txt
- 실제 발행된 X 문안
- 실제 랜딩 수정안
- 유지 운영 메시지
- 결과 지표 메모

## 저장할 것
- 어떤 variant를 실제 선택했는가
- 실제로 수정한 부분은 무엇인가
- 클릭률/전환율/응답률이 어땠는가
- 왜 다른 후보보다 이 안을 썼는가

## 추천 구조
feedback/
- YYYY-MM-DD/
  - project/
    - selected_variant.json
    - metrics.md
    - lessons.md

## 최소 기록 포맷
selected_variant.json
- preset
- chosen_business_rank
- chosen_x_rank
- chosen_landing_rank
- chosen_retention_rank
- final_edits

metrics.md
- X 클릭/댓글/공유
- 랜딩 클릭/상담/전환
- retention 체크인/재방문

lessons.md
- 무엇이 먹혔는가
- 무엇이 덜 먹혔는가
- 다음 번 자동 생성에서 강화할 포인트

## 다음 자동화 아이디어
1. feedback 폴더를 읽어 score 보정 힌트 생성
2. 반복적으로 선택된 표현을 preset 강화 규칙으로 승격
3. 낮은 성과 표현은 감점 규칙 후보로 분류
