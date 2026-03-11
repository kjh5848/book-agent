# RAG기술서 v1 — 프로젝트 오케스트레이터

## 역할

이 디렉토리는 **기술 도서 자동 집필 에이전트 시스템 v1** 프로젝트다.
사용자 지시에 따라 **자동 모드** 또는 **수동 모드**로 파이프라인을 실행한다.

- **수동 모드** (기본): 각 Phase 완료 후 사용자 승인 게이트를 거친다.
- **자동 모드**: `"자동으로 해"` 지시 시, 승인 없이 Phase 0~6을 자동 연속 실행한다.

## 프로젝트 구조

```
projects/RAG기술서_v1/
├── CLAUDE.md              ← 이 파일 (프로젝트 오케스트레이터)
├── progress.json          ← 진행 상태 추적
├── skills-manifest.json   ← 에이전트-스킬 매핑
├── plan/                  ← Phase 1 출력: 설계서, chapter_spec
├── outline/               ← Phase 3 출력: TOC.md
├── examples/              ← Phase 2 출력: 챕터별 예제 프로젝트
├── chapters/              ← Phase 4 출력: 챕터 원고
├── assets/                ← 이미지 (챕터별: assets/CH{N}/)
├── review/                ← 검증 보고서, 회고
└── book_final.md          ← Phase 5 출력: 통합 원고
```

## 스킬 레지스트리

공유 스킬은 `집필에이전트/.claude/skills/` 에 위치한다.
각 에이전트가 사용하는 스킬은 `skills-manifest.json`을 참조한다.

## 파이프라인

> **모드 분기**: 각 Phase에서 `[수동]` 표시된 단계는 수동 모드에서만 실행한다. 자동 모드에서는 건너뛴다.

### Phase 0: 초안 구체화 (대화형)

1. 사용자에게 아래 질문을 순서대로 한다:
   - "어떤 주제의 기술서를 집필하시겠습니까?"
   - "대상 독자는 누구입니까? (초급/중급/고급)"
   - "핵심 기술 스택은 무엇입니까? (예: Python 3.11, LangChain 0.2)"
   - "예상 챕터 수는 몇 개입니까?"
   - "특별히 포함하거나 제외할 주제가 있습니까?"
2. 사용자 응답을 취합하여 `outline/draft.md`로 저장한다.
3. `[수동]` **승인 게이트**: 사용자에게 초안을 보여주고 확인을 요청한다.

### Phase 1: 기획 → 검증

1. `v1-planning-agent` 호출
   - 입력: `outline/draft.md`
   - 출력: `plan/plan.md`, `plan/chapter_spec_CH*.md`
2. `[수동]` **사용자 검토 게이트**: "기획서가 완성되었습니다. plan/plan.md를 검토해 주십시오."
3. `v1-planning-verifier` 호출
   - 출력: `review/verify_plan.md`
4. FAIL 시: planning-agent에 수정 요청 → 재검증 (최대 2회)
5. 2회 후에도 FAIL: `review` 상태 전환, 사용자에게 보고
6. `[수동]` **최종 승인**: "기획이 검증을 통과했습니다. Phase 2로 진행하시겠습니까?"

### Phase 2: 코드 생성 → 검증

1. `v1-code-agent` 호출 (챕터별, 의존성 없으면 병렬)
   - 입력: `plan/plan.md`, `plan/chapter_spec_CH{N}.md`
   - 출력: `examples/CH{N}_{제목}/`
2. `[수동]` **사용자 검토 게이트**: "예제 코드가 생성되었습니다. examples/ 폴더를 검토해 주십시오."
3. `v1-code-verifier` 호출 (챕터별)
   - 출력: `review/verify_code_CH{N}.md`
4. FAIL 시: code-agent에 수정 요청 → 재검증 (최대 2회)
5. `[수동]` **최종 승인**: "코드가 검증을 통과했습니다. Phase 3으로 진행하시겠습니까?"

### Phase 3: 목차 생성 → 검증

1. `v1-toc-agent` 호출
   - 입력: `plan/plan.md`, `plan/chapter_spec_CH*.md`, `examples/`
   - 출력: `outline/TOC.md`
2. `[수동]` **사용자 검토 게이트**: "상세 목차가 생성되었습니다. outline/TOC.md를 검토해 주십시오."
3. `v1-toc-verifier` 호출
   - 출력: `review/verify_toc.md`
4. FAIL 시: toc-agent에 수정 요청 → 재검증 (최대 2회)
5. `[수동]` **최종 승인**: "목차가 검증을 통과했습니다. Phase 4로 진행하시겠습니까?"

### Phase 4: 집필 → 검증 → 독자 리뷰

**챕터별 순차 진행** (이전 챕터 요약이 다음 챕터에 필요):

1. `v1-writing-agent` 호출
   - 입력: `outline/TOC.md`, `plan/chapter_spec_CH{N}.md`, `examples/CH{N}_{제목}/`, 이전 챕터 요약
   - 출력: `chapters/CH{N}_{제목}.md`
2. `[수동]` **사용자 검토 게이트**: "CH{N} 원고가 완성되었습니다. 검토해 주십시오."
3. `v1-writing-verifier` 호출 (챕터별)
   - 출력: `review/verify_chapter_CH{N}.md`
4. FAIL 시: writing-agent에 수정 요청 → 재검증 (최대 2회)
5. **독자 리뷰** (자동 실행): `v1-chapter-reviewer` 호출
   - 입력: `chapters/CH{N}_{제목}.md`, `examples/CH{N}_{제목}/`
   - 출력: `review/chapter_review_CH{N}.md`
   - 독자 관점 피드백을 다음 챕터 집필에 반영
6. `[수동]` 사용자 승인 → 다음 챕터

### Phase 5: 병합

1. `[수동]` **승인 게이트**: "모든 챕터가 완성되었습니다. 최종 병합을 진행하시겠습니까?"
2. 모든 챕터를 합쳐 최종 원고를 확인한다.
3. 챕터 간 용어 일관성, 상호 참조를 확인한다.
4. **단일 통합 원고 생성**:
   ```bash
   python .claude/skills/planning/scripts/merge_book.py projects/RAG기술서_v1
   ```
   - 입력: `outline/TOC.md`, `chapters/CH*.md` (progress.json 순서 기준)
   - 출력: `book_final.md` (표지 + TOC + 전체 챕터 통합본)

#### book_final.md 구성

```
# {책 제목}
> 집필 컨셉, 주인공, 생성일시

---

## 목차 (TOC.md 내용)

---

{CH01 전체 내용}

---

{CH02 전체 내용}

...
```

### Phase 6: 완료 보고

`progress.json`의 `status`를 `done`으로 변경하고 아래 형식으로 보고한다:

```
집필 완료

- 총 챕터 수: N개
- 단일 통합 원고: book_final.md
- 챕터별 원고: chapters/
- 예제 코드: examples/
- 검증 보고서: review/
- 수정 필요 사항: N건 (review 상태 항목)
```

### Phase 6+ (선택): 회고

사용자가 요청하면 `v1-retrospective` 에이전트를 호출한다.
- 출력: `review/retrospective.md`

## 승인 게이트 동작 (수동 모드)

수동 모드에서 모든 승인 게이트는 AskUserQuestion 도구를 사용한다:

```
질문: "{산출물}이 완성되었습니다. 검토 후 진행하시겠습니까?"
옵션:
  - "승인 — 다음 Phase로 진행"
  - "수정 요청 — 특정 부분 수정 후 재확인"
  - "재생성 — 처음부터 다시 생성"
```

## 상태값

| 값 | 의미 |
|----|------|
| `not_started` | 프로젝트 시작 전 |
| `pending` | 해당 Phase 대기 |
| `in_progress` | 해당 Phase 진행 중 |
| `awaiting_approval` | 사용자 승인 대기 (수동 모드) |
| `done` | 완료 |
| `review` | 오류 발생, 사용자 개입 필요 |

## 시작 방법

**수동 모드** (기본):
> "RAG 기술서를 집필해줘"

**자동 모드**:
> "자동으로 RAG 기술서를 집필해줘"
