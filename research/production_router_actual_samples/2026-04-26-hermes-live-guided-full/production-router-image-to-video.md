---
task_id: production-router-image-to-video
title: 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅
lane: actual_hermes_live_guided_full
created_at: 2026-04-26T09:38:47+10:00
source: hermes chat -q
---

# 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅

## 요청

지피티 이미지 투로 제품 이미지를 만들고, 럽아트에서 시댄스 이점영 영상까지 실험해줘.

## 실행 지시

```text
너는 민의 헤르메스 제작 라우터다. 아래 요청에 대해 계획만 말하지 말고, 선행 도구, 실행 표면, 산출물, 검증, 기록까지 닫는 답변을 작성하라.

과제: 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅
요청: 지피티 이미지 투로 제품 이미지를 만들고, 럽아트에서 시댄스 이점영 영상까지 실험해줘.
반드시 넣을 말: openai-codex-gpt-image-2-workflow, 파일 존재, 럽아트, 시댄스, 점수표, 다음 변수
작업분류에 넣을 말: 이미지, 영상, 럽아트, 시댄스
선행경로에 넣을 말: openai-codex-gpt-image-2-workflow, 지피티 이미지 투, 프롬프트, 파일 존재
실행표면에 넣을 말: 이미지 생성, 럽아트, 시댄스, 영상, 변형
산출물에 넣을 말: 이미지 파일, 영상, 링크, 프롬프트, 점수표
검증에 넣을 말: 파일 존재, 크기, 시각 확인, 점수표, 결과
기록에 넣을 말: 학습 질문, 기준군, 변형, 유지할 것, 버릴 것, 다음 변수

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
│  Session: 20260426_093756_a028e0  hermes-agent, hermes-contex...             │
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

과제: 지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅
요청: 지피티 이미지 투로 제품 이미지를 만들고, 럽아트에서 시댄스 이점영 영상까지
실험해줘.
반드시 넣을 말: openai-codex-gpt-image-2-workflow, 파일 존재, 럽아트, 시댄스, 
점수표, 다음 변수
작업분류에 넣을 말: 이미지, 영상, 럽아트, 시댄스
선행경로에 넣을 말: openai-codex-gpt-image-2-workflow, 지피티 이미지 투, 
프롬프트, 파일 존재
실행표면에 넣을 말: 이미지 생성, 럽아트, 시댄스, 영상, 변형
산출물에 넣을 말: 이미지 파일, 영상, 링크, 프롬프트, 점수표
검증에 넣을 말: 파일 존재, 크기, 시각 확인, 점수표, 결과
기록에 넣을 말: 학습 질문, 기준군, 변형, 유지할 것, 버릴 것, 다음 변수

아래 형식을 정확히 지켜라.
작업분류:
선행경로:
실행표면:
산출물:
검증:
기록:

Initializing agent...
────────────────────────────────────────

  ┊ 📚 skill     openai-codex-gpt-image-2-workflow  0.0s
  ┊ 📚 skill     lovart-learning-loop  0.1s
  ┊ 📚 skill     seedance-prompt-repo-analysis-to-obsidian  0.1s

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    작업분류:
    이미지 → 영상 연결 실험. 지피티 이미지 투로 제품 이미지 기준군을 만들고, 럽아트에서 시댄스 영상 변형까지 이어지는 제작 라우팅이다. 작업분류는 이미지, 영상, 럽아트, 시댄스 실험으로 닫는다.
    
    선행경로:
    openai-codex-gpt-image-2-workflow를 먼저 적용한다. 지피티 이미지 투 생성 전 프롬프트를 고정하고, 생성 뒤에는 파일 존재를 확인한다. 그다음 해당 이미지 파일을 럽아트 참조로 넘겨 시댄스 실험 프롬프트를 만든다.
    
    실행표면:
    1. 이미지 생성: openai-codex-gpt-image-2-workflow로 제품 이미지 생성
    2. 럽아트: 생성된 제품 이미지를 참조 이미지로 업로드
    3. 시댄스: 럽아트 안에서 시댄스 이점영 영상 생성
    4. 영상 변형: 기준군 하나와 변형 하나 이상 실행
    5. 변형 기준: 카메라, 움직임, 제품 고정 문장, 마지막 장면 중 다음 변수 하나만 바꿈
    
    산출물:
    이미지 파일, 영상, 링크, 프롬프트, 점수표를 남긴다. 이미지 파일은 절대 경로로 남기고, 럽아트 결과는 영상 링크 또는 저장 파일로 남긴다. 프롬프트는 이미지 생성용과 시댄스 영상용을 분리해서 기록한다. 점수표에는 제품 충실도, 장면 선명도, 카메라 자연스러움, 움직임 설득력, 마지막 장면 힘, 사업 활용도를 넣는다.
    
    검증:
    파일 존재를 확인한다. 이미지 파일은 크기를 확인하고, 시각 확인으로 제품 이미지가 의도와 맞는지 본다. 럽아트 시댄스 영상은 결과 링크 또는 저장본을 확인하고, 점수표를 작성한다. 최종 결과는 파일 존재, 크기, 시각 확인, 점수표, 결과 링크 또는 영상 파일까지 있어야 완료로 본다.
    
    기록:
    학습 질문: 지피티 이미지 투 제품 이미지를 참조로 넣었을 때 럽아트 시댄스 영상의 제품 일관성이 유지되는가.
    기준군: 원본 제품 이미지와 기본 시댄스 프롬프트.
    변형: 다음 변수 하나만 바꾼 영상 버전.
    유지할 것: 제품 형태, 로고나 핵심 특징, 마지막 영웅 장면, 짧은 세 박자 구조.
    버릴 것: 과한 배경, 긴 설명, 여러 카메라 움직임 동시 지시, 제품을 흐리는 장식.
    다음 변수: 카메라 움직임, 제품 고정 문장, 손 사용 장면, 마지막 장면 구도 중 하나를 다음 실험 변수로 잡는다.
╰──────────────────────────────────────────────────────────────────────────────╯

Resume this session with:
  hermes --resume 20260426_093756_a028e0

Session:        20260426_093756_a028e0
Duration:       41s
Messages:       7 (1 user, 5 tool calls)
