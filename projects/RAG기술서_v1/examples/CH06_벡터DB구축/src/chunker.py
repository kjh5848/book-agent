"""
텍스트 청킹 모듈.

추출된 페이지 텍스트를 벡터 검색에 적합한 크기의 청크로 분할합니다.
두 가지 전략을 제공합니다:
    1. Markdown 헤더 청킹: ## 헤더 기준 의미 단위 분할 (Vision LLM 결과에 최적)
    2. Fixed-size 청킹:    고정 크기 슬라이딩 윈도우 방식 (규칙 기반 추출 결과에 최적)
"""

import re
from pathlib import Path


def markdown_chunk(
    markdown_text: str,
    source: str,
    max_chunk_size: int = 500,
) -> list[dict]:
    """Markdown 헤더(##) 기준으로 텍스트를 의미 단위로 청킹합니다.

    ## 헤더를 섹션 경계로 삼아 분할합니다. 섹션이 max_chunk_size를 초과하면
    추가로 고정 크기로 분할합니다. 메타데이터에 section_title과 department를 포함합니다.

    Args:
        markdown_text: Vision LLM이 생성한 Markdown 형식 텍스트.
        source: 원본 파일명 (예: HR_취업규칙_v1.0.pdf).
        max_chunk_size: 청크당 최대 문자 수. 기본값은 500.

    Returns:
        청크 딕셔너리의 리스트. 각 딕셔너리 구조:
            {
                "chunk_id": str,   # "{source}_mk_chunk_{index}"
                "text": str,       # 청크 텍스트
                "metadata": dict,  # section_title, department, source, chunk_index 포함
            }

    Raises:
        ValueError: markdown_text가 비어 있을 때.
        ValueError: max_chunk_size가 1 미만일 때.
    """
    # --- Input ---
    if not markdown_text or not markdown_text.strip():
        raise ValueError(
            "markdown_text가 비어 있습니다. Vision LLM 추출 결과를 확인하십시오."
        )
    if max_chunk_size < 1:
        raise ValueError(
            f"max_chunk_size는 1 이상이어야 합니다. 현재 값: {max_chunk_size}"
        )

    # 파일명에서 부서 정보 추출
    from src.extractor import parse_filename_metadata
    metadata_from_filename = parse_filename_metadata(source)
    department = metadata_from_filename.get("department", "unknown")

    chunks: list[dict] = []
    chunk_index = 0

    # --- Process ---
    # ## 헤더를 기준으로 섹션 분리
    # 패턴: ## 또는 ### 로 시작하는 줄을 섹션 시작점으로 인식
    section_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(section_pattern.finditer(markdown_text))

    if not matches:
        # 헤더가 없으면 전체 텍스트를 고정 크기로 분할
        start = 0
        current_title = "본문"
        while start < len(markdown_text):
            chunk_text = markdown_text[start : start + max_chunk_size].strip()
            if chunk_text:
                chunk_id = f"{source}_mk_chunk_{chunk_index}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "source": source,
                            "section_title": current_title,
                            "department": department,
                            "chunk_index": chunk_index,
                        },
                    }
                )
                chunk_index += 1
            start += max_chunk_size
        return chunks

    # 헤더 기준 섹션 추출
    sections: list[tuple[str, str]] = []

    # 첫 번째 헤더 이전 내용 (도입부)
    first_match_start = matches[0].start()
    if first_match_start > 0:
        intro_text = markdown_text[:first_match_start].strip()
        if intro_text:
            sections.append(("도입부", intro_text))

    # 각 헤더 ~ 다음 헤더까지 섹션으로 분리
    for i, match in enumerate(matches):
        section_title = match.group(2).strip()
        section_start = match.start()
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        section_text = markdown_text[section_start:section_end].strip()
        sections.append((section_title, section_text))

    # 섹션별 청킹: max_chunk_size 초과 시 추가 분할
    for section_title, section_text in sections:
        if not section_text:
            continue

        if len(section_text) <= max_chunk_size:
            chunk_id = f"{source}_mk_chunk_{chunk_index}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": section_text,
                    "metadata": {
                        "source": source,
                        "section_title": section_title,
                        "department": department,
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1
        else:
            # 섹션이 너무 길면 고정 크기로 추가 분할 (섹션 제목 유지)
            start = 0
            sub_index = 0
            while start < len(section_text):
                sub_text = section_text[start : start + max_chunk_size].strip()
                if sub_text:
                    sub_title = f"{section_title} (파트 {sub_index + 1})"
                    chunk_id = f"{source}_mk_chunk_{chunk_index}"
                    chunks.append(
                        {
                            "chunk_id": chunk_id,
                            "text": sub_text,
                            "metadata": {
                                "source": source,
                                "section_title": sub_title,
                                "department": department,
                                "chunk_index": chunk_index,
                            },
                        }
                    )
                    chunk_index += 1
                    sub_index += 1
                start += max_chunk_size

    # --- Output ---
    return chunks


def fixed_size_chunk(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """고정 크기 슬라이딩 윈도우 방식으로 텍스트를 청킹합니다.

    각 페이지의 텍스트를 이어붙인 전체 텍스트를 chunk_size 문자 단위로 잘라냅니다.
    인접 청크는 overlap 문자만큼 겹쳐 문맥 단절을 줄입니다.
    메타데이터에 source, page, chunk_index, department를 포함합니다.

    Args:
        pages: extractor 모듈이 반환한 페이지 딕셔너리 리스트.
               각 요소는 {"page": int, "text": str, "source": str} 형태여야 합니다.
        chunk_size: 청크당 최대 문자 수. 기본값은 500.
        overlap: 인접 청크 간 겹치는 문자 수. 기본값은 50.
                 overlap이 없으면 청크 경계에서 문장이 잘려 검색 품질이 저하됩니다.

    Returns:
        청크 딕셔너리의 리스트. 각 딕셔너리 구조:
            {
                "chunk_id": str,   # "{source}_fs_chunk_{index}"
                "text": str,       # 청크 텍스트
                "metadata": dict,  # source, page, chunk_index, department 포함
            }

    Raises:
        ValueError: pages 리스트가 비어 있을 때.
        ValueError: chunk_size가 overlap 이하일 때.
    """
    # --- Input ---
    if not pages:
        raise ValueError(
            "pages 리스트가 비어 있습니다. PDF 텍스트 추출 결과를 확인하십시오."
        )
    if chunk_size <= overlap:
        raise ValueError(
            f"chunk_size({chunk_size})는 overlap({overlap})보다 커야 합니다."
        )

    chunks: list[dict] = []

    # --- Process ---
    from itertools import groupby
    from src.extractor import parse_filename_metadata

    for source, page_group in groupby(pages, key=lambda p: p["source"]):
        page_list = list(page_group)

        # 파일명에서 부서 정보 추출
        meta = parse_filename_metadata(source)
        department = meta.get("department", "unknown")

        # 페이지 텍스트를 하나의 문자열로 합침
        full_text = "\n".join(p["text"] for p in page_list)

        # 페이지 위치 경계 매핑 (청크가 어느 페이지에 속하는지 추적)
        page_boundaries: list[tuple[int, int, int]] = []
        cursor = 0
        for page in page_list:
            start = cursor
            end = cursor + len(page["text"])
            page_boundaries.append((start, end, page["page"]))
            cursor = end + 1  # '\n' 구분자 1자

        def get_page_for_position(pos: int) -> int:
            """텍스트 내 절대 위치에 해당하는 페이지 번호를 반환합니다.

            Args:
                pos: 전체 텍스트 내 절대 문자 위치.

            Returns:
                해당 위치가 속하는 페이지 번호.
            """
            for seg_start, seg_end, page_num in page_boundaries:
                if seg_start <= pos <= seg_end:
                    return page_num
            return page_list[-1]["page"]

        # 슬라이딩 윈도우 청킹
        start = 0
        chunk_index = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end].strip()

            if chunk_text:
                page_num = get_page_for_position(start)
                chunk_id = f"{source}_fs_chunk_{chunk_index}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "source": source,
                            "page": page_num,
                            "chunk_index": chunk_index,
                            "department": department,
                        },
                    }
                )
                chunk_index += 1

            step = chunk_size - overlap
            start += step

    # --- Output ---
    return chunks


def compare_strategies(pages: list[dict], markdown_path: str) -> None:
    """Fixed-size 청킹과 Markdown 청킹 두 전략의 결과를 비교하여 출력합니다.

    동일한 원본 데이터를 두 전략으로 처리한 뒤 청크 수, 평균 길이,
    섹션 보존 여부를 표 형태로 출력합니다.

    Args:
        pages: extractor 모듈이 반환한 페이지 딕셔너리 리스트.
        markdown_path: Vision LLM이 생성한 Markdown 파일 경로.

    Returns:
        None. 비교 결과를 표준 출력으로 내보냅니다.
    """
    # --- Input ---
    if not pages:
        print("비교할 페이지 데이터가 없습니다.")
        return

    import os
    if not os.path.exists(markdown_path):
        print(f"Markdown 파일을 찾을 수 없습니다: {markdown_path}")
        print("Fixed-size 청킹 결과만 출력합니다.")
        fixed_chunks = fixed_size_chunk(pages)
        _print_single_stats("Fixed-size", fixed_chunks)
        return

    # --- Process ---
    # Fixed-size 청킹
    fixed_chunks = fixed_size_chunk(pages)

    # Markdown 청킹 (Markdown 파일 내용 사용)
    with open(markdown_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()
    source = Path(markdown_path).name.replace(".md", ".pdf")
    mk_chunks = markdown_chunk(markdown_text, source=source)

    def calc_stats(chunks: list[dict]) -> dict:
        """청크 리스트의 통계를 계산합니다.

        Args:
            chunks: 청크 딕셔너리 리스트.

        Returns:
            count, avg_len, has_section 키를 가진 통계 딕셔너리.
        """
        lengths = [len(c["text"]) for c in chunks]
        has_section = any("section_title" in c.get("metadata", {}) for c in chunks)
        return {
            "count": len(chunks),
            "avg_len": sum(lengths) / len(lengths) if lengths else 0,
            "has_section": has_section,
        }

    fixed_stats = calc_stats(fixed_chunks)
    mk_stats = calc_stats(mk_chunks)

    print("\n[청킹 전략 비교]")
    print("=" * 65)
    print(f"  {'항목':22s}  {'Fixed-size':>14}  {'Markdown 헤더':>14}")
    print("  " + "-" * 53)
    print(f"  {'청크 수':22s}  {fixed_stats['count']:>14,}  {mk_stats['count']:>14,}")
    print(f"  {'평균 길이 (문자)':22s}  {fixed_stats['avg_len']:>14.1f}  {mk_stats['avg_len']:>14.1f}")
    section_fixed = "X" if not fixed_stats["has_section"] else "O"
    section_mk = "O" if mk_stats["has_section"] else "X"
    print(f"  {'섹션 제목 보존':22s}  {section_fixed:>14}  {section_mk:>14}")
    print("=" * 65)

    # --- Output ---
    print("비교 완료.\n")


def _print_single_stats(strategy_name: str, chunks: list[dict]) -> None:
    """단일 전략의 청킹 통계를 화면에 출력합니다.

    Args:
        strategy_name: 전략 이름 문자열.
        chunks: 청크 딕셔너리 리스트.

    Returns:
        None.
    """
    lengths = [len(c["text"]) for c in chunks]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"\n[{strategy_name} 청킹 통계]")
    print(f"  청크 수: {len(chunks)}")
    print(f"  평균 길이: {avg_len:.1f}자")
