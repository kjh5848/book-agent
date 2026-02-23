# v1 수동 모드 오케스트레이터

## 역할

이 디렉토리는 **기술 도서 자동 집필 에이전트 시스템 v1 (수동 모드)** 프로젝트다.
각 Phase 완료 후 **사용자 검토 및 승인을 거쳐** 다음 Phase로 진행한다.

## 프로젝트 구조

```
v1/수동/
├── CLAUDE.md              ← 이 파일 (수동 오케스트레이터)
├── 책 집필 에이전트 기획서(수동).md  ← 상세 파이프라인 명세
├── progress.json          ← 진행 상태 추적 (승인 상태 포함)
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

## 수동 파이프라인

### Phase 0: 초안 구체화 (대화형 + 승인)

1. 사용자에게 아래 질문을 순서대로 한다:
   - "어떤 주제의 기술서를 집필하시겠습니까?"
   - "대상 독자는 누구입니까? (초급/중급/고급)"
   - "핵심 기술 스택은 무엇입니까? (예: Python 3.11, LangChain 0.2)"
   - "예상 챕터 수는 몇 개입니까?"
   - "특별히 포함하거나 제외할 주제가 있습니까?"
2. 사용자 응답을 취합하여 `outline/draft.md`로 저장한다.
3. **승인 게이트**: 사용자에게 초안을 보여주고 확인을 요청한다.
   - "초안이 완성되었습니다. 검토 후 수정할 부분이 있으면 말씀해 주십시오. 진행하시겠습니까?"
   - 사용자가 수정 요청 시 → 수정 후 재확인
   - 사용자가 승인 시 → Phase 1 진행

### Phase 1: 기획 → 사용자 검토 → 검증 → 승인

1. `v1-planning-agent` 호출
   - 입력: `outline/draft.md`
   - 출력: `plan/plan.md`, `plan/chapter_spec_CH*.md`
2. **사용자 검토 게이트**:
   - "기획서가 완성되었습니다. plan/plan.md를 검토해 주십시오."
   - 사용자 수정 요청 시 → planning-agent 재호출 또는 직접 수정
   - 사용자 승인 시 → 검증 진행
3. `v1-planning-verifier` 호출
   - 출력: `review/verify_plan.md`
4. FAIL 시: 사용자에게 검증 결과 보고 → 수정 후 재검증
5. **최종 승인**: "기획이 검증을 통과했습니다. Phase 2로 진행하시겠습니까?"

### Phase 2: 코드 생성 → 사용자 검토 → 검증 → 승인

1. `v1-code-agent` 호출 (챕터별, 의존성 없으면 병렬)
   - 출력: `examples/CH{N}_{제목}/`
2. **사용자 검토 게이트**:
   - "예제 코드가 생성되었습니다. examples/ 폴더를 검토해 주십시오."
   - 사용자 수정 요청 시 → code-agent 재호출 또는 직접 수정
3. `v1-code-verifier` 호출 (챕터별)
   - 출력: `review/verify_code_CH{N}.md`
4. FAIL 시: 사용자에게 보고 → 수정 → 재검증 (최대 2회)
5. **최종 승인**: "코드가 검증을 통과했습니다. Phase 3으로 진행하시겠습니까?"

### Phase 3: 목차 생성 → 사용자 검토 → 검증 → 승인

1. `v1-toc-agent` 호출
   - 출력: `outline/TOC.md`
2. **사용자 검토 게이트**:
   - "상세 목차가 생성되었습니다. outline/TOC.md를 검토해 주십시오."
   - 사용자 수정 요청 시 → toc-agent 재호출 또는 직접 수정
3. `v1-toc-verifier` 호출
   - 출력: `review/verify_toc.md`
4. **최종 승인**: "목차가 검증을 통과했습니다. Phase 4로 진행하시겠습니까?"

### Phase 4: 집필 → 챕터별 사용자 검토 → 검증

1. **챕터별 순차 진행** (각 챕터마다 승인 게이트):
   a. `v1-writing-agent` 호출
      - 출력: `chapters/CH{N}_{제목}.md`
   b. **사용자 검토 게이트**:
      - "CH{N} 원고가 완성되었습니다. 검토해 주십시오."
      - 사용자 수정 요청 시 → writing-agent 재호출 또는 직접 수정
   c. `v1-writing-verifier` 호출
      - 출력: `review/verify_chapter_CH{N}.md`
   d. FAIL 시: 수정 → 재검증 (최대 2회)
   e. 사용자 승인 → 다음 챕터
2. 모든 챕터 완료 후: **Phase 5 진행 승인 요청**

### Phase 5: 병합 (승인 후)

1. **승인 게이트**: "모든 챕터가 완성되었습니다. 최종 병합을 진행하시겠습니까?"
2. 모든 챕터를 합쳐 최종 원고를 확인한다.
3. 챕터 간 용어 일관성, 상호 참조를 확인한다.

### Phase 6: 완료 보고

`progress.json`의 `status`를 `done`으로 변경하고 아래 형식으로 보고한다:

```
집필 완료 (수동 모드)

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
- 사용자 수정 횟수: N회
- 수정 필요 사항: N건 (review 상태 항목)
```

### Phase 6+ (선택): 회고

사용자가 요청하면 `v1-retrospective` 에이전트를 호출한다.
- 출력: `review/retrospective.md`

## 승인 게이트 동작

모든 승인 게이트에서 AskUserQuestion 도구를 사용한다:

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
| `awaiting_approval` | 사용자 승인 대기 |
| `done` | 완료 |
| `review` | 오류 발생, 사용자 개입 필요 |

## 시작 방법

> "RAG 기술서를 집필해줘"

또는

> "Python으로 배우는 웹 크롤링 책을 만들어줘"
