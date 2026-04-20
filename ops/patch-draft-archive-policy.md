# Patch Draft Archive 운영 규칙

작성일: 2026-04-15

## 목적
활성 patch queue 와 과거 초안을 분리해서, 실제 후속 작업 후보만 review queue 에 남기고 나머지는 보관 상태로 관리한다.

## 기본 원칙
- 활성 queue 에는 실제 후속 판단이 필요한 patch 만 남긴다.
- 실행 가치가 없는 초안은 `feedback/patch_drafts/archived/` 아래로 이동한다.
- 보관은 삭제가 아니라 분리다.
- archived patch 는 필요 시 다시 꺼내 볼 수 있지만, 기본 운영에서는 활성 queue 계산에서 제외한다.

## 상태 의미
### 1. empty
의미
- patch 파일은 있지만 실제 `suggested_old/suggested_new` 또는 `weight_old/weight_new` 쌍이 없다.
- 즉 설명 주석만 있고 적용 가능한 엔트리가 없는 빈 초안이다.

처리
- `feedback/patch_drafts/archived/empty/` 로 이동한다.
- `pending_review_count` 에서 제외한다.

### 2. stale_partial
의미
- 일부 엔트리는 이미 현재 코드에 반영돼 있다.
- 남은 엔트리는 현재 코드에서 `old` 와 `new` 둘 다 없어져서, 실질적으로 낡은 제안이 됐다.
- 즉 숫자로는 부분 적용처럼 보이지만 실제 후속 작업 후보는 아니다.

처리
- `feedback/patch_drafts/archived/stale_partial/` 로 이동한다.
- `pending_review_count` 와 `top_review_candidate` 에서 제외한다.

### 3. superseded
의미
- 같은 대상 파일 묶음에 대해 더 최신 patch 가 이미 존재하거나,
- 그 대상 파일 묶음이 이미 `empty` 또는 `stale_partial` 로 archived 된 더 최신 patch 에 의해 덮였다.

처리
- `feedback/patch_drafts/archived/superseded/` 로 이동한다.
- review queue 계산 대상에서 제외한다.

## 현재 아카이브 폴더 구조
- `feedback/patch_drafts/archived/empty/`
- `feedback/patch_drafts/archived/stale_partial/`
- `feedback/patch_drafts/archived/superseded/`

## 운영 명령
### queue 요약만 보기
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python3 ops/run_review_queue.py --drafts-dir feedback/patch_drafts
```

### 비실행 초안 자동 보관
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python3 ops/run_review_queue.py --drafts-dir feedback/patch_drafts --archive-nonactionable
```

### 다른 보관 경로로 보내기
```bash
cd /Users/heomin/.hermes/hermes-agent/tinker-atropos
python3 ops/run_review_queue.py \
  --drafts-dir feedback/patch_drafts \
  --archive-nonactionable \
  --archive-dir /tmp/tinker-patch-archive
```

## 운영 해석 규칙
- `pending_review_count` 가 0 이어도 archived patch 가 존재할 수 있다.
- 이 경우 의미는 `활성 queue 는 비었고 과거 초안은 보관 상태다` 이다.
- 따라서 active queue 와 archive 규모를 혼동하지 않는다.

## archived patch 를 다시 볼 때
다음 조건 중 하나일 때만 archived patch 를 재검토한다.
- 현재 코드가 크게 바뀌어 예전 draft 를 다시 참고할 가치가 생김
- 특정 카피 규칙이나 점수 규칙의 변화 이력을 추적해야 함
- 회고 문서나 운영 규칙 문서에 근거 예시가 필요함

기본값은 재활성화가 아니라 참고 전용이다.

## 마감 기준
다음 네 가지가 맞으면 patch queue 운영은 마감 상태로 본다.
1. `run_review_queue.py` 결과의 `pending_review_count` 가 0 이다.
2. `top_review_candidate` 가 없다.
3. 비실행 초안이 archived 아래로 분리돼 있다.
4. active `feedback/patch_drafts/` 에는 실제 후속 작업 후보만 남는다.

## 주의
- archived 이동은 원본 삭제가 아니라 위치 변경이다.
- archived 상태만 보고 실제 코드 품질이 검증됐다고 해석하면 안 된다.
- code 적용 완료 판단은 여전히 테스트와 산출물 검증으로 닫아야 한다.
