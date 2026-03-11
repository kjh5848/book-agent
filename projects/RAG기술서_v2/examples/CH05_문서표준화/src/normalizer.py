"""문서 정규화 모듈.

전처리된 텍스트를 구조화된 Markdown 형식으로 변환합니다.
섹션 헤더를 자동 감지하여 계층적 Markdown 구조를 생성합니다.
"""

import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 출력 디렉토리 환경 변수 (기본값: outputs/markdown)
OUTPUT_DIR = os.getenv("NORMALIZED_OUTPUT_DIR", "outputs/markdown")

# 섹션 헤더 감지 패턴 (우선순위 순)
HEADER_PATTERNS: list[tuple[int, str]] = [
    # (헤더 레벨, 정규식 패턴)
    (1, r"^(\d+)\.\s+[가-힣A-Za-z]"),           # "1. 제목" 형식
    (2, r"^(\d+\.\d+)\s+[가-힣A-Za-z]"),         # "1.1 제목" 형식
    (3, r"^(\d+\.\d+\.\d+)\s+[가-힣A-Za-z]"),    # "1.1.1 제목" 형식
]

# 목록 항목 감지 패턴
LIST_PATTERNS: list[str] = [
    r"^[-*•]\s+",           # - 또는 * 또는 • 로 시작하는 항목
    r"^\d+단계:\s+",        # "1단계:" 형식
    r"^단계\s+\d+:\s+",    # "단계 1:" 형식
]


def detect_header_level(line: str) -> int:
    """라인이 섹션 헤더인지 감지하고 Markdown 헤더 레벨을 반환합니다.

    Args:
        line: 검사할 텍스트 라인

    Returns:
        Markdown 헤더 레벨 (1~3). 헤더가 아니면 0 반환.
    """

    # --- Input ---
    stripped = line.strip()

    # --- Process ---
    for level, pattern in HEADER_PATTERNS:
        if re.match(pattern, stripped):
            return level

    # --- Output ---
    return 0


def is_list_item(line: str) -> bool:
    """라인이 목록 항목인지 감지합니다.

    Args:
        line: 검사할 텍스트 라인

    Returns:
        목록 항목이면 True, 아니면 False
    """

    # --- Input / Process ---
    stripped = line.strip()
    for pattern in LIST_PATTERNS:
        if re.match(pattern, stripped):
            return True

    # --- Output ---
    return False


def convert_table_to_markdown(lines: list[str], start_idx: int) -> tuple[str, int]:
    """파이프(|) 구분자를 포함한 표 블록을 Markdown 표로 변환합니다.

    Args:
        lines: 전체 텍스트 라인 리스트
        start_idx: 표 시작 라인 인덱스

    Returns:
        (변환된 Markdown 표 문자열, 다음 처리 시작 인덱스) 튜플
    """

    # --- Input ---
    table_lines: list[str] = []
    idx = start_idx

    # --- Process ---
    while idx < len(lines):
        line = lines[idx].strip()
        if "|" in line:
            table_lines.append(line)
            idx += 1
        else:
            break

    if len(table_lines) < 2:
        # 표가 충분하지 않으면 원본 반환
        return "\n".join(table_lines), idx

    # 첫 번째 행을 헤더로, 나머지를 데이터로 처리
    header_line = table_lines[0]
    # 헤더 아래 구분선 자동 삽입
    cols = len(header_line.split("|")) - 2  # 양쪽 빈 | 제외
    separator = "| " + " | ".join(["---"] * max(cols, 1)) + " |"

    result_lines = [header_line, separator] + table_lines[1:]

    # --- Output ---
    return "\n".join(result_lines), idx


def normalize_to_markdown(text: str, source_file_name: str = "") -> str:
    """전처리된 텍스트를 Markdown 형식으로 변환합니다.

    변환 규칙:
    - 숫자 번호 섹션 → Markdown 헤더 (#, ##, ###)
    - 파이프 포함 라인 → Markdown 표
    - 기존 목록 항목 유지

    Args:
        text: 전처리 완료된 텍스트 문자열
        source_file_name: 원본 파일명 (문서 상단 제목 생성용)

    Returns:
        Markdown 형식으로 변환된 텍스트
    """

    # --- Input ---
    lines = text.splitlines()
    result_lines: list[str] = []

    # 문서 상단에 파일명 기반 제목 삽입
    if source_file_name:
        doc_title = Path(source_file_name).stem.replace("_", " ")
        result_lines.append(f"# {doc_title}")
        result_lines.append("")

    # --- Process ---
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        # 빈 줄 그대로 유지
        if not stripped:
            result_lines.append("")
            idx += 1
            continue

        # 표 감지 (파이프 문자 포함)
        if "|" in stripped and stripped.startswith("|"):
            table_md, idx = convert_table_to_markdown(lines, idx)
            result_lines.append(table_md)
            result_lines.append("")
            continue

        # 섹션 헤더 감지
        header_level = detect_header_level(stripped)
        if header_level > 0:
            prefix = "#" * (header_level + 1)  # 파일명이 H1이므로 +1
            result_lines.append(f"{prefix} {stripped}")
            idx += 1
            continue

        # 일반 텍스트 (들여쓰기 기반 목록 처리)
        if is_list_item(stripped):
            # 기존 하이픈/별표 목록을 Markdown 목록으로 표준화
            normalized_item = re.sub(r"^[-*•]\s+", "- ", stripped)
            # "N단계:" 또는 "단계 N:" 형식을 번호 목록으로
            normalized_item = re.sub(r"^(\d+)단계:\s+", r"\1. ", normalized_item)
            normalized_item = re.sub(r"^단계\s+(\d+):\s+", r"\1. ", normalized_item)
            result_lines.append(normalized_item)
        else:
            result_lines.append(stripped)

        idx += 1

    # 연속 빈 줄 압축 (최대 1줄)
    final_lines: list[str] = []
    prev_blank = False
    for line in result_lines:
        if line == "":
            if not prev_blank:
                final_lines.append(line)
            prev_blank = True
        else:
            final_lines.append(line)
            prev_blank = False

    # --- Output ---
    return "\n".join(final_lines).strip()


def save_normalized_file(
    markdown_text: str,
    source_file_name: str,
    output_dir: str,
) -> str:
    """정규화된 Markdown 텍스트를 파일로 저장합니다.

    저장 경로: {output_dir}/{원본파일명}_normalized.md

    Args:
        markdown_text: 저장할 Markdown 텍스트
        source_file_name: 원본 파일명 (출력 파일명 생성 기준)
        output_dir: 저장할 디렉토리 경로

    Returns:
        저장된 파일의 절대 경로
    """

    # --- Input ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    stem = Path(source_file_name).stem
    output_file = output_path / f"{stem}_normalized.md"

    # --- Process ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_text)
        f.write("\n")  # 파일 끝 개행 보장

    print(f"  저장 완료: {output_file}")

    # --- Output ---
    return str(output_file.absolute())


if __name__ == "__main__":
    # 독립 실행 시: sample_docs의 모든 .txt 파일을 정규화하여 outputs/markdown에 저장
    import os
    from preprocessor import preprocess

    base_dir = Path(__file__).parent.parent
    sample_dir = base_dir / "data" / "sample_docs"
    output_dir = base_dir / OUTPUT_DIR

    txt_files = list(sample_dir.glob("*.txt"))

    if not txt_files:
        print(f"오류: {sample_dir} 에서 .txt 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"정규화 대상: {len(txt_files)}개 파일")
    print(f"출력 경로: {output_dir}")
    print()

    for txt_file in sorted(txt_files):
        print(f"처리 중: {txt_file.name}")

        with open(txt_file, encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = preprocess(raw_text)
        markdown = normalize_to_markdown(cleaned, txt_file.name)
        save_normalized_file(markdown, txt_file.name, str(output_dir))

    print(f"\n정규화 완료: {len(txt_files)}개 파일 처리")
