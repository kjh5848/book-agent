# merge_book.py
<!-- 챕터별 원고를 하나의 book_final.md로 통합하는 스크립트 -->

Reads `progress.json` for chapter order and metadata, then merges all chapter `.md` files into a single `book_final.md` with a title page and TOC.

## Prerequisites
<!-- 사전 환경 설정 -->

### 1. Python — no extra packages required
<!-- Python 표준 라이브러리만 사용 (별도 설치 불필요) -->

`merge_book.py` uses only the Python standard library (`json`, `pathlib`, `datetime`). No `pip install` needed.

```bash
python3 --version   # 3.8 or higher required
```

### 2. Required files before running
<!-- 실행 전 필요한 파일 체크리스트 -->

```bash
# Check all required files exist
ls {mode}/progress.json          # must have status: "done"
ls {mode}/outline/TOC.md         # chapter table of contents
ls {mode}/chapters/CH*.md        # all chapter manuscripts
```

`progress.json` must have each chapter's `file` field filled in:

```json
{
  "status": "done",
  "chapters": [
    { "number": "CH01", "file": "chapters/CH01_제목.md", "status": "done" },
    ...
  ]
}
```

## Usage
<!-- 기본 사용법 -->

```bash
# 수동 모드
python3 {project_root}/.claude/skills/planning/scripts/merge_book.py 수동

# 자동 모드
python3 {project_root}/.claude/skills/planning/scripts/merge_book.py 자동

# 출력 파일명 지정
python3 {project_root}/.claude/skills/planning/scripts/merge_book.py 수동 --output 내책최종.md
```

## Parameters
<!-- 파라미터 -->

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | ✅ | `수동` or `자동` — determines which project directory to use |
| `--output` | — | Custom output filename (default: `book_final.md`) |

## Output Structure
<!-- 생성되는 book_final.md 구조 -->

```
{mode}/book_final.md

─ Title page (book title, writing_concept label, story_persona, timestamp)
─ TOC (outline/TOC.md contents)
─ --- separator
─ CH01 full content
─ --- separator
─ CH02 full content
  ...
─ CH10 full content
```

## Requirements
<!-- 실행 전 필요 조건 -->

- `{mode}/progress.json` must exist with `status: done` and chapter file paths filled in
- `{mode}/outline/TOC.md` must exist
- All `chapters/CH{N}_*.md` files listed in `progress.json` must exist

## When to run
<!-- 실행 시점 -->

Run at **Phase 5** after all chapters are written and verified:

```bash
# Phase 5 final merge
python3 .claude/skills/planning/scripts/merge_book.py 수동
# Output: 수동/book_final.md
```
