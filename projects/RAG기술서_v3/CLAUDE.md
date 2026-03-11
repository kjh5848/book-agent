# RAG기술서 v3 — 프로젝트 설정

## 프로젝트 정보

- **writing_concept**: `practical-guide` (실무 지침서)

## 프로젝트 구조

```
projects/RAG기술서_v3/
├── CLAUDE.md              ← 이 파일
├── progress.json          ← 진행 상태 추적
├── plan/                  ← Phase 1 출력: 설계서, chapter_spec
├── outline/               ← Phase 0/3 출력: draft.md, TOC.md
├── examples/              ← Phase 2 출력: 챕터별 예제 프로젝트
├── chapters/              ← Phase 4 출력: 챕터 원고
├── assets/                ← 이미지 (챕터별: assets/CH{N}/)
├── review/                ← 검증 보고서
└── book_final.md          ← Phase 5 출력: 통합 원고
```

## 스킬 레지스트리

공유 스킬은 `.claude/skills/`에 위치한다.

## 파이프라인 실행

`v1-orchestrator` 에이전트가 전체 파이프라인을 관리한다.
현재 진행 상태는 `progress.json`을 참조한다.
