---
name: code
description: 기술 도서 예제 코드의 Python 컨벤션, 프로젝트 구조, README 템플릿, 코드 설명 패턴 규칙. 예제 코드 생성, 프로젝트 스캐폴딩, 코드 검증 시 이 스킬을 로드한다.
---

# 코드 스킬

## 핵심 규칙

- 네이밍: 변수/함수 `snake_case`, 클래스 `PascalCase`, 상수 `UPPER_SNAKE_CASE`
- 독스트링: 모든 함수에 한국어 역할 설명 + Args/Returns/Raises 필수
- 타입 힌트: 모든 함수에 적용 (Python 3.9+ 내장 타입)
- 실습 방식: GitHub Clone 방식만 사용 — `clone → .env → pip install → run`
- 인프라: DB/백엔드는 Docker Compose로 실행 (직접 설치 금지)
- 스캐폴딩: `scripts/scaffold_project.py`로 표준 폴더 구조 자동 생성

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/folder-structure.md` | 프로젝트 구조 설계 시 (항상) |
| `references/README-template.md` | README.md 작성 시 |
| `references/naming.md` | Python 네이밍 컨벤션 확인 시 |
| `references/docstring.md` | 독스트링 작성 시 |
| `references/error-handling.md` | 에러 처리 구현 시 |
| `references/code-explanation.md` | 코드 설명 및 워크플로우 섹션 작성 시 |
| `references/dependencies.md` | requirements.txt 작성 시 |
| `references/terminal-output.md` | CLI 스크립트의 print 문 작성 시 |

## 스크립트

- `scripts/scaffold_project.py` — 표준 챕터 프로젝트 폴더 구조 자동 생성
