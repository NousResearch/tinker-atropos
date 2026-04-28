# Feedback 기록 구조

목적
- 실제 운영에서 선택한 안과 성과를 다시 기록해
- 다음 score 보정과 preset 개선 힌트로 쓰기

권장 구조
- feedback/YYYY-MM-DD/project/
  - selected_variant.json
  - metrics.md
  - lessons.md

최소 기록 규칙
1. 실제로 선택한 business/x/landing/retention rank 기록
2. 실제 수정한 문장 기록
3. 결과 지표 기록
4. 다음 번 자동 생성에서 강화/감점할 포인트 기록

운영 루틴
1. 배포 직후 `python bootstrap_feedback_entry.py 프로젝트명 --preset 프리셋 --final-json 결과파일경로` 실행
2. 이미 폴더가 있더라도 다시 실행하면 `metrics.md` 만 새 구조로 갱신되고 `selected_variant.json`, `lessons.md` 는 보존된다.
3. 여러 프로젝트를 한 번에 채우려면 옵시디언 일괄 입력 시트를 먼저 채운다.
4. 아주 빠르게 빈칸만 보고 싶으면 `python print_feedback_missing_form.py --date YYYY-MM-DD` 로 missing-only 폼을 먼저 뽑는다.
5. 옵시디언 `실측 feedback 초간단 복붙 폼` 노트를 최신 빈칸 기준으로 맞추려면 `python refresh_feedback_missing_note.py --date YYYY-MM-DD` 를 실행한다.
6. `python apply_feedback_fill_sheet.py --date YYYY-MM-DD --sheet "시트경로.md"` 로 각 프로젝트 `metrics.md` 에 반영한다.
7. selected_variant.json 에 실제 선택 rank 와 수정 사항 입력
8. metrics.md 에 클릭률/전환율/체크인 수 같은 실측 수치를 입력
9. `python run_feedback_patch_cycle.py --date YYYY-MM-DD` 로 빈칸이 남았는지 먼저 확인
10. lessons.md 에 강화/감점 포인트 입력
11. 준비가 끝나면 `python run_feedback_patch_cycle.py --date YYYY-MM-DD --run` 으로 안전하게 자동화 체인 실행
12. 필요하면 `python extract_feedback_hints.py` 로 힌트를 단독 확인
13. 또는 `python generate_score_patch_draft.py` 와 `python generate_score_patch_v4a.py` 를 개별 실행해 다음 개선 초안 확인
