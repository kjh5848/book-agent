# Verification Common Rules

## 1. Judgment Criteria
<!-- PASS/FAIL/CONDITIONAL_PASS 판정 기준 -->

| Judgment | Condition | Next Action |
|----------|-----------|-------------|
| **PASS** | All required items passed | Proceed to next Phase |
| **CONDITIONAL_PASS** | Required items passed, some recommended items failed | Proceed to next Phase (record warnings) |
| **FAIL** | One or more required items failed | Request revision from production agent, then re-verify |

## 2. Verification Report Standard Format
<!-- 검증 보고서 표준 형식 -->

```markdown
# Verification Report: {Target Name}

## Judgment: {PASS / CONDITIONAL_PASS / FAIL}

## Verification Items

| # | Item | Required/Recommended | Result | Notes |
|---|------|----------------------|--------|-------|
| 1 | {item name} | Required | PASS/FAIL | {details} |
| 2 | {item name} | Recommended | PASS/FAIL | {details} |

## Failed Item Details (when FAIL)

### Item {number}: {item name}
- **Current State**: {problem description}
- **Expected State**: {correct state}
- **Suggested Fix**: {specific fix method}

## Summary
- Total verification items: {N}
- Passed: {N}
- Failed: {N}
- Attempt count: {N}/2
```

## 3. Retry Protocol
<!-- 검증 실패 시 재시도 프로토콜 -->

1. When the verification agent issues a FAIL judgment, it returns a report containing details of the failed items.
2. The orchestrator forwards the report to the production agent and requests revisions.
3. After the production agent completes revisions, the verification agent re-verifies.
4. If FAIL persists after **a maximum of 2 retries**, the Phase transitions to `review` status.
5. `review` status means manual user intervention is required.

## 4. Code Workflow Exception Condition
<!-- 코드 워크플로우 예외 조건 — bash 블록 CONDITIONAL 방지 -->

**bash/shell code blocks are exempt from the Code Workflow requirement.**

When evaluating writing verification item "Code Workflow placement":
- `python`, `javascript`, `typescript` blocks → **Required** (FAIL if missing)
- `bash`, `sh`, `zsh`, `shell` blocks → **Exempt** (do NOT mark as CONDITIONAL or FAIL)

This prevents all chapters from generating unnecessary CONDITIONAL_PASS judgments due to shell command blocks.

## 5. Per-Phase Verification Checklist Reference
<!-- 각 Phase별 검증 체크리스트 참조 -->

Each verification agent uses the checklist corresponding to its Phase:

- **Planning verification**: "Planning Verification Checklist" in `planning/blueprint.md` (5 items)
- **Code verification**: `code-python/error-handling.md` + execution verification (7 items)
- **TOC verification**: "TOC Verification Checklist" in `planning/pagination.md` (4 items)
- **Writing verification**: Checklists in `writing/style.md` + `writing/chapter-structure.md` (6 categories)
