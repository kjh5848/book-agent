"""LangChain LCEL 기반 RAG 파이프라인 모듈.

LangChain Expression Language(LCEL)로 Retriever -> Prompt -> LLM -> OutputParser를
체인으로 연결합니다. Ollama 미연결 또는 LangChain 미설치 시 Mock 모드로 자동 전환합니다.
"""

import os
import sys
from typing import Optional

from citation import CitationFormatter
from retriever import ChromaRetriever

# 환경 변수에서 설정 로드
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))

# 커넥트HR 사내 문서 기반 RAG 프롬프트 템플릿
SYSTEM_PROMPT = """당신은 커넥트HR 사내 문서를 기반으로 답변하는 AI 어시스턴트입니다.
아래 컨텍스트를 참고하여 질문에 답변하십시오.
컨텍스트에 없는 내용은 "해당 정보를 찾을 수 없습니다"라고 답하십시오.

컨텍스트:
{context}

질문: {question}
답변:"""


def _check_ollama_available() -> bool:
    """Ollama 서버 연결 가능 여부를 확인합니다.

    Returns:
        연결 가능하면 True, 불가능하면 False
    """

    # --- Process ---
    try:
        import requests
        resp = requests.get(OLLAMA_BASE_URL, timeout=3)
        return resp.status_code == 200
    except Exception:
        return False

    # --- Output ---
    # bool 반환


def _check_langchain_available() -> bool:
    """LangChain Ollama 패키지 설치 여부를 확인합니다.

    Returns:
        langchain-ollama가 설치되어 있으면 True, 없으면 False
    """

    # --- Process ---
    try:
        import langchain_ollama  # noqa: F401
        import langchain_core  # noqa: F401
        return True
    except ImportError:
        return False

    # --- Output ---
    # bool 반환


def _build_context_string(docs: list[dict]) -> str:
    """검색된 문서 리스트를 하나의 컨텍스트 문자열로 조합합니다.

    Args:
        docs: retriever.search()가 반환한 검색 결과 리스트

    Returns:
        번호가 붙은 컨텍스트 문자열. 예:
        [1] (HR취업규칙_v1.0)
        연차 휴가는 1년에 15일...

        [2] (HR정보보안서약서)
        보안 정책에 따라...
    """

    # --- Input ---
    if not docs:
        return "관련 문서를 찾을 수 없습니다."

    # --- Process ---
    context_parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.get("source", "unknown")
        content = doc.get("content", "")
        context_parts.append(f"[{i}] ({source})\n{content}")

    context_string = "\n\n".join(context_parts)

    # --- Output ---
    return context_string


class MockLLM:
    """Ollama 미연결 또는 LangChain 미설치 시 사용하는 Mock LLM 클래스.

    실제 LLM 없이 RAG 파이프라인 전체 흐름을 테스트할 수 있습니다.
    검색된 컨텍스트를 요약하여 Mock 답변을 생성합니다.

    Attributes:
        model_name: 표시용 모델 이름
    """

    def __init__(self, model_name: str = "mock-llm") -> None:
        """MockLLM을 초기화합니다.

        Args:
            model_name: 표시용 모델 이름 (기본값: "mock-llm")
        """

        self.model_name = model_name
        print(f"  [Mock 모드] LLM: {self.model_name}")
        print("  Ollama가 연결되지 않았거나 LangChain 패키지가 없어 Mock 응답을 사용합니다.")
        print(f"  실제 LLM 사용 시 실행 순서:")
        print(f"    1. ollama pull {OLLAMA_MODEL}")
        print(f"    2. pip install langchain langchain-ollama langchain-core")
        print(f"    3. python src/main.py 재실행")

    def invoke(self, prompt_text: str) -> str:
        """Mock 답변을 생성합니다.

        Args:
            prompt_text: 프롬프트 문자열 (컨텍스트 + 질문 포함)

        Returns:
            컨텍스트 기반으로 생성된 Mock 답변 문자열
        """

        # --- Input ---
        # 프롬프트에서 컨텍스트 섹션을 추출하여 Mock 답변 생성
        context_start = prompt_text.find("컨텍스트:")
        question_start = prompt_text.find("질문:")
        answer_start = prompt_text.find("답변:")

        # --- Process ---
        if context_start != -1 and question_start != -1:
            context_section = prompt_text[context_start + 5:question_start].strip()
            question_section = (
                prompt_text[question_start + 3:answer_start].strip()
                if answer_start != -1
                else ""
            )

            # 컨텍스트가 있으면 첫 번째 문서 내용을 요약하여 답변
            if context_section and context_section != "관련 문서를 찾을 수 없습니다.":
                first_doc_end = context_section.find("\n\n[2]")
                first_doc = (
                    context_section if first_doc_end == -1 else context_section[:first_doc_end]
                )
                # 첫 번째 청크의 처음 200자를 Mock 답변으로 사용
                first_doc_content = first_doc.split("\n", 1)[-1].strip()
                mock_answer = (
                    f"[Mock 응답] 다음 내용을 참고하십시오:\n"
                    f"{first_doc_content[:200]}..."
                )
            else:
                mock_answer = "[Mock 응답] 해당 정보를 찾을 수 없습니다."
        else:
            mock_answer = "[Mock 응답] 프롬프트 형식을 인식할 수 없습니다."

        # --- Output ---
        return mock_answer


class RAGChain:
    """LangChain LCEL 방식으로 구성된 RAG 파이프라인 클래스.

    ChromaDB 검색 → 프롬프트 조합 → LLM 추론 → 출처 포맷팅의
    전체 흐름을 하나의 체인으로 연결합니다.

    Attributes:
        retriever: ChromaDB 검색기 인스턴스
        citation_formatter: 출처 포맷터 인스턴스
        top_k: 검색 결과 수
        is_mock_mode: Mock 모드 활성화 여부
        llm: LLM 인스턴스 (Ollama 또는 Mock)
        chain: LCEL 체인 (Ollama 모드에서만 구성)
    """

    def __init__(
        self,
        retriever: ChromaRetriever,
        top_k: Optional[int] = None,
        show_score: bool = True,
    ) -> None:
        """RAGChain을 초기화합니다.

        Ollama 연결 및 LangChain 패키지 설치 여부를 확인하여
        가능한 경우 LCEL 체인을, 불가능한 경우 Mock 모드로 자동 전환합니다.

        Args:
            retriever: 초기화된 ChromaRetriever 인스턴스
            top_k: 검색 결과 수. None이면 환경 변수 RAG_TOP_K 값을 사용합니다.
            show_score: 출처에 유사도 점수를 표시할지 여부 (기본값: True)
        """

        # --- Input ---
        self.retriever = retriever
        self.top_k = top_k or RAG_TOP_K
        self.citation_formatter = CitationFormatter(show_score=show_score)
        self.is_mock_mode = False
        self.llm = None
        self.chain = None

        # --- Process ---
        # Ollama 연결 확인
        print(f"  Ollama 서버 연결 확인 중: {OLLAMA_BASE_URL}")
        ollama_ok = _check_ollama_available()
        langchain_ok = _check_langchain_available()

        if ollama_ok and langchain_ok:
            # Ollama 연결 + LangChain 설치 완료 → LCEL 체인 구성
            print(f"  [Ollama 모드] 모델: {OLLAMA_MODEL}")
            self._setup_langchain()
        else:
            # Mock 모드 전환 이유 출력
            if not ollama_ok:
                print("  [경고] Ollama 서버에 연결할 수 없습니다.")
            if not langchain_ok:
                print("  [경고] langchain-ollama 패키지가 설치되지 않았습니다.")
            print("  Mock 모드로 전환합니다.")
            self.is_mock_mode = True
            self.llm = MockLLM(model_name=OLLAMA_MODEL)

        # --- Output ---
        # self.llm 및 self.chain 설정 완료

    def _setup_langchain(self) -> None:
        """LangChain LCEL 체인을 구성합니다.

        langchain-ollama, langchain-core 패키지를 임포트하고
        ChatPromptTemplate | ChatOllama | StrOutputParser 체인을 빌드합니다.

        Raises:
            RuntimeError: langchain 또는 langchain-ollama 패키지가 없는 경우
        """

        # --- Input ---
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
        except ImportError as e:
            raise RuntimeError(
                f"LangChain 패키지를 찾을 수 없습니다: {e}\n"
                "다음 명령어로 설치하십시오:\n"
                "pip install langchain langchain-ollama langchain-core"
            ) from e

        # --- Process ---
        # ChatOllama LLM 인스턴스 생성
        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,  # 낮은 temperature로 일관된 답변 생성
        )

        # LCEL 체인 구성: 프롬프트 → LLM → 문자열 파서
        prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        output_parser = StrOutputParser()

        # LCEL 파이프 연산자(|)로 체인 연결
        self.chain = prompt | self.llm | output_parser

        print("  LCEL 체인 구성 완료: ChatPromptTemplate | ChatOllama | StrOutputParser")

        # --- Output ---
        # self.chain에 LCEL 체인 설정 완료

    def invoke(self, question: str) -> dict:
        """질문에 대한 RAG 답변을 생성합니다.

        검색 → 컨텍스트 조합 → LLM 추론 → 출처 포맷팅의 전체 흐름을 실행합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            RAG 응답 딕셔너리:
            - answer (str): 출처가 포함된 최종 답변
            - raw_answer (str): LLM이 생성한 원본 답변
            - sources (list[dict]): 참조된 출처 정보 리스트
            - retrieved_docs (list[dict]): 검색된 문서 리스트
            - question (str): 원본 질문

        Raises:
            ValueError: 질문이 비어있는 경우
        """

        # --- Input ---
        if not question or not question.strip():
            raise ValueError("질문이 비어있습니다. 질문을 입력하십시오.")

        # --- Process ---
        # 1단계: 유사도 검색
        retrieved_docs = self.retriever.search(query=question, k=self.top_k)

        if not retrieved_docs:
            return {
                "answer": self.citation_formatter.format_no_result(),
                "raw_answer": "",
                "sources": [],
                "retrieved_docs": [],
                "question": question,
            }

        # 2단계: 컨텍스트 문자열 구성
        context = _build_context_string(retrieved_docs)

        # 3단계: LLM 추론
        try:
            if self.is_mock_mode:
                # Mock 모드: 직접 프롬프트 문자열 생성 후 MockLLM 호출
                prompt_text = SYSTEM_PROMPT.format(context=context, question=question)
                raw_answer = self.llm.invoke(prompt_text)
            else:
                # Ollama 모드: LCEL 체인 실행
                raw_answer = self.chain.invoke({"context": context, "question": question})
        except Exception as e:
            return {
                "answer": self.citation_formatter.format_error(str(e)),
                "raw_answer": "",
                "sources": [],
                "retrieved_docs": retrieved_docs,
                "question": question,
            }

        # 4단계: 출처 추출 및 포맷팅
        sources = self.citation_formatter.extract_source_info(retrieved_docs)
        formatted_answer = self.citation_formatter.format_response(
            answer=raw_answer,
            sources=sources,
        )

        # --- Output ---
        return {
            "answer": formatted_answer,
            "raw_answer": raw_answer,
            "sources": sources,
            "retrieved_docs": retrieved_docs,
            "question": question,
        }

    def get_status(self) -> dict:
        """현재 RAG 체인 상태 정보를 반환합니다.

        Returns:
            상태 정보 딕셔너리:
            - mode (str): "ollama" 또는 "mock"
            - model (str): 사용 중인 모델 이름
            - top_k (int): 검색 결과 수
            - collection (str): ChromaDB 컬렉션 이름
        """

        # --- Output ---
        return {
            "mode": "mock" if self.is_mock_mode else "ollama",
            "model": OLLAMA_MODEL,
            "top_k": self.top_k,
            "collection": self.retriever.collection_name,
        }
