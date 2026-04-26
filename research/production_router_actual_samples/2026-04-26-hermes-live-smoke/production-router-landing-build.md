---
task_id: production-router-landing-build
title: 웹사이트 제작 요청 라우팅
lane: actual_hermes_live_smoke
created_at: 2026-04-26T09:13:07+10:00
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
│  Session: 20260426_091215_fe921d  hermes-agent, hermes-contex...             │
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

아래 형식을 정확히 지켜라.
작업분류:
선행경로:
실행표면:
산출물:
검증:
기록:

Initializing agent...
────────────────────────────────────────

  ┊ 📚 skill     figma-use  0.1s
  ┊ 📚 skill     design-md  0.2s
  ┊ 📚 skill     codex  0.2s
  ┊ 📚 skill     openai-codex-gpt-image-2-workflow  0.1s
  ┊ 📚 skill     nextjs-browser-qa-and-dev-server-refresh  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류:
    새 랜딩페이지 제작 라우팅. 피그마 시안 생성, DESIGN.md 작성, 지피티 이미지 투 이미지 자산 생성, 코덱스 씨엘아이 구현, 빌드, 브라우저 검증까지 이어지는 표준 제작 흐름이다.
    
    선행경로:
    알피 씨엘아이로 대상 저장소와 작업 루트를 먼저 확인한다. 그다음 figma-use를 선행으로 불러 피그마 파일 구조와 기존 토큰을 확인한다. 디자인 기준은 DESIGN.md에 먼저 고정하고, 이미지 작업은 openai-codex 기반 지피티 이미지 투 이미지 경로를 쓴다.
    
    실행표면:
    피그마 시안은 figma-use 기반 피그마 실행 표면에서 만든다. 디자인 규칙은 저장소 루트의 DESIGN.md에 기록한다. 구현은 저장소 안에서 코덱스 씨엘아이로 진행한다. 이미지 자산은 gpt-image-2 경로로 생성해 프로젝트 자산 폴더에 넣는다. 최종 화면은 로컬 개발 서버와 브라우저 검증 표면에서 확인한다.
    
    산출물:
    피그마 랜딩페이지 시안, DESIGN.md, 이미지 투 이미지 생성 자산, 구현된 랜딩페이지 코드, 빌드 산출물, 브라우저 검증 결과를 남긴다. 코드 구현 에이전트에는 DESIGN.md와 피그마 캡처를 함께 넘겨 임의 색상이나 간격을 만들지 않게 한다.
    
    검증:
    알피 씨엘아이로 실제 저장소 루트 확인. DESIGN.md는 린트로 토큰과 대비를 확인. 코덱스 씨엘아이 구현 뒤 패키지 검사와 빌드를 실행. 로컬 서버를 띄운 뒤 브라우저 검증으로 실제 화면, 콘솔 오류, 반응형, 문구 잔존, 이미지 표시를 확인. 빌드 성공만으로 완료 판정하지 않고 브라우저 화면까지 맞아야 완료로 본다.
    
    기록:
    결정 기준은 DESIGN.md에 남기고, 실행 로그는 작업 노트나 저장소 기록에 남긴다. 최종 보고에는 사용한 선행경로, 피그마 파일 또는 시안 위치, 변경 파일, 이미지 자산 경로, 빌드 결과, 브라우저 검증 결과를 함께 적는다. 이번 라우팅 답변은 figma-use, DESIGN.md, 코덱스 씨엘아이, 지피티 이미지 경로, 브라우저 검증 스킬을 확인한 뒤 작성했다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_091215_fe921d

Session:        20260426_091215_fe921d
Duration:       43s
Messages:       9 (1 user, 7 tool calls)
