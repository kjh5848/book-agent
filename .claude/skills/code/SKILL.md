---
name: code
description: 기술 도서 예제 코드의 Python 컨벤션, 프로젝트 구조, README 템플릿, IPO 워크플로우 패턴 규칙. 예제 코드 생성, 프로젝트 스캐폴딩, 코드 검증 시 이 스킬을 로드한다.
---

# 코드 스킬 (Code)

## 핵심 규칙 요약

- 네이밍: 변수/함수 `snake_case`, 클래스 `PascalCase`, 상수 `UPPER_SNAKE_CASE`
- Docstring: 모든 함수에 한국어 역할 설명 + Args/Returns/Raises
- 타입 힌트: 모든 함수에 적용 (Python 3.9+ 내장 타입)
- 실습 방식: GitHub Clone 전용 — `clone → .env → pip install → run` 순서
- 인프라: Docker Compose로 DB/백엔드 구동 (직접 설치 금지)
- 스크립트: `scripts/scaffold_project.py`로 표준 폴더 구조 자동 생성

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/folder-structure.md` | 프로젝트 구조 설계 시 (항상) |
| `references/README-template.md` | README.md 작성 시 |
| `references/naming.md` | Python 네이밍 규칙 확인 시 |
| `references/docstring.md` | Docstring 작성 시 |
| `references/error-handling.md` | 에러 처리 구현 시 |
| `references/IPO-pattern.md` | 코드 워크플로우 섹션 작성 시 |
| `references/dependencies.md` | requirements.txt 작성 시 |

## 스크립트

- `scripts/scaffold_project.py` — 표준 챕터 프로젝트 폴더 구조 자동 생성
