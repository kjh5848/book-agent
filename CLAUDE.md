# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 집필에이전트 오케스트레이터 (claude_v1)

## 역할

이 디렉토리는 **기술 도서 자동 집필 에이전트 시스템 v1**의 루트다.
**자동 모드**와 **수동 모드** 두 가지로 운영된다.

## 폴더 구조

```
집필에이전트/
├── CLAUDE.md              ← 이 파일 (루트 오케스트레이터)
├── README.md              ← 전체 시스템 설계 개요
├── .claude/
│   ├── agents/            ← 공유 에이전트 (9개)
│   └── skills/            ← 공유 스킬 (5개 + skill-creator)
├── 수동/                  ← v1 수동 모드 (매 Phase 승인 게이트)
└── 자동/                  ← v1 자동 모드 (자동 연속 실행)
```

## v1 파이프라인 (6 Phase)

```
Phase 0: 초안 구체화 (대화형)
Phase 1: 기획  (v1-planning-agent  → v1-planning-verifier)
Phase 2: 코드  (v1-code-agent      → v1-code-verifier)
Phase 3: 목차  (v1-toc-agent       → v1-toc-verifier)
Phase 4: 집필  (v1-writing-agent   → v1-writing-verifier)  ← 챕터별 반복
Phase 5: 병합 + 완료
Phase 6+: 회고 (v1-retrospective, 선택)
```

## v1 에이전트 (9개)

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| v1-planning-agent | opus | 초안 → plan.md (설계서, 아키텍처, 환경명세, 분량계획) |
| v1-planning-verifier | haiku | plan.md 5항목 검증 |
| v1-code-agent | sonnet | plan.md → 챕터별 예제 프로젝트 |
| v1-code-verifier | sonnet | 가상환경 실행 검증, 에러 수정 |
| v1-toc-agent | sonnet | plan.md + 예제코드 → TOC.md |
| v1-toc-verifier | haiku | TOC.md 4항목 검증 |
| v1-writing-agent | sonnet | TOC + chapter_spec + 예제코드 → 챕터 원고 |
| v1-writing-verifier | sonnet | 문체/볼딩/맥락/구조/동기화/분량 6카테고리 검증 |
| v1-retrospective | opus | 책 완성 후 프로세스 회고, 스킬/에이전트 개선 제안 |

## v1 스킬 (5개)

| 스킬 | 주요 내용 | 사용 에이전트 |
|------|---------|-------------|
| `writing` | 문체(하십시오체), 챕터 4단계 구조, 박스스타일, 독자 수준별 심도 | toc, writing |
| `visual` | Gemini 이미지 플레이스홀더(3종), Mermaid 문법 | planning, code, writing |
| `code` | Python 컨벤션, 폴더 구조, README 템플릿, IPO 패턴 + `scripts/scaffold_project.py` | code, writing |
| `planning` | plan.md 4섹션 템플릿, 갭 분석, 기획-회고 루프, 분량 관리 | planning |
| `verification` | PASS/FAIL 판정, 재시도 프로토콜 + `scripts/check_structure.py` | 모든 verifier |

### 에이전트-스킬 매핑

| 에이전트 | 스킬 |
|---------|------|
| v1-planning-agent | planning, visual |
| v1-planning-verifier | planning, verification |
| v1-code-agent | code, visual |
| v1-code-verifier | code, verification |
| v1-toc-agent | writing, planning |
| v1-toc-verifier | writing, planning, verification |
| v1-writing-agent | writing, visual, code |
| v1-writing-verifier | writing, visual, code, verification |

## 시작 방법

**수동 모드** (매 Phase 사용자 승인):
> "수동 모드로 RAG 기술서를 집필해줘"
> → `수동/CLAUDE.md` 참조

**자동 모드** (자동 연속 실행):
> "자동 모드로 RAG 기술서를 집필해줘"
> → `자동/CLAUDE.md` 참조

## 에이전트 상태값

| 값 | 의미 |
|----|------|
| `pending` | 대기 중 |
| `in_progress` | 진행 중 |
| `awaiting_approval` | 사용자 승인 대기 |
| `done` | 완료 |
| `review` | 오류 발생, 사용자 개입 필요 |
