"""통합 에이전트 모듈 — LangChain ReAct 에이전트.

DB 조회 도구(MCP 스타일)와 문서 검색 도구(RAG)를
하나의 ReAct 에이전트로 통합합니다.

에이전트는 사용자 질문을 받아:
  1. 필요한 도구를 스스로 선택하고
  2. 도구를 호출하여 정보를 수집하고
  3. 수집된 정보를 바탕으로 최종 답변을 생성합니다.

실행 전 Ollama 서버가 반드시 실행 중이어야 합니다.
미연결 시 RuntimeError가 발생합니다.

챕터 8.4: 대표 질문 시나리오 — 통합 에이전트 구현
"""

import os
from typing import Any

from dotenv import load_dotenv

from mcp_tools import DB_TOOLS
from rag_tool import RAG_TOOLS
from router import QueryRouter

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "8"))

# 전체 도구 목록
ALL_TOOLS = DB_TOOLS + RAG_TOOLS

# ============================================================
# ReAct 프롬프트
# ============================================================

REACT_PROMPT_TEMPLATE = """당신은 커넥트HR 사내 AI 어시스턴트입니다.
직원 정보, 연차 잔액, 매출 데이터는 DB 조회 도구를 사용하고,
회사 정책, 규정, 절차는 문서 검색 도구를 사용하십시오.
복합 질문은 여러 도구를 순서대로 사용하여 통합 답변을 작성하십시오.

사용 가능한 도구:
{tools}

도구 이름 목록:
{tool_names}

답변 형식 (반드시 준수):
Thought: 어떤 도구를 왜 사용할지 생각합니다.
Action: 도구 이름
Action Input: 도구에 전달할 입력값
Observation: 도구 실행 결과
... (필요 시 반복)
Thought: 최종 답변을 정리합니다.
Final Answer: 통합된 최종 답변

질문: {input}
{agent_scratchpad}"""


def _check_ollama_available() -> bool:
    """Ollama 서버 연결 가능 여부를 확인합니다.

    Returns:
        연결 가능하면 True, 불가능하면 False
    """

    # --- Process ---
    try:
        import requests
        response = requests.get(OLLAMA_BASE_URL, timeout=3)
        return response.status_code == 200
    except Exception:
        return False

    # --- Output ---
    # bool 반환


class IntegratedAgent:
    """MCP DB 도구와 RAG 문서 검색 도구를 통합하는 에이전트 클래스.

    LangChain ReAct 에이전트를 사용하여 사용자 질문에 대해
    DB 조회 또는 문서 검색(또는 둘 다)을 수행하고 통합 답변을 생성합니다.
    실행 전 Ollama, PostgreSQL, ChromaDB가 모두 구동되어 있어야 합니다.

    Attributes:
        router: 질문 유형 분류기
        executor: LangChain AgentExecutor
    """

    def __init__(self) -> None:
        """IntegratedAgent를 초기화합니다.

        Ollama 연결 여부를 확인하고 ReAct 에이전트를 구성합니다.
        Ollama 미연결 시 RuntimeError가 발생합니다.

        Raises:
            RuntimeError: Ollama 서버에 연결할 수 없는 경우
        """

        # --- Input ---
        self.router = QueryRouter(use_llm_fallback=False)  # 라우터는 LLM 폴백 없이 규칙만 사용
        self.executor = None

        # --- Process ---
        print(f"  Ollama 서버 연결 확인: {OLLAMA_BASE_URL}")
        if not _check_ollama_available():
            raise RuntimeError(
                f"Ollama 서버에 연결할 수 없습니다: {OLLAMA_BASE_URL}\n"
                "다음 명령을 실행한 후 재시도하십시오:\n"
                "  ollama serve\n"
                f"  ollama pull {OLLAMA_MODEL}"
            )

        self._setup_react_agent()
        print(f"  [에이전트] ReAct 에이전트 구성 완료 (모델: {OLLAMA_MODEL})")

        # --- Output ---
        # self.executor 설정 완료

    def _setup_react_agent(self) -> None:
        """LangChain ReAct 에이전트를 구성합니다.

        ChatOllama LLM과 DB/RAG 도구를 연결하여
        AgentExecutor를 생성합니다.

        Raises:
            ImportError: langchain 패키지 미설치 시
            RuntimeError: 에이전트 구성 실패 시
        """

        # --- Input ---
        try:
            from langchain_ollama import ChatOllama
            from langchain.agents import AgentExecutor, create_react_agent
            from langchain_core.prompts import PromptTemplate
        except ImportError as e:
            raise ImportError(
                f"LangChain 패키지를 찾을 수 없습니다: {e}\n"
                "pip install langchain langchain-ollama langchain-core 를 실행하십시오."
            ) from e

        # --- Process ---
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )

        prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

        agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=True,
            max_iterations=AGENT_MAX_ITERATIONS,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )

        # --- Output ---
        # self.executor 설정 완료

    def run(self, question: str) -> dict[str, Any]:
        """사용자 질문을 처리하여 통합 답변을 생성합니다.

        1단계: 질문 유형을 분류합니다 (정형/비정형/복합).
        2단계: 에이전트가 적절한 도구를 선택하여 정보를 수집합니다.
        3단계: 수집된 정보를 바탕으로 최종 답변을 생성합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            결과 딕셔너리:
            - question (str): 원본 질문
            - query_type (str): 질문 유형
            - confidence (float): 분류 신뢰도
            - method (str): 분류 방법 (rule | llm | default)
            - answer (str): 최종 답변
            - mode (str): 실행 모드 (ollama)

        Raises:
            ValueError: 질문이 비어있는 경우
            RuntimeError: 에이전트 실행 실패 시
        """

        # --- Input ---
        if not question or not question.strip():
            raise ValueError("질문이 비어있습니다. 질문을 입력하십시오.")

        # --- Process ---
        # 1단계: 질문 유형 분류
        route = self.router.classify(question)
        query_type = route["type"]
        confidence = route["confidence"]
        method = route["method"]

        # 2단계: 에이전트 실행
        result = self.executor.invoke({"input": question})
        answer = result.get("output", "답변을 생성하지 못했습니다.")

        # --- Output ---
        return {
            "question": question,
            "query_type": query_type,
            "confidence": confidence,
            "method": method,
            "answer": answer,
            "mode": "ollama",
        }
