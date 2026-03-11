---
name: writing-concept
description: 기술서 집필 컨셉(스타일) 규칙 모음. plan.md의 writing_concept 값에 따라 해당 레퍼런스를 로드한다. v1-writing-agent가 집필 전 반드시 로드한다.
---

# 집필 컨셉 스킬

## 사용 방법

plan.md의 `writing_concept` 값을 확인하고 Read 도구로 해당 레퍼런스 파일을 로드한다.

| writing_concept 값 | 로드할 파일 |
|-------------------|-----------|
| `practical-guide` | `references/practical-guide.md` |
| `storytelling`    | `references/storytelling.md` |
| `recipe`          | `references/recipe.md` |
| `project-buildup` | `references/project-buildup.md` |
| `comparison`      | `references/comparison.md` |
| `workbook`        | `references/workbook.md` |

값이 없거나 미지정인 경우 기본값 `practical-guide`를 사용한다.

## 컨셉 요약

| 컨셉 | 한국어 이름 | 대상 독자 |
|------|-----------|----------|
| `practical-guide` | 실무 지침서 | 실무 적용이 목적인 중급 개발자 |
| `storytelling` | 스토리텔링 | 입문자 및 동기부여가 필요한 독자 |
| `recipe` | 레시피/쿡북 | 문제 해결 참고서가 필요한 중급 이상 |
| `project-buildup` | 프로젝트 빌드업 | 처음부터 끝까지 만들고 싶은 독자 |
| `comparison` | 비교/대조 | 기술 선택 기준이 필요한 시니어 개발자 |
| `workbook` | 워크북 | 실습 중심 학습자 및 부트캠프 참가자 |
