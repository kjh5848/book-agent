"""출처 표시(Source Citation) 시스템 모듈.

RAG 답변에 근거 문서와 유사도 점수를 함께 표시하여
기업 환경에서의 신뢰성을 확보합니다.
"""

import os
from pathlib import Path

# 제거 대상 문서 확장자 목록 (소문자)
DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".doc", ".xlsx", ".csv"}


def _normalize_source_name(source: str) -> str:
    """파일 경로에서 읽기 좋은 문서명을 추출합니다.

    문서 확장자(.pdf, .txt, .md 등)가 있으면 제거하고,
    언더스코어와 하이픈을 공백으로 변환합니다.
    확장자가 없는 문서 ID(예: HR_취업규칙_v1.0)는 그대로 표시합니다.

    Args:
        source: 원본 출처 문자열 (파일 경로, 파일명, 또는 문서 ID)

    Returns:
        가독성이 향상된 문서명 문자열
    """

    # --- Input ---
    if not source or source == "unknown":
        return "사내 문서"

    # --- Process ---
    # 파일 경로에서 파일명만 추출
    file_name = Path(source).name

    # 문서 확장자가 있는 경우에만 확장자 제거 (버전 번호 보존)
    suffix = Path(file_name).suffix.lower()
    if suffix in DOCUMENT_EXTENSIONS:
        display_name = Path(file_name).stem
    else:
        # 문서 ID 형식(예: HR_취업규칙_v1.0)은 그대로 사용
        display_name = file_name

    # 언더스코어와 하이픈을 공백으로 변환하여 가독성 향상
    readable = display_name.replace("_", " ").replace("-", " ")

    # --- Output ---
    return readable


class CitationFormatter:
    """RAG 답변에 출처 정보를 포맷팅하는 클래스.

    답변과 검색된 문서 목록을 받아 출처가 포함된
    형식화된 최종 응답 문자열을 생성합니다.

    Attributes:
        show_score: 유사도 점수 표시 여부
        max_sources: 표시할 최대 출처 수
    """

    def __init__(
        self,
        show_score: bool = True,
        max_sources: int = 3,
    ) -> None:
        """CitationFormatter를 초기화합니다.

        Args:
            show_score: 각 출처에 유사도 점수를 표시할지 여부 (기본값: True)
            max_sources: 표시할 최대 출처 수 (기본값: 3)
        """

        # --- Input ---
        self.show_score = show_score
        self.max_sources = max_sources

        # --- Output ---
        # 인스턴스 속성 설정 완료

    def extract_source_info(self, docs: list[dict]) -> list[dict]:
        """검색된 문서 리스트에서 출처 정보를 추출합니다.

        중복 출처를 제거하고 가장 높은 유사도 점수만 유지합니다.

        Args:
            docs: retriever.search()가 반환한 검색 결과 리스트.
                각 원소는 source, score, content 키를 포함해야 합니다.

        Returns:
            중복 제거된 출처 정보 리스트. 각 원소는 다음 키를 포함합니다:
            - source (str): 원본 파일명
            - display_name (str): 표시용 문서명
            - score (float): 최고 유사도 점수
        """

        # --- Input ---
        if not docs:
            return []

        # --- Process ---
        # 출처별로 최고 유사도 점수 추적
        source_scores: dict[str, float] = {}

        for doc in docs:
            source = doc.get("source", "unknown")
            score = doc.get("score", 0.0)

            # 동일 출처 중 최고 점수만 보관
            if source not in source_scores or score > source_scores[source]:
                source_scores[source] = score

        # 유사도 점수 내림차순 정렬
        sorted_sources = sorted(
            source_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        # 최대 출처 수 제한 적용
        limited_sources = sorted_sources[: self.max_sources]

        # 출처 정보 딕셔너리 구성
        source_info_list: list[dict] = []
        for source, score in limited_sources:
            source_info_list.append({
                "source": source,
                "display_name": _normalize_source_name(source),
                "score": score,
            })

        # --- Output ---
        return source_info_list

    def format_response(self, answer: str, sources: list[dict]) -> str:
        """답변과 출처 목록을 결합하여 최종 응답을 포맷팅합니다.

        Args:
            answer: LLM이 생성한 답변 텍스트
            sources: extract_source_info()가 반환한 출처 정보 리스트

        Returns:
            출처 섹션이 포함된 최종 응답 문자열.
            형식:
                {답변 내용}

                참고 문서:
                - {문서명} (관련도: {점수:.0%})
        """

        # --- Input ---
        answer_text = answer.strip() if answer else "답변을 생성할 수 없습니다."

        # --- Process ---
        if not sources:
            return answer_text

        # 출처 섹션 구성
        source_lines: list[str] = []
        for source_info in sources:
            display_name = source_info.get("display_name", "사내 문서")
            score = source_info.get("score", 0.0)

            if self.show_score:
                line = f"  - {display_name} (관련도: {score:.0%})"
            else:
                line = f"  - {display_name}"

            source_lines.append(line)

        citation_block = "\n".join(source_lines)
        formatted = f"{answer_text}\n\n참고 문서:\n{citation_block}"

        # --- Output ---
        return formatted

    def format_no_result(self) -> str:
        """검색 결과가 없을 때 표시할 메시지를 반환합니다.

        Returns:
            결과 없음 안내 문자열
        """

        # --- Output ---
        return (
            "해당 정보를 사내 문서에서 찾을 수 없습니다.\n"
            "질문을 다르게 표현하거나 더 구체적인 키워드를 사용해 보십시오."
        )

    def format_error(self, error_message: str) -> str:
        """오류 발생 시 표시할 메시지를 반환합니다.

        Args:
            error_message: 오류 내용 문자열

        Returns:
            사용자 친화적인 오류 안내 문자열
        """

        # --- Output ---
        return (
            f"답변 생성 중 오류가 발생했습니다.\n"
            f"오류 내용: {error_message}\n"
            "시스템 관리자에게 문의하십시오."
        )
