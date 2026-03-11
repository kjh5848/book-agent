"""문서 청킹(분할) 모듈.

긴 문서를 검색 가능한 작은 단위로 분할합니다.
고정 크기 청킹(FixedSizeChunker)과 의미 단위 청킹(SemanticChunker) 두 가지 전략을 제공합니다.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """단일 청크 데이터 클래스.

    Attributes:
        text: 청크 텍스트 내용
        index: 문서 내 청크 순서 (0부터 시작)
        source: 원본 파일명
        strategy: 사용된 청킹 전략 ("fixed" 또는 "semantic")
        char_start: 원본 문서 내 시작 문자 위치
        char_end: 원본 문서 내 끝 문자 위치
    """

    text: str
    index: int
    source: str
    strategy: str
    char_start: int = 0
    char_end: int = 0
    metadata: dict = field(default_factory=dict)


class FixedSizeChunker:
    """고정 크기 청킹 클래스.

    문서를 일정한 문자 수 단위로 분할하며, 인접 청크 사이에 오버랩을 적용합니다.
    구현이 단순하고 예측 가능하지만, 문장 중간에서 잘릴 수 있습니다.

    Attributes:
        chunk_size: 각 청크의 최대 문자 수
        overlap: 인접 청크 간 겹치는 문자 수 (문맥 단절 방지)
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        """FixedSizeChunker를 초기화합니다.

        Args:
            chunk_size: 각 청크의 최대 문자 수 (기본값: 500)
            overlap: 인접 청크 간 겹치는 문자 수 (기본값: 50)

        Raises:
            ValueError: chunk_size가 overlap보다 작거나 같을 경우
        """

        if chunk_size <= overlap:
            raise ValueError(
                f"chunk_size({chunk_size})는 overlap({overlap})보다 커야 합니다.\n"
                "예: chunk_size=500, overlap=50"
            )
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str, source: str = "unknown") -> list[Chunk]:
        """텍스트를 고정 크기 청크로 분할합니다.

        Args:
            text: 분할할 텍스트 문자열
            source: 원본 파일명 (메타데이터용)

        Returns:
            Chunk 객체 리스트. 텍스트가 비어있으면 빈 리스트를 반환합니다.
        """

        # --- Input ---
        if not text or not text.strip():
            return []

        # --- Process ---
        chunks: list[Chunk] = []
        step = self.chunk_size - self.overlap
        start = 0
        index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        index=index,
                        source=source,
                        strategy="fixed",
                        char_start=start,
                        char_end=end,
                    )
                )
                index += 1

            start += step

        # --- Output ---
        return chunks


class SemanticChunker:
    """의미 단위(문단 기반) 청킹 클래스.

    빈 줄을 기준으로 문단을 분리하고, 최대 크기를 초과하면 문단을 병합하지 않습니다.
    문맥이 자연스럽게 보존되지만, 청크 크기가 일정하지 않을 수 있습니다.

    Attributes:
        max_chunk_size: 단일 청크의 최대 문자 수
        min_chunk_size: 단일 청크의 최소 문자 수 (너무 짧은 청크 제거용)
    """

    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 50) -> None:
        """SemanticChunker를 초기화합니다.

        Args:
            max_chunk_size: 단일 청크의 최대 문자 수 (기본값: 800)
            min_chunk_size: 단일 청크의 최소 문자 수 (기본값: 50)
        """

        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """텍스트를 문단 단위로 분리합니다.

        빈 줄(2개 이상의 연속 줄바꿈) 또는 섹션 제목 패턴(숫자.숫자)을 기준으로 분리합니다.

        Args:
            text: 분리할 원본 텍스트

        Returns:
            문단 문자열 리스트
        """

        # --- Input / Process ---
        # 연속된 빈 줄을 구분자로 분리
        paragraphs = re.split(r"\n\s*\n", text)

        # 너무 짧은 문단 필터링
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # --- Output ---
        return paragraphs

    def split(self, text: str, source: str = "unknown") -> list[Chunk]:
        """텍스트를 의미 단위(문단) 기반 청크로 분할합니다.

        문단이 max_chunk_size를 초과하면 문장 단위로 추가 분할합니다.
        min_chunk_size 미만의 청크는 이전 청크에 합쳐집니다.

        Args:
            text: 분할할 텍스트 문자열
            source: 원본 파일명 (메타데이터용)

        Returns:
            Chunk 객체 리스트. 텍스트가 비어있으면 빈 리스트를 반환합니다.
        """

        # --- Input ---
        if not text or not text.strip():
            return []

        # --- Process ---
        paragraphs = self._split_into_paragraphs(text)
        chunks: list[Chunk] = []
        current_buffer = ""
        index = 0
        char_pos = 0

        for para in paragraphs:
            # 단일 문단이 max_chunk_size 초과 시 문장 단위로 분리
            if len(para) > self.max_chunk_size:
                # 현재 버퍼 저장
                if current_buffer and len(current_buffer) >= self.min_chunk_size:
                    chunks.append(
                        Chunk(
                            text=current_buffer.strip(),
                            index=index,
                            source=source,
                            strategy="semantic",
                            char_start=char_pos,
                            char_end=char_pos + len(current_buffer),
                        )
                    )
                    index += 1
                    char_pos += len(current_buffer)
                    current_buffer = ""

                # 문장 단위 분리
                sentences = re.split(r"(?<=[.!?。])\s+", para)
                sentence_buffer = ""
                for sentence in sentences:
                    if len(sentence_buffer) + len(sentence) > self.max_chunk_size:
                        if sentence_buffer and len(sentence_buffer) >= self.min_chunk_size:
                            chunks.append(
                                Chunk(
                                    text=sentence_buffer.strip(),
                                    index=index,
                                    source=source,
                                    strategy="semantic",
                                    char_start=char_pos,
                                    char_end=char_pos + len(sentence_buffer),
                                )
                            )
                            index += 1
                            char_pos += len(sentence_buffer)
                        sentence_buffer = sentence + " "
                    else:
                        sentence_buffer += sentence + " "

                if sentence_buffer.strip():
                    current_buffer = sentence_buffer
            else:
                # 버퍼 + 현재 문단이 max_chunk_size 초과 시 버퍼 먼저 저장
                if len(current_buffer) + len(para) + 2 > self.max_chunk_size:
                    if current_buffer and len(current_buffer) >= self.min_chunk_size:
                        chunks.append(
                            Chunk(
                                text=current_buffer.strip(),
                                index=index,
                                source=source,
                                strategy="semantic",
                                char_start=char_pos,
                                char_end=char_pos + len(current_buffer),
                            )
                        )
                        index += 1
                        char_pos += len(current_buffer)
                    current_buffer = para + "\n\n"
                else:
                    current_buffer += para + "\n\n"

        # 마지막 버퍼 저장
        if current_buffer and len(current_buffer.strip()) >= self.min_chunk_size:
            chunks.append(
                Chunk(
                    text=current_buffer.strip(),
                    index=index,
                    source=source,
                    strategy="semantic",
                    char_start=char_pos,
                    char_end=char_pos + len(current_buffer),
                )
            )

        # --- Output ---
        return chunks


def chunk_document(
    text: str,
    source: str = "unknown",
    strategy: str = "fixed",
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """문서 텍스트를 지정한 전략으로 청킹합니다.

    Args:
        text: 분할할 텍스트 문자열
        source: 원본 파일명 (메타데이터용)
        strategy: 청킹 전략. "fixed" 또는 "semantic" (기본값: "fixed")
        chunk_size: FixedSizeChunker의 청크 크기 (strategy="fixed"일 때 사용)
        overlap: FixedSizeChunker의 오버랩 크기 (strategy="fixed"일 때 사용)

    Returns:
        Chunk 객체 리스트

    Raises:
        ValueError: 지원하지 않는 strategy 값이 전달된 경우
    """

    # --- Input ---
    if strategy not in ("fixed", "semantic"):
        raise ValueError(
            f"지원하지 않는 청킹 전략: '{strategy}'\n"
            "사용 가능한 전략: 'fixed', 'semantic'"
        )

    # --- Process ---
    if strategy == "fixed":
        chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
    else:
        chunker = SemanticChunker(max_chunk_size=chunk_size)

    chunks = chunker.split(text, source=source)

    # --- Output ---
    return chunks


def compare_strategies(text: str, source: str = "unknown") -> None:
    """두 청킹 전략의 결과를 비교 출력합니다.

    같은 텍스트에 Fixed-size와 Semantic 전략을 각각 적용하고
    청크 수, 평균 크기, 최대/최소 크기를 비교합니다.

    Args:
        text: 비교에 사용할 텍스트
        source: 원본 파일명 (표시용)
    """

    # --- Input ---
    if not text or not text.strip():
        print("비교할 텍스트가 없습니다.")
        return

    # --- Process ---
    fixed_chunks = chunk_document(text, source=source, strategy="fixed", chunk_size=500, overlap=50)
    semantic_chunks = chunk_document(text, source=source, strategy="semantic", chunk_size=500)

    def stats(chunks: list[Chunk]) -> dict[str, float]:
        """청크 통계를 계산합니다."""
        sizes = [len(c.text) for c in chunks]
        if not sizes:
            return {"count": 0, "avg": 0, "max": 0, "min": 0}
        return {
            "count": len(sizes),
            "avg": sum(sizes) / len(sizes),
            "max": max(sizes),
            "min": min(sizes),
        }

    fixed_stats = stats(fixed_chunks)
    semantic_stats = stats(semantic_chunks)

    # --- Output ---
    print(f"\n{'=' * 50}")
    print(f"청킹 전략 비교: {source}")
    print(f"{'=' * 50}")
    print(f"{'항목':<15} {'Fixed-size':>15} {'Semantic':>15}")
    print(f"{'-' * 45}")
    print(f"{'청크 수':<15} {fixed_stats['count']:>15.0f} {semantic_stats['count']:>15.0f}")
    print(f"{'평균 크기(자)':<15} {fixed_stats['avg']:>15.1f} {semantic_stats['avg']:>15.1f}")
    print(f"{'최대 크기(자)':<15} {fixed_stats['max']:>15.0f} {semantic_stats['max']:>15.0f}")
    print(f"{'최소 크기(자)':<15} {fixed_stats['min']:>15.0f} {semantic_stats['min']:>15.0f}")
    print(f"{'=' * 50}")

    print("\n[Fixed-size] 첫 번째 청크 미리보기:")
    if fixed_chunks:
        print(f"  {fixed_chunks[0].text[:150]}...")

    print("\n[Semantic] 첫 번째 청크 미리보기:")
    if semantic_chunks:
        print(f"  {semantic_chunks[0].text[:150]}...")


if __name__ == "__main__":
    from pathlib import Path

    base_dir = Path(__file__).parent.parent
    sample_file = base_dir / "data" / "sample_docs" / "leave_rules.txt"

    if not sample_file.exists():
        print(f"샘플 파일이 없습니다: {sample_file}")
    else:
        text = sample_file.read_text(encoding="utf-8")
        print(f"원본 텍스트 길이: {len(text)}자")
        compare_strategies(text, source=sample_file.name)
