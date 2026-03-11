#!/usr/bin/env python3
"""
merge_book.py — 챕터 원고를 하나의 book_final.md로 통합

사용법:
    python scripts/merge_book.py 수동
    python scripts/merge_book.py 자동
    python scripts/merge_book.py 수동 --output 내책.md
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def load_progress(project_dir: Path) -> dict:
    progress_path = project_dir / "progress.json"
    if not progress_path.exists():
        raise FileNotFoundError(f"progress.json 없음: {progress_path}")
    with open(progress_path, encoding="utf-8") as f:
        return json.load(f)

def make_title_page(progress: dict) -> str:
    title = progress.get("book_title", "제목 없음")
    concept = progress.get("writing_concept", "")
    concept_label = {
        "storytelling": "스토리텔링 버전",
        "practical-guide": "실무 지침서",
        "recipe": "레시피/쿡북",
        "project-buildup": "프로젝트 빌드업",
        "comparison": "비교/대조",
        "workbook": "워크북",
    }.get(concept, "")

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {title}",
        "",
    ]
    if concept_label:
        lines += [f"> **집필 컨셉**: {concept_label}", ""]

    persona = progress.get("story_persona", "")
    if persona:
        lines += [f"> **주인공**: {persona}", ""]

    lines += [
        f"> 생성일시: {generated_at}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)

def load_toc(project_dir: Path) -> str:
    toc_path = project_dir / "outline" / "TOC.md"
    if not toc_path.exists():
        return ""
    with open(toc_path, encoding="utf-8") as f:
        content = f.read().strip()
    return f"## 목차\n\n{content}\n\n---\n\n"

def load_chapters(project_dir: Path, progress: dict) -> list[tuple[int, str, str]]:
    """(챕터번호, 제목, 내용) 목록 반환"""
    chapters = []
    for ch in sorted(progress.get("chapters", []), key=lambda x: x["number"]):
        if ch.get("status") != "done":
            print(f"  ⚠️  CH{ch['number']:02d} 미완료 — 건너뜀")
            continue
        file_rel = ch.get("file", "")
        if not file_rel:
            print(f"  ⚠️  CH{ch['number']:02d} 파일 경로 없음 — 건너뜀")
            continue
        chapter_path = project_dir / file_rel
        if not chapter_path.exists():
            # chapters/ 하위 직접 탐색
            name = Path(file_rel).name
            alt = project_dir / "chapters" / name
            if alt.exists():
                chapter_path = alt
            else:
                print(f"  ⚠️  CH{ch['number']:02d} 파일 없음: {chapter_path}")
                continue
        with open(chapter_path, encoding="utf-8") as f:
            content = f.read().strip()
        chapters.append((ch["number"], ch["title"], content))
        print(f"  ✅  CH{ch['number']:02d} {ch['title']} ({len(content.splitlines())}줄)")
    return chapters

def merge(project_dir: Path, output_path: Path):
    print(f"\n📚 통합 시작: {project_dir.name}")

    progress = load_progress(project_dir)
    book_title = progress.get("book_title", "book")

    parts = []

    # 표지
    parts.append(make_title_page(progress))

    # 목차
    toc = load_toc(project_dir)
    if toc:
        parts.append(toc)
        print("  ✅  TOC.md 포함")
    else:
        print("  ⚠️  TOC.md 없음 — 건너뜀")

    # 챕터
    chapters = load_chapters(project_dir, progress)
    if not chapters:
        print("  ❌ 완료된 챕터가 없습니다.")
        sys.exit(1)

    for num, title, content in chapters:
        parts.append(content)
        parts.append("\n\n---\n\n")  # 챕터 구분선

    # 마지막 구분선 제거
    if parts and parts[-1].strip() == "---":
        parts.pop()

    final = "\n\n".join(p.rstrip() for p in parts if p.strip())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final)

    total_lines = len(final.splitlines())
    size_kb = len(final.encode("utf-8")) / 1024

    print(f"\n✅ 통합 완료!")
    print(f"   출력: {output_path}")
    print(f"   총 {total_lines}줄 / {size_kb:.1f} KB / {len(chapters)}챕터")


if __name__ == "__main__":
    import argparse

    ROOT = Path(__file__).parent.parent  # 집필에이전트-claude/

    parser = argparse.ArgumentParser(description="챕터 원고를 하나의 book_final.md로 통합")
    parser.add_argument("mode", choices=["수동", "자동"], help="수동 또는 자동 모드 폴더")
    parser.add_argument("--output", default="", help="출력 파일 경로 (기본: {mode}/book_final.md)")
    args = parser.parse_args()

    project_dir = ROOT / args.mode
    if not project_dir.exists():
        print(f"❌ 폴더 없음: {project_dir}")
        sys.exit(1)

    output_path = Path(args.output) if args.output else project_dir / "book_final.md"

    merge(project_dir, output_path)
