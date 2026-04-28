# Full Funnel Automation Examples

## Daily shell run
```bash
/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_daily.sh \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/sample_research_strategy.txt \
  ordinarybiz-daily \
  ordinarybiz
```

## Operational shell run
```bash
/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/sample_research_strategy.txt \
  ordinarybiz-daily \
  ordinarybiz
```

- 로컬 `http://127.0.0.1:3100` 가 `local_trusted` 모드면 별도 `PAPERCLIP_API_KEY` 없이 Paperclip 동기화까지 진행된다.
- 원격 또는 인증 모드 서버에서는 기존대로 `PAPERCLIP_API_KEY` 를 넣는다.

## Bootcamp daily run
```bash
/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_daily.sh \
  /Users/heomin/.hermes/hermes-agent/tinker-atropos/sample_research_strategy.txt \
  bootcamp-daily \
  bootcamp
```

## Cron example
```cron
30 8 * * * /Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh /Users/heomin/.hermes/hermes-agent/tinker-atropos/sample_research_strategy.txt ordinarybiz-daily ordinarybiz >> /Users/heomin/.hermes/hermes-agent/tinker-atropos/cron_full_funnel.log 2>&1
```

## launchd ProgramArguments example
```json
[
  "/Users/heomin/.hermes/hermes-agent/tinker-atropos/run_full_funnel_operational.sh",
  "/Users/heomin/.hermes/hermes-agent/tinker-atropos/sample_research_strategy.txt",
  "ordinarybiz-daily",
  "ordinarybiz"
]
```

## Preset variants
- ordinarybiz
- bootcamp
- vip
- ailit
- youtube
- x-article

## Output location
- outputs/YYYY-MM-DD/PROJECT/business/
- outputs/YYYY-MM-DD/PROJECT/x/
- outputs/YYYY-MM-DD/PROJECT/landing/
- outputs/YYYY-MM-DD/PROJECT/retention/
- outputs/YYYY-MM-DD/PROJECT/summary/
- outputs/YYYY-MM-DD/PROJECT/ops/

## Suggested routine
1. research input 템플릿 복사
2. 조사 메모 입력
3. `run_full_funnel_operational.sh INPUT PROJECT PRESET` 실행
4. summary/one-line.txt 확인
5. publish_ready 산출물과 ops 로그 확인
6. Paperclip 코멘트와 상태 마감 확인
