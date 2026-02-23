---
name: verification
description: 검증 에이전트 공통 보고서 형식, PASS/FAIL 판정 기준, 재시도 프로토콜. 모든 검증 단계(plan, code, toc, chapter)에서 이 스킬을 로드한다.
---

# 검증 스킬 (Verification)

## 핵심 규칙 요약

- 판정: PASS / CONDITIONAL_PASS / FAIL
- FAIL: 실패 항목 + 수정 제안 반드시 포함
- 재시도: 최대 2회, 이후 `review` 상태로 전환
- 보고서: 마크다운 형식, `review/verify_{대상}.md`에 저장
- 스크립트: `scripts/check_structure.py`로 파일 구조 자동 검증

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/common-rules.md` | 검증 수행 시 (항상) |

## 스크립트

- `scripts/check_structure.py` — 프로젝트/챕터 파일 구조 자동 검증
