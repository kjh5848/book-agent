---
name: planning
description: 기술 도서 설계서(plan.md) 작성, 갭 분석, 기획 회고 루프 프로토콜. Phase 1 기획 및 검증 시 이 스킬을 로드한다.
---

# 기획 스킬

## 핵심 규칙

- plan.md 출력: 정확히 4개 섹션 필수 (설계서 / 아키텍처 / 환경 명세 / 분량 계획)
- 총 분량: 100페이지 이하 (절대 상한), 단일 챕터: 20페이지 이하
- 기술 스택: 버전 반드시 명시
- 갭 분석: plan.md 작성 전 필수 수행 → 사용자 승인 후에만 작성 시작
- Phase 2 진입: 사용자의 명시적 승인 없이 진입 절대 금지

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/plan-template.md` | plan.md 작성 시 (항상) |
| `references/gap-analysis.md` | 갭 분석 수행 시 (항상) |
| `references/review-loop.md` | 사용자 승인 요청 시 (항상) |
| `references/pagination.md` | 분량 계획 작성 시 |
| `references/merge-book.md` | Phase 5 최종 통합(book_final.md 생성) 실행 시 |

## 스크립트

### `scripts/generate_overview.py` — 마스터 개요 자동 생성

`plan/plan.md` + `plan/chapter_plan/*.md` + `plan/example_plan/*.md`를 읽어
`plan/master_overview.md`를 자동 생성한다.

```bash
python3 .claude/skills/planning/scripts/generate_overview.py <project_dir>
# 예: python3 .claude/skills/planning/scripts/generate_overview.py 수동
```

**출력 섹션**:
1. 프로젝트 개요 (기술 스택 테이블)
2. 챕터 개요 테이블 (CH / 제목 / 유형 / 주요 파일 / 핵심 개념)
3. 챕터별 상세 (섹션 구조 · 예제 파일 · 실행 명령어 · 다음 챕터 연결)
4. 챕터 의존성 그래프 (Mermaid)
5. 빠른 시작 가이드

**호출 시점**: Phase 2 코드 생성 완료 후, Phase 3 목차 작성 전. 또는 사용자가 "개요 보여줘"를 요청할 때.
