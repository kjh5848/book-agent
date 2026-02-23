# v1 자동 모드 오케스트레이터

## 역할

이 디렉토리는 **기술 도서 자동 집필 에이전트 시스템 v1 (자동 모드)** 프로젝트다.
사용자가 주제를 입력하면 Phase 0~6을 **승인 없이 자동 연속 실행**한다.

## 프로젝트 구조

```
v1/자동/
├── CLAUDE.md              ← 이 파일 (자동 오케스트레이터)
├── 책 집필 에이전트 기획서(자동).md  ← 상세 파이프라인 명세
├── progress.json          ← 진행 상태 추적
├── skills-manifest.json   ← 에이전트-스킬 매핑
├── plan/                  ← Phase 1 출력: 설계서, chapter_spec
├── outline/               ← Phase 3 출력: TOC.md
├── examples/              ← Phase 2 출력: 챕터별 예제 프로젝트
├── chapters/              ← Phase 4 출력: 챕터 원고
├── assets/                ← 이미지, 다이어그램 등
└── review/                ← 검증 보고서, 회고
```

## 스킬 레지스트리

공유 스킬은 `클로드집필/.claude/skills/` 에 위치한다.
각 에이전트가 사용하는 스킬은 `skills-manifest.json`을 참조한다.

## 자동 파이프라인

### Phase 0: 초안 구체화 (대화형)

1. 사용자에게 아래 질문을 순서대로 한다:
   - "어떤 주제의 기술서를 집필하시겠습니까?"
   - "대상 독자는 누구입니까? (초급/중급/고급)"
   - "핵심 기술 스택은 무엇입니까? (예: Python 3.11, LangChain 0.2)"
   - "예상 챕터 수는 몇 개입니까?"
   - "특별히 포함하거나 제외할 주제가 있습니까?"
2. 사용자 응답을 취합하여 `outline/draft.md`로 저장한다.
3. **자동 진행**: 다음 Phase로 즉시 이동한다.

### Phase 1: 기획 → 검증 (자동)

1. `v1-planning-agent` 호출
   - 입력: `outline/draft.md`
   - 출력: `plan/plan.md`, `plan/chapter_spec_CH*.md`
2. `v1-planning-verifier` 호출
   - 입력: `plan/plan.md`, `plan/chapter_spec_CH*.md`
   - 출력: `review/verify_plan.md`
3. FAIL 시: planning-agent에 수정 요청 → 재검증 (최대 2회)
4. 2회 후에도 FAIL: `review` 상태 전환, 사용자에게 보고
5. PASS/CONDITIONAL_PASS: **자동으로 Phase 2 진행**

### Phase 2: 코드 생성 → 검증 (자동)

1. `v1-code-agent` 호출 (챕터별, 의존성 없으면 병렬)
   - 입력: `plan/plan.md`, `plan/chapter_spec_CH{N}.md`
   - 출력: `examples/CH{N}_{제목}/`
2. `v1-code-verifier` 호출 (챕터별)
   - 입력: `examples/CH{N}_{제목}/`
   - 출력: `review/verify_code_CH{N}.md`
3. FAIL 시: code-agent에 수정 요청 → 재검증 (최대 2회)
4. **자동으로 Phase 3 진행**

### Phase 3: 목차 생성 → 검증 (자동)

1. `v1-toc-agent` 호출
   - 입력: `plan/plan.md`, `plan/chapter_spec_CH*.md`, `examples/`
   - 출력: `outline/TOC.md`
2. `v1-toc-verifier` 호출
   - 입력: `outline/TOC.md`, `plan/plan.md`, `examples/`
   - 출력: `review/verify_toc.md`
3. FAIL 시: toc-agent에 수정 요청 → 재검증 (최대 2회)
4. **자동으로 Phase 4 진행**

### Phase 4: 집필 → 검증 (자동)

1. `v1-writing-agent` 호출 (챕터별 순차 — 이전 챕터 요약 필요)
   - 입력: `outline/TOC.md`, `plan/chapter_spec_CH{N}.md`, `examples/CH{N}_{제목}/`, 이전 챕터 요약
   - 출력: `chapters/CH{N}_{제목}.md`
2. `v1-writing-verifier` 호출 (챕터별)
   - 입력: `chapters/CH{N}_{제목}.md`, `examples/CH{N}_{제목}/`, `outline/TOC.md`
   - 출력: `review/verify_chapter_CH{N}.md`
3. FAIL 시: writing-agent에 수정 요청 → 재검증 (최대 2회)
4. **자동으로 Phase 5 진행**

### Phase 5: 병합 (자동)

1. 모든 챕터를 합쳐 최종 원고를 확인한다.
2. 챕터 간 용어 일관성, 상호 참조를 확인한다.
3. `progress.json`을 최종 상태로 업데이트한다.

### Phase 6: 완료 보고

`progress.json`의 `status`를 `done`으로 변경하고 아래 형식으로 보고한다:

```
집필 완료 (자동 모드)

- 총 챕터 수: N개
- 생성된 파일:
  - chapters/CH01_제목.md
  - chapters/CH02_제목.md
  - ...
- 예제 코드:
  - examples/CH01_제목/
  - examples/CH02_제목/
  - ...
- 검증 보고서: review/
- 수정 필요 사항: N건 (review 상태 항목)
```

### Phase 6+ (선택): 회고

사용자가 요청하면 `v1-retrospective` 에이전트를 호출한다.
- 출력: `review/retrospective.md`

## 상태값

| 값 | 의미 |
|----|------|
| `not_started` | 프로젝트 시작 전 |
| `pending` | 해당 Phase 대기 |
| `in_progress` | 해당 Phase 진행 중 |
| `done` | 완료 |
| `review` | 오류 발생, 사용자 개입 필요 |

## 시작 방법

> "RAG 기술서를 집필해줘"

또는

> "Python으로 배우는 웹 크롤링 책을 만들어줘"
