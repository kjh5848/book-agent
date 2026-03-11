---
name: writing
description: 기술 도서 집필 문체, 챕터 구조, 박스 스타일 규칙. 모든 집필 에이전트가 사용한다. 챕터 원고 작성, 문체 교정, 구조 설계 시 이 스킬을 로드한다.
---

# 집필 스킬

## 핵심 규칙

- 문체: 격식체 경어(~합니다, ~입니다), 추측 표현 금지
- 볼드: `**용어**` 양쪽에 띄어쓰기 필수
- 이모지: 본문 내 사용 금지
- 구조: 모든 챕터는 `## N. 정리하며`로 끝나야 한다
- 코드 블록 뒤: `> **동작 요약:**` 또는 `> **흐름:**` 배치 (`code/references/code-explanation.md` §6 참조, 스타일은 `plan.md → code_workflow_style`에 따라 결정)
- 실습: GitHub Clone 방식만 사용 — 독자는 코드를 직접 타이핑하지 않는다

## 참조 파일

작업 시작 전 필요한 파일을 로드한다:

| 파일 | 로드 시점 |
|------|---------|
| `references/style.md` | 항상 |
| `references/chapter-structure.md` | 챕터 작성 시 |
| `references/box-style.md` | tip/warning 박스 삽입 시 |
| `references/download-warning.md` | 설치 코드 블록(pip/npm/docker/ollama 등) 작성 시 |
