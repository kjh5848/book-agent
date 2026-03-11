---
name: screenshot
description: 터미널 실행 결과와 브라우저 웹 UI를 PNG 스크린샷으로 생성하는 스킬. terminal_screenshot.py(터미널)와 Playwright MCP(브라우저)를 모두 지원한다.
---

# 스크린샷 스킬

## 핵심 규칙

- 스크린샷 명령어(prompt)에 절대경로/venv 경로를 노출하지 않는다 (`--display` 사용)
- 출력 PNG는 `{project}/assets/CH{N}/`에 저장한다
- 파일명: `{CH번호}_{설명}.png` (예: `06_main-pipeline.png`, `07_chat-ui-running.png`)
- 캡처 후 반드시 PNG 파일 존재와 크기(>5KB)를 검증한다
- **터미널 출력** → `terminal_screenshot.py` 또는 `capture.py` 사용
- **브라우저 웹 UI** → Playwright MCP 도구 사용

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/terminal-capture.md` | 터미널 스크린샷 생성 시 |
| `references/browser-capture.md` | 브라우저 웹 UI 캡처 시 |
