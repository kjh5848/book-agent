"""문서 전처리 모듈.

원본 텍스트에서 노이즈를 제거하고 한국어 텍스트를 정규화합니다.
머리글/바닥글 패턴 제거, 특수문자 처리, 공백 정리를 담당합니다.
"""

import re
import sys
from pathlib import Path


# 제거할 헤더/푸터 패턴 (정규식)
HEADER_FOOTER_PATTERNS: list[str] = [
    r"={40,}",                          # === 구분선 (40자 이상)
    r"-{40,}",                          # --- 구분선 (40자 이상)
    r"\[문서\s*끝\].*",                  # [문서 끝] 라인
    r"\[목차\]",                          # [목차] 라인
    r"페이지\s*\d+\s*/\s*\d+",          # 페이지 N/M 패턴
    r"버전:\s*v[\d.]+\s*\|.*",          # 버전 메타 라인
    r"문서\s*ID:\s*\S+",                # 문서 ID 라인
    r"최종\s*승인:.*",                   # 최종 승인 라인
    r"다음\s*개정\s*예정:.*",            # 개정 예정 라인
]

# 특수문자 대체 규칙 (원본 → 대체)
SPECIAL_CHAR_REPLACEMENTS: dict[str, str] = {
    "\u2013": "-",   # en dash → 하이픈
    "\u2014": "-",   # em dash → 하이픈
    "\u2018": "'",   # 왼쪽 작은따옴표
    "\u2019": "'",   # 오른쪽 작은따옴표
    "\u201c": '"',   # 왼쪽 큰따옴표
    "\u201d": '"',   # 오른쪽 큰따옴표
    "\u00b7": "·",   # 중간점 유니코드 → 가운뎃점
}


def remove_header_footer(text: str) -> str:
    """머리글/바닥글 패턴을 감지하여 해당 라인을 제거합니다.

    Args:
        text: 원본 텍스트 문자열

    Returns:
        머리글/바닥글이 제거된 텍스트
    """

    # --- Input ---
    lines = text.splitlines()
    cleaned_lines: list[str] = []

    # --- Process ---
    for line in lines:
        stripped = line.strip()
        is_noise = False

        for pattern in HEADER_FOOTER_PATTERNS:
            if re.search(pattern, stripped):
                is_noise = True
                break

        if not is_noise:
            cleaned_lines.append(line)

    # --- Output ---
    return "\n".join(cleaned_lines)


def replace_special_chars(text: str) -> str:
    """특수문자를 표준 문자로 교체합니다.

    Args:
        text: 처리할 텍스트 문자열

    Returns:
        특수문자가 교체된 텍스트
    """

    # --- Input / Process ---
    result = text
    for original, replacement in SPECIAL_CHAR_REPLACEMENTS.items():
        result = result.replace(original, replacement)

    # --- Output ---
    return result


def normalize_whitespace(text: str) -> str:
    """과도한 공백과 빈 줄을 정리합니다.

    - 줄 끝 공백 제거
    - 3줄 이상 연속 빈 줄을 2줄로 압축
    - 탭 문자를 공백 4칸으로 변환

    Args:
        text: 처리할 텍스트 문자열

    Returns:
        공백이 정규화된 텍스트
    """

    # --- Input ---
    lines = text.splitlines()

    # --- Process ---
    # 탭 → 공백 4칸, 줄 끝 공백 제거
    lines = [line.replace("\t", "    ").rstrip() for line in lines]

    # 연속 빈 줄 압축 (3줄 이상 → 2줄로)
    result_lines: list[str] = []
    blank_count = 0

    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                result_lines.append(line)
        else:
            blank_count = 0
            result_lines.append(line)

    # --- Output ---
    return "\n".join(result_lines)


def remove_repeated_separators(text: str) -> str:
    """반복되는 구분선을 단일 빈 줄로 변환합니다.

    PDF 변환 과정에서 생기는 과도한 구분선 패턴을 정리합니다.

    Args:
        text: 처리할 텍스트 문자열

    Returns:
        구분선이 정리된 텍스트
    """

    # --- Input / Process ---
    # 짧은 구분선(=, -, *, _ 등 20자 이하)만 보존, 긴 구분선은 제거
    lines = text.splitlines()
    cleaned_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        # 순수 구분선 문자로만 구성된 라인 처리
        if re.fullmatch(r"[=\-\*_]{10,}", stripped):
            # 10자 이상 구분선은 삭제 (이미 remove_header_footer에서 40자 이상 처리)
            continue
        cleaned_lines.append(line)

    # --- Output ---
    return "\n".join(cleaned_lines)


def preprocess(text: str) -> str:
    """텍스트 전처리 전체 파이프라인을 순서대로 실행합니다.

    처리 순서:
    1. 머리글/바닥글 제거
    2. 특수문자 교체
    3. 반복 구분선 제거
    4. 공백 정규화

    Args:
        text: 원본 텍스트 문자열

    Returns:
        전처리가 완료된 정제 텍스트

    Raises:
        ValueError: 텍스트가 비어있을 경우
    """

    # --- Input ---
    if not text or not text.strip():
        raise ValueError("텍스트가 비어있습니다. 유효한 문서 내용을 입력하십시오.")

    original_length = len(text)

    # --- Process ---
    result = remove_header_footer(text)
    result = replace_special_chars(result)
    result = remove_repeated_separators(result)
    result = normalize_whitespace(result)
    result = result.strip()

    cleaned_length = len(result)
    reduction_rate = (1 - cleaned_length / original_length) * 100

    print(f"  전처리 완료: {original_length}자 → {cleaned_length}자 ({reduction_rate:.1f}% 감소)")

    # --- Output ---
    return result


if __name__ == "__main__":
    # 독립 실행 시: sample_docs 디렉토리의 첫 번째 .txt 파일 전처리
    base_dir = Path(__file__).parent.parent
    sample_dir = base_dir / "data" / "sample_docs"

    txt_files = list(sample_dir.glob("*.txt"))

    if not txt_files:
        print(f"오류: {sample_dir} 에서 .txt 파일을 찾을 수 없습니다.")
        sys.exit(1)

    target_file = txt_files[0]
    print(f"전처리 대상: {target_file.name}")

    with open(target_file, encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = preprocess(raw_text)

    # 결과 미리보기 (앞 500자)
    print("\n--- 전처리 결과 미리보기 (앞 500자) ---")
    print(cleaned_text[:500])
    print("...")
