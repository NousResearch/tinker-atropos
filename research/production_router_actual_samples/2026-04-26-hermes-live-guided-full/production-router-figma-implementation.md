---
task_id: production-router-figma-implementation
title: 피그마 구현 요청 라우팅
lane: actual_hermes_live_guided_full
created_at: 2026-04-26T09:39:32+10:00
source: hermes chat -q
---

# 피그마 구현 요청 라우팅

## 요청

피그마 파일을 기준으로 지금 웹 앱 화면을 맞춰줘. 디자인 엠디도 같이 써줘.

## 실행 지시

```text
너는 민의 헤르메스 제작 라우터다. 아래 요청에 대해 계획만 말하지 말고, 선행 도구, 실행 표면, 산출물, 검증, 기록까지 닫는 답변을 작성하라.

과제: 피그마 구현 요청 라우팅
요청: 피그마 파일을 기준으로 지금 웹 앱 화면을 맞춰줘. 디자인 엠디도 같이 써줘.
반드시 넣을 말: figma-use, 스크린샷, 디자인 문맥, DESIGN.md, 드리프트, 코드 반영
작업분류에 넣을 말: 피그마, 웹 앱, 화면, 디자인
선행경로에 넣을 말: figma-use, 디자인 문맥, 스크린샷, DESIGN.md
실행표면에 넣을 말: 코드 반영, 구현, 토큰, 컴포넌트
산출물에 넣을 말: 스크린샷, 노드, 드리프트, 변경 파일, DESIGN.md
검증에 넣을 말: 브라우저, 화면 비교, 린트, 빌드, 드리프트
기록에 넣을 말: 옵시디언, 스킬, 디자인 계약, 실패 패턴

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
│  Session: 20260426_093849_3f72f8  hermes-agent, hermes-contex...             │
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

과제: 피그마 구현 요청 라우팅
요청: 피그마 파일을 기준으로 지금 웹 앱 화면을 맞춰줘. 디자인 엠디도 같이 써줘.
반드시 넣을 말: figma-use, 스크린샷, 디자인 문맥, DESIGN.md, 드리프트, 코드 반영
작업분류에 넣을 말: 피그마, 웹 앱, 화면, 디자인
선행경로에 넣을 말: figma-use, 디자인 문맥, 스크린샷, DESIGN.md
실행표면에 넣을 말: 코드 반영, 구현, 토큰, 컴포넌트
산출물에 넣을 말: 스크린샷, 노드, 드리프트, 변경 파일, DESIGN.md
검증에 넣을 말: 브라우저, 화면 비교, 린트, 빌드, 드리프트
기록에 넣을 말: 옵시디언, 스킬, 디자인 계약, 실패 패턴

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
  ┊ 📚 skill     figma-implement-design  0.1s
  ┊ 📚 skill     design-md  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류:
    피그마 기준 웹 앱 화면 맞춤 작업이다. 작업분류는 피그마, 웹 앱, 화면, 디자인 구현이다.
    
    선행경로:
    figma-use를 먼저 열고 피그마 디자인 문맥을 가져온다. 같은 노드의 스크린샷을 확보한 뒤, 저장소의 DESIGN.md를 읽어 디자인 문맥과 토큰 기준을 맞춘다. 피그마와 DESIGN.md가 다르면 드리프트로 기록하고 어느 쪽을 기준으로 삼을지 명시한다.
    
    실행표면:
    코드 반영은 저장소에서 한다. 구현은 기존 컴포넌트 재사용을 우선하고, 피그마 토큰과 DESIGN.md 토큰을 맞춰서 색상, 간격, 글꼴, 둥근값을 반영한다. 새 컴포넌트가 필요하면 기존 규칙에 맞춰 추가하고, 하드코딩 대신 토큰으로 연결한다.
    
    산출물:
    산출물은 피그마 스크린샷, 대상 노드 목록, 디자인 문맥 요약, 드리프트 로그, 변경 파일 목록, 갱신 또는 신규 DESIGN.md다. 코드 반영 결과와 함께 어떤 컴포넌트가 바뀌었는지도 남긴다.
    
    검증:
    브라우저에서 실제 웹 앱을 열고 피그마 스크린샷과 화면 비교를 한다. 린트와 빌드를 실행하고, DESIGN.md 기준에서 토큰 드리프트가 남았는지 확인한다. 화면 비교에서 간격, 글꼴, 색상, 정렬, 반응형이 맞지 않으면 다시 코드 반영한다.
    
    기록:
    옵시디언에 피그마 노드, 스크린샷 기준, 디자인 계약, DESIGN.md 변경 이유, 드리프트 판단, 실패 패턴을 기록한다. 반복 가능한 절차나 새로 발견한 실패 패턴은 스킬로 저장하거나 기존 스킬에 보강한다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_093849_3f72f8

Session:        20260426_093849_3f72f8
Duration:       34s
Messages:       6 (1 user, 4 tool calls)
