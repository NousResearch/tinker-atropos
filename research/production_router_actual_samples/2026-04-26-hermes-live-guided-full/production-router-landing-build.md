---
task_id: production-router-landing-build
title: 웹사이트 제작 요청 라우팅
lane: actual_hermes_live_guided_full
created_at: 2026-04-26T09:37:54+10:00
source: hermes chat -q
---

# 웹사이트 제작 요청 라우팅

## 요청

새 랜딩페이지를 만들고 싶다. 피그마 시안, 디자인 엠디, 지피티 이미지 투 이미지, 코덱스 씨엘아이 구현, 브라우저 검증까지 연결해줘.

## 실행 지시

```text
너는 민의 헤르메스 제작 라우터다. 아래 요청에 대해 계획만 말하지 말고, 선행 도구, 실행 표면, 산출물, 검증, 기록까지 닫는 답변을 작성하라.

과제: 웹사이트 제작 요청 라우팅
요청: 새 랜딩페이지를 만들고 싶다. 피그마 시안, 디자인 엠디, 지피티 이미지 투 이미지, 코덱스 씨엘아이 구현, 브라우저 검증까지 연결해줘.
반드시 넣을 말: 알피 씨엘아이, DESIGN.md, figma-use, 코덱스 씨엘아이, 브라우저 검증, 빌드
작업분류에 넣을 말: 웹사이트, 랜딩, 코드, 피그마
선행경로에 넣을 말: 알피 씨엘아이, DESIGN.md, figma-use, 피그마, 디자인 문맥
실행표면에 넣을 말: 헤르메스, 코덱스 씨엘아이, 구현, 지피티 이미지 투, openai-codex-gpt-image-2-workflow
산출물에 넣을 말: 변경 파일, 이미지 파일, 프롬프트, 스크린샷, 드리프트
검증에 넣을 말: 빌드, 테스트, 브라우저 검증, 파일 존재, 완료 보고
기록에 넣을 말: 옵시디언, 티커 아트로포스, 평가 세트, 실패 패턴, 성공 규칙

아래 형식을 정확히 지켜라.
작업분류:
선행경로:
실행표면:
산출물:
검증:
기록:
```

## 답변

╭──────────── Hermes Agent v0.11.0 (2026.4.23) · upstream 283c8fd6 ────────────╮
│                                   Available Tools                            │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⣀⣀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   browser: browser_back, browser_click, ...  │
│  ⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣇⠸⣿⣿⠇⣸⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀   browser-cdp: browser_cdp, browser_dialog   │
│  ⠀⢀⣠⣴⣶⠿⠋⣩⡿⣿⡿⠻⣿⡇⢠⡄⢸⣿⠟⢿⣿⢿⣍⠙⠿⣶⣦⣄⡀⠀   clarify: clarify                           │
│  ⠀⠀⠉⠉⠁⠶⠟⠋⠀⠉⠀⢀⣈⣁⡈⢁⣈⣁⡀⠀⠉⠀⠙⠻⠶⠈⠉⠉⠀⠀   code_execution: execute_code               │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡿⠛⢁⡈⠛⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   cronjob: cronjob                           │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣦⣤⣈⠁⢠⣴⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   delegation: delegate_task                  │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠻⢿⣿⣦⡉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   discord: discord_server                    │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣦⣈⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   file: patch, read_file, search_files,      │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⠦⠈⠙⠿⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   write_file                                 │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣤⡈⠁⢤⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   (and 15 more toolsets...)                  │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                                              │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠑⢶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   MCP Servers                                │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⢰⡆⠈⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   qmd (stdio) — 8 tool(s)                    │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠈⣡⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                                              │
│  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   Available Skills                           │
│                                   apple: apple-notes, apple-reminders,       │
│      gpt-5.5 · Nous Research      findmy, imessage                           │
│           /Users/heomin           autonomous-ai-agents: claude-code, codex,  │
│  Session: 20260426_093712_4fe089  hermes-agent, hermes-contex...             │
│                                   baoyu: baoyu-format-markdown,              │
│                                   baoyu-imagine, baoyu-inf...                │
│                                   content-strategy:                          │
│                                   landing-page-proof-hardening, minto,       │
│                                   youtube-co...                              │
│                                   creative: architecture-diagram,            │
│                                   ascii-art, ascii-video, b...               │
│                                   data-science: jupyter-live-kernel          │
│                                   devops: ai-toolkit-tool-folder-ops,        │
│                                   ailit-ultra-core-bu...                     │
│                                   dogfood: hermes-agent-setup                │
│                                   email: himalaya                            │
│                                   gaming: minecraft-modpack-server,          │
│                                   pokemon-player                             │
│                                   general: cron-error-review, dogfood,       │
│                                   life-os, prism-3way...                     │
│                                   github: codebase-inspection, github-auth,  │
│                                   github-code-r...                           │
│                                   infranodus: actionize,                     │
│                                   embodied-navigation, infranodus, llm...    │
│                                   leisure: find-nearby                       │
│                                   mcp: figma-code-connect,                   │
│                                   figma-create-design-system-...             │
│                                   media: gif-search, heartmula, songsee,     │
│                                   spotify, video-...                         │
│                                   mlops: audiocraft-audio-generation,        │
│                                   axolotl, clip, dsp...                      │
│                                   note-taking:                               │
│                                   bootcamp-learning-note-search-hub,         │
│                                   github-relea...                            │
│                                   openclaw-imports: ab-test-setup,           │
│                                   ad-creative, agent-reach, agenta...        │
│                                   productivity: google-workspace,            │
│                                   google-workspace-briefing-ops...           │
│                                   red-teaming: godmode                       │
│                                   research: arxiv, github-trending-scout,    │
│                                   last30days, ml-pa...                       │
│                                   smart-home: openhue                        │
│                                   social-media:                              │
│                                   x-account-obsidian-marketing-monitor,      │
│                                   x-article...                               │
│                                   software-development: code-review,         │
│                                   cross-codebase-analysis, nextjs-br...      │
│                                                                              │
│                                   49 tools · 336 skills · 1 MCP servers ·    │
│                                   /help for commands                         │
│                                   ⚠ 49 commits behind — run hermes update    │
│                                   to update                                  │
╰──────────────────────────────────────────────────────────────────────────────╯

Query: 너는 민의 헤르메스 제작 라우터다. 아래 요청에 대해 계획만 말하지 말고, 
선행 도구, 실행 표면, 산출물, 검증, 기록까지 닫는 답변을 작성하라.

과제: 웹사이트 제작 요청 라우팅
요청: 새 랜딩페이지를 만들고 싶다. 피그마 시안, 디자인 엠디, 지피티 이미지 투 
이미지, 코덱스 씨엘아이 구현, 브라우저 검증까지 연결해줘.
반드시 넣을 말: 알피 씨엘아이, DESIGN.md, figma-use, 코덱스 씨엘아이, 브라우저 
검증, 빌드
작업분류에 넣을 말: 웹사이트, 랜딩, 코드, 피그마
선행경로에 넣을 말: 알피 씨엘아이, DESIGN.md, figma-use, 피그마, 디자인 문맥
실행표면에 넣을 말: 헤르메스, 코덱스 씨엘아이, 구현, 지피티 이미지 투, 
openai-codex-gpt-image-2-workflow
산출물에 넣을 말: 변경 파일, 이미지 파일, 프롬프트, 스크린샷, 드리프트
검증에 넣을 말: 빌드, 테스트, 브라우저 검증, 파일 존재, 완료 보고
기록에 넣을 말: 옵시디언, 티커 아트로포스, 평가 세트, 실패 패턴, 성공 규칙

아래 형식을 정확히 지켜라.
작업분류:
선행경로:
실행표면:
산출물:
검증:
기록:

Initializing agent...
────────────────────────────────────────

  ┊ 📚 skill     figma-use  0.2s
  ┊ 📚 skill     design-md  0.2s
  ┊ 📚 skill     codex  0.1s
  ┊ 📚 skill     openai-codex-gpt-image-2-workflow  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류:
    웹사이트, 랜딩, 코드, 피그마 제작 요청으로 분류한다. 새 랜딩페이지 제작은 디자인 문맥 정리부터 구현과 브라우저 검증까지 닫는 빌드 작업이다.
    
    선행경로:
    알피 씨엘아이로 현재 저장소와 작업 루트를 먼저 확인한다. DESIGN.md를 디자인 문맥의 기준 파일로 만들거나 갱신한다. 피그마 시안 작업 전에는 figma-use를 선행 로드하고, 피그마 파일의 기존 토큰, 컴포넌트, 레이아웃을 읽어 DESIGN.md와 드리프트를 확인한다.
    
    실행표면:
    헤르메스가 전체 라우터로 움직인다. 피그마 시안은 figma-use 기반으로 다루고, 이미지 방향성이나 지피티 이미지 투 작업은 openai-codex-gpt-image-2-workflow로 처리한다. 코드 구현은 코덱스 씨엘아이로 맡기고, 헤르메스가 구현 결과를 다시 검증한다.
    
    산출물:
    변경 파일, DESIGN.md, 이미지 파일, 지피티 이미지 투 프롬프트, 피그마 기준 스크린샷, 구현 후 브라우저 스크린샷, 디자인과 코드 사이의 드리프트 기록을 남긴다.
    
    검증:
    빌드, 테스트, 브라우저 검증을 반드시 돌린다. 변경 파일과 이미지 파일의 파일 존재 여부를 확인하고, 스크린샷으로 랜딩페이지 화면을 확인한 뒤에만 완료 보고한다.
    
    기록:
    옵시디언에 제작 라우팅 결과를 남긴다. 티커 아트로포스 평가 세트에는 이번 랜딩 제작 흐름의 실패 패턴과 성공 규칙을 기록해서 다음 웹사이트, 랜딩, 코드, 피그마 작업의 재사용 기준으로 삼는다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_093712_4fe089

Session:        20260426_093712_4fe089
Duration:       34s
Messages:       7 (1 user, 5 tool calls)
