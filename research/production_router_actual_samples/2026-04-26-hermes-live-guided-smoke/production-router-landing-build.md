---
task_id: production-router-landing-build
title: 웹사이트 제작 요청 라우팅
lane: actual_hermes_live_guided_smoke
created_at: 2026-04-26T09:31:04+10:00
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
작업분류에 넣을 말: 
선행경로에 넣을 말: 
실행표면에 넣을 말: 
산출물에 넣을 말: 
검증에 넣을 말: 
기록에 넣을 말: 

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
│  Session: 20260426_092944_44e93e  hermes-agent, hermes-contex...             │
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
작업분류에 넣을 말: 
선행경로에 넣을 말: 
실행표면에 넣을 말: 
산출물에 넣을 말: 
검증에 넣을 말: 
기록에 넣을 말: 

아래 형식을 정확히 지켜라.
작업분류:
선행경로:
실행표면:
산출물:
검증:
기록:

Initializing agent...
────────────────────────────────────────

  ┊ 📚 skill     figma-use  0.3s
  ┊ 📚 skill     design-md  0.3s
  ┊ 📚 skill     openai-codex-gpt-image-2-workflow  0.3s
  ┊ 📚 skill     codex  0.3s
  ┊ 📚 skill     nextjs-browser-qa-and-dev-server-refresh  0.3s
  ┊ 📚 skill     obsidian  0.1s
  ┊ ✍️  write     /Users/heomin/Obsidian Vault/AI_Toolkit/Guides/웹사이트 제작 요청 라우팅.md  0.9s
  ┊ review diff
a//Users/heomin/Obsidian Vault/AI_Toolkit/Guides/웹사이트 제작 요청 라우팅.md → b//Users/heomin/Obsidian Vault/AI_Toolkit/Guides/웹사이트 제작 요청 라우팅.md
@@ -0,0 +1,16 @@
+---
+title: 웹사이트 제작 요청 라우팅
+type: routing
+tags:
+  - 헤르메스
+  - 랜딩페이지
+  - 피그마
+  - 코덱스
+---
+
+작업분류: 랜딩페이지 제작 전체 흐름. 피그마 시안, DESIGN.md, 지피티 이미지 투 이미지, 코덱스 씨엘아이 구현, 브라우저 검증, 빌드까지 이어지는 제작 라우팅.
+선행경로: figma-use를 먼저 불러 피그마 작업 규칙을 고정하고, 알피 씨엘아이로 대상 저장소와 구조를 확인한 뒤 DESIGN.md를 단일 디자인 기준으로 둔다.
+실행표면: 피그마는 시안과 변수 표면, DESIGN.md는 토큰과 디자인 결정 표면, 지피티 이미지 투 이미지는 시각 자산 표면, 코덱스 씨엘아이는 구현 표면, 브라우저 검증은 실제 화면 판정 표면으로 쓴다.
+산출물: 피그마 시안, DESIGN.md, 이미지 투 이미지 결과물, 랜딩페이지 코드, 빌드 산출물, 브라우저 검증 증거를 남긴다.
+검증: DESIGN.md 린트, 알피 씨엘아이 기반 구조 확인, 빌드 성공, 로컬 서버 확인, 브라우저 검증, 콘솔 오류 확인, 화면 문구와 시각 요소 확인으로 닫는다.
+기록: 이 라우팅은 옵시디언에 기록하고, 최종 완료 보고에는 선행경로, 실행표면, 산출물, 검증 결과를 함께 남긴다.
  ┊ 📖 read      /Users/heomin/Obsidian Vault/AI_Toolkit/Guides/웹사이트 제작 요청 라우팅.md  0.9s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류: 새 랜딩페이지 제작 라우팅. 피그마 시안, DESIGN.md, 지피티 이미지 투 이미지, 코덱스 씨엘아이 구현, 빌드, 브라우저 검증까지 한 흐름으로 묶는 제작 과제.
    선행경로: figma-use, DESIGN.md, openai-codex-gpt-image-2-workflow, 코덱스 씨엘아이, 브라우저 검증 스킬을 먼저 확인했고, 실제 저장소 작업 때는 알피 씨엘아이로 대상 루트와 구조를 먼저 잡는다.
    실행표면: 피그마는 시안 표면, DESIGN.md는 디자인 기준 표면, 지피티 이미지 투 이미지는 시각 자산 표면, 코덱스 씨엘아이는 구현 표면, 브라우저 검증은 실제 화면 판정 표면으로 둔다.
    산출물: 피그마 시안, DESIGN.md, 이미지 투 이미지 결과물, 랜딩페이지 코드, 빌드 산출물, 브라우저 검증 증거, 최종 작업 보고.
    검증: DESIGN.md 린트, 알피 씨엘아이 구조 확인, 빌드 성공, 로컬 서버 확인, 브라우저 검증, 콘솔 오류 확인, 화면 문구와 시각 요소 확인으로 닫는다.
    기록: 옵시디언에 기록 완료. 경로: /Users/heomin/Obsidian Vault/AI_Toolkit/Guides/웹사이트 제작 요청 라우팅.md. read_file로 열여섯 줄 저장 상태까지 확인했다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_092944_44e93e

Session:        20260426_092944_44e93e
Duration:       1m 10s
Messages:       14 (1 user, 12 tool calls)
