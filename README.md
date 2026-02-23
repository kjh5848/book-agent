## Context

`claude_agent_guide.md` 기반으로 기술서 자동 집필 에이전트 시스템 v1을 구축한다.
**자동 모드**와 **수동 모드** 두 프로젝트를 동시에 만들어 비교 테스트한다.

핵심 원칙:

- 스킬은 `references/` 하위 파일로 분리하여 필요 시 로드 (Progressive Disclosure)
- 에이전트와 스킬은 공유, 오케스트레이터만 다름
- 프로젝트 특화 설정(아이콘 사전, LLM 선택 등)은 `outline/` 폴더에 위치

---

## 전체 구조

```
집필에이전트/
├── README.md
├── CLAUDE.md                         ← 루트 오케스트레이터
├── .claude/
│   ├── agents/                       ← 공유 에이전트 (9개)
│   │   ├── v1-planning-agent.md      ← skills: planning, visual
│   │   ├── v1-planning-verifier.md   ← skills: planning, verification
│   │   ├── v1-code-agent.md          ← skills: code, visual
│   │   ├── v1-code-verifier.md       ← skills: code, verification
│   │   ├── v1-toc-agent.md           ← skills: writing, planning
│   │   ├── v1-toc-verifier.md        ← skills: writing, planning, verification
│   │   ├── v1-writing-agent.md       ← skills: writing, visual, code
│   │   ├── v1-writing-verifier.md    ← skills: writing, visual, code, verification
│   │   └── v1-retrospective.md       ← 회고 에이전트 (책 완성 후 실행)
│   └── skills/                       ← 공유 스킬 (5개 + skill-creator)
│       ├── skill-creator/            ← npx skills add로 설치
│       ├── writing/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── style.md          ← 문체, 볼딩, 독자 수준별 심도
│       │       ├── chapter-structure.md
│       │       └── box-style.md
│       ├── visual/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── image.md          ← 3종 플레이스홀더 (개념/Gemini/캡처)
│       │       └── mermaid.md
│       ├── code/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   └── scaffold_project.py   ← 챕터 프로젝트 자동 생성
│       │   └── references/
│       │       ├── naming.md
│       │       ├── docstring.md
│       │       ├── error-handling.md
│       │       ├── IPO-pattern.md
│       │       ├── folder-structure.md
│       │       ├── README-template.md
│       │       └── dependencies.md
│       ├── planning/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── plan-template.md  ← 4섹션 템플릿, chapter_spec
│       │       ├── gap-analysis.md   ← 갭 분석 절차, 우선순위
│       │       ├── review-loop.md    ← 기획-회고 루프, LLM Provider 원칙
│       │       └── pagination.md
│       └── verification/
│           ├── SKILL.md
│           ├── scripts/
│           │   └── check_structure.py    ← 프로젝트 구조 자동 검증
│           └── references/
│               └── common-rules.md
├── 자동/                              ← 자동 모드 프로젝트
│   ├── CLAUDE.md
│   ├── progress.json
│   ├── plan/ outline/ examples/ chapters/ assets/ review/
└── 수동/                              ← 수동 모드 프로젝트
    ├── CLAUDE.md
    ├── progress.json
    ├── outline/
    │   ├── draft.md                  ← Phase 0 초안
    │   └── image-guide.md            ← 이 책 전용 Gemini 아이콘 사전
    ├── plan/ examples/ chapters/ assets/ review/
```

---

## 자동 vs 수동 차이점

| 구분 | 자동 모드 | 수동 모드 |
| --- | --- | --- |
| Phase 0 (초안) | 대화형 질문 → **자동 진행** | 대화형 질문 → **사용자 검토/수정** |
| Phase 1 (기획) | agent → verifier → **자동 진행** | agent → **사용자 검토/수정** → verifier → **승인** |
| Phase 2 (코드) | agent → verifier → **자동 진행** | agent → **사용자 검토/수정** → verifier → **승인** |
| Phase 3 (목차) | agent → verifier → **자동 진행** | agent → **사용자 검토/수정** → verifier → **승인** |
| Phase 4 (집필) | agent → verifier → **자동 진행** | 챕터별 → **사용자 검토/수정** → 다음 챕터 |
| Phase 5 (병합) | 자동 | **승인 후** 병합 |

---

## 에이전트-스킬 매핑

```json
{
  "v1-planning-agent":   ["planning", "visual"],
  "v1-planning-verifier":["planning", "verification"],
  "v1-code-agent":       ["code", "visual"],
  "v1-code-verifier":    ["code", "verification"],
  "v1-toc-agent":        ["writing", "planning"],
  "v1-toc-verifier":     ["writing", "planning", "verification"],
  "v1-writing-agent":    ["writing", "visual", "code"],
  "v1-writing-verifier": ["writing", "visual", "code", "verification"]
}
```

> 다른 언어 기술서를 쓸 때: `code` 스킬의 `references/naming.md`, `docstring.md`만 교체.

---

## 스킬 설계 원칙

| 원칙 | 설명 |
|------|------|
| Progressive Disclosure | `SKILL.md`(요약) → `references/`(상세, 필요 시만 로드) |
| 재사용성 | 스킬에 프로젝트 특화 내용 금지. 특화 내용은 `outline/`에 |
| 스크립트 우선 | 반복 가능한 검증/생성 작업은 `scripts/`에 Python으로 |
| 이미지 3분류 | 개념→Gemini 플레이스홀더, 실습결과→캡처 플레이스홀더, 흐름→Mermaid |
