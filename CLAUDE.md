# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 집필에이전트 (v1)

## 역할

이 디렉토리는 **기술 도서 자동 집필 에이전트 시스템 v1**의 루트다.
`projects/` 아래에 책별·버전별 프로젝트를 관리한다.

## 폴더 구조

```
집필에이전트/
├── CLAUDE.md              ← 이 파일 (레지스트리)
├── .claude/
│   ├── agents/            ← 공유 에이전트 (13개)
│   └── skills/            ← 공유 스킬 (8개)
└── projects/              ← 책별 프로젝트
    └── {책이름}_v{N}/     ← 프로젝트별 폴더
```

### 프로젝트 내부 구조

```
projects/{책이름}_v{N}/
├── CLAUDE.md              ← 프로젝트 설정
├── progress.json          ← 진행 상태 추적
├── plan/                  ← Phase 1: 설계서
├── outline/               ← Phase 3: TOC.md
├── examples/              ← Phase 2: 챕터별 예제
├── chapters/              ← Phase 4: 챕터 원고
├── assets/                ← 이미지 (assets/CH{N}/)
├── review/                ← 검증 보고서
└── book_final.md          ← Phase 5: 통합 원고
```

## 시작 방법

> "집필해줘" → `v1-orchestrator`가 파이프라인을 실행한다.

## 에이전트 레지스트리 (13개)

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| v1-orchestrator | opus | 파이프라인 전체 관리 (Phase 0~6 순차 실행) |
| v1-planning-agent | opus | 초안 → plan.md (설계서, 아키텍처, 환경명세, 분량계획) |
| v1-planning-verifier | haiku | plan.md 5항목 검증 |
| v1-code-agent | sonnet | plan.md → 챕터별 예제 프로젝트 |
| v1-code-verifier | sonnet | 가상환경 실행 검증, 에러 수정 |
| v1-toc-agent | sonnet | plan.md + 예제코드 → TOC.md |
| v1-toc-verifier | haiku | TOC.md 4항목 검증 |
| v1-writing-agent | sonnet | TOC + chapter_spec + 예제코드 → 챕터 원고 |
| v1-writing-verifier | sonnet | 문체/볼딩/맥락/구조/동기화/분량 6카테고리 검증 |
| v1-chapter-reviewer | sonnet | 학생 관점 독자 리뷰 + Playwright 캡처 |
| v1-screenshot-agent | haiku | 터미널 + 브라우저(Playwright MCP) → PNG 스크린샷 생성 |
| v1-lab-reporter | sonnet | 챕터 예제 실습 + 실습 보고서 생성 |
| v1-retrospective | opus | 책 완성 후 프로세스 회고, 스킬/에이전트 개선 제안 |

## 스킬 레지스트리 (8개)

| 스킬 | 주요 내용 | 사용 에이전트 |
|------|---------|-------------|
| `writing` | 문체(하십시오체), 챕터 4단계 구조, 박스스타일 | toc, writing |
| `writing-concept` | 집필 컨셉(스토리텔링, 튜토리얼 등) 스타일 규칙 | writing |
| `visual` | 이미지 플레이스홀더(3종), Mermaid 문법 | planning, code, writing |
| `code` | Python 컨벤션, 폴더 구조, README 템플릿, IPO 패턴 | code, writing |
| `planning` | plan.md 4섹션 템플릿, 갭 분석, 분량 관리 | planning |
| `verification` | PASS/FAIL 판정, 재시도 프로토콜 | 모든 verifier |
| `screenshot` | 터미널 + 브라우저(Playwright MCP) 스크린샷 워크플로우 | screenshot-agent, lab-reporter |
| `lab-report` | 실습 보고서 템플릿, 평가 기준 | lab-reporter, chapter-reviewer |

## 상태값

| 값 | 의미 |
|----|------|
| `pending` | 대기 중 |
| `in_progress` | 진행 중 |
| `done` | 완료 |
| `review` | 오류 발생, 사용자 개입 필요 |
