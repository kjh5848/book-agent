"""
XLSX 파일을 파싱하여 Markdown으로 변환하고 data/markdown/에 저장하는 스크립트.

실행 방법:
    python src/extract_xlsx.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import extract_from_xlsx

# 기본 경로
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "data" / "docs"
MARKDOWN_DIR = BASE_DIR / "data" / "markdown"


def save_as_markdown(result: dict, output_dir: Path) -> Path:
    """추출 결과를 Markdown 파일로 저장합니다.

    Args:
        result: extractor.extract_from_xlsx() 반환값
        output_dir: Markdown 파일 저장 디렉토리

    Returns:
        저장된 Markdown 파일 경로
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(result["file_name"]).stem
    md_path = output_dir / f"{stem}.md"

    lines = []
    lines.append(f"# {result['file_name']}\n")
    lines.append(f"- 파일 형식: {result['file_type']}")
    lines.append(f"- 총 시트: {len(result['pages'])}개")
    lines.append(f"- 추출 글자 수: {len(result['full_text'])}자")
    lines.append(f"- 원본 경로: `{result['source_path']}`\n")
    lines.append("---\n")

    for page in result["pages"]:
        text = page["text"]
        if not text:
            continue
        lines.append(f"## 시트 {page['page']}\n")
        lines.append(text)
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    """data/docs/에서 모든 XLSX를 찾아 파싱하고 Markdown으로 저장합니다."""
    print("\n" + "=" * 60)
    print("XLSX 파싱 → Markdown 변환")
    print("=" * 60)

    # XLSX 파일 수집
    xlsx_files = sorted(DOCS_DIR.rglob("*.xlsx"))
    if not xlsx_files:
        print(f"XLSX 파일이 없습니다: {DOCS_DIR}")
        sys.exit(1)

    print(f"문서 디렉토리: {DOCS_DIR}")
    print(f"XLSX 파일: {len(xlsx_files)}개\n")

    start_time = time.time()
    results = []

    for file_path in xlsx_files:
        print(f"  추출 중: {file_path.name} ...", end=" ", flush=True)
        result = extract_from_xlsx(file_path)
        md_path = save_as_markdown(result, MARKDOWN_DIR)
        text_len = len(result["full_text"])
        sheet_count = len(result["pages"])
        print(f"완료 ({sheet_count}시트, {text_len}자) → {md_path.name}")
        results.append(result)

    elapsed = time.time() - start_time

    # 결과 요약
    print(f"\nXLSX 파싱 완료: {len(results)}개 파일 ({elapsed:.1f}초)")
    print(f"Markdown 저장 위치: {MARKDOWN_DIR}/")
    print("\n[저장된 파일]")
    for r in results:
        stem = Path(r["file_name"]).stem
        print(f"  {stem}.md ({len(r['full_text'])}자)")


if __name__ == "__main__":
    main()
