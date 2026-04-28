---
task_id: production-router-figma-implementation
title: 피그마 구현 요청 라우팅
lane: actual_hermes_live_smoke
created_at: 2026-04-26T09:16:15+10:00
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
│  Session: 20260426_091534_30fd8f  hermes-agent, hermes-contex...             │
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
  ┊ 📚 skill     figma-implement-design  0.2s
  ┊ 📚 skill     design-md  0.2s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류:
    피그마 구현 요청 라우팅. 피그마 파일 기준으로 현재 웹 앱 화면을 맞추는 코드 반영 작업이며, 동시에 DESIGN.md를 작성하거나 갱신하는 디자인 문맥 고정 작업이다.
    
    선행경로:
    figma-use를 먼저 로드한 뒤 피그마에서 디자인 문맥과 스크린샷을 가져온다. 이어서 design-md와 figma-implement-design 경로를 적용한다. 코드 저장소 작업이므로 Repo Prompt 선행 확인으로 대상 저장소와 화면 파일을 잡고, 기존 DESIGN.md가 있으면 먼저 읽어 드리프트를 확인한다.
    
    실행표면:
    피그마 MCP는 디자인 문맥, 노드 구조, 스크린샷, 자산 추출 표면으로 사용한다. Repo Prompt와 코드 도구는 웹 앱 코드 반영 표면으로 사용한다. DESIGN.md는 색, 글꼴, 간격, 둥근값, 구성 요소 규칙을 고정하는 문서 표면으로 사용한다.
    
    산출물:
    피그마 기준으로 맞춘 웹 앱 화면 코드 반영 결과, 새로 작성하거나 갱신한 DESIGN.md, 피그마와 현재 코드 사이의 드리프트 기록, 필요한 자산 반영, 그리고 변경 파일 목록을 남긴다.
    
    검증:
    피그마 스크린샷과 로컬 웹 앱 스크린샷을 나란히 비교해 간격, 정렬, 글꼴, 색, 둥근값, 자산 누락을 확인한다. DESIGN.md는 린트와 토큰 참조 검사를 돌리고, 웹 앱은 빌드나 테스트, 브라우저 화면 확인까지 끝낸다. 드리프트가 남으면 의도된 차이인지 수정 대상인지 기록한다.
    
    기록:
    최종 보고에는 사용한 선행경로가 figma-use, Repo Prompt, design-md였음을 적고, 스크린샷 기준 검증 결과, 디자인 문맥 출처, DESIGN.md 경로, 코드 반영 파일, 남은 드리프트 여부를 함께 남긴다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_091534_30fd8f

Session:        20260426_091534_30fd8f
Duration:       32s
Messages:       6 (1 user, 4 tool calls)
