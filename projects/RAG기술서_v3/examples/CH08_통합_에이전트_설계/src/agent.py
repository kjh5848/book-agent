"""통합 에이전트 모듈.

ReAct 패턴(Reasoning + Acting)으로 정형 DB 조회와
비정형 문서 검색을 통합하여 복합 질문에 답변하는 에이전트를 구현한다.

IPO 패턴:
  Input  - 사용자 질문 문자열 + QueryRouter 분류 결과
  Process - ReAct Agent가 MCP 도구를 선택·실행하여 정보 수집
  Output - 최종 답변 + 정형/비정형 데이터 + 중간 실행 단계
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from .mcp_tools import ALL_TOOLS
from .router import QueryRouter

# ---------------------------------------------------------------------------
# 1. LLM 팩토리
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """당신은 사내 HR 및 업무 질문에 답변하는 AI 어시스턴트입니다.

사용 가능한 도구:
- leave_balance: 직원 연차 잔여 조회 (emp_no 또는 이름으로 검색)
- sales_sum: 매출 합계 조회 (부서, 기간 필터 가능)
- list_employees: 직원 목록 조회 (부서 필터 가능)
- search_documents: 사내 문서 검색 (절차, 정책, 안내 등)

규칙:
1. 정형 데이터(숫자/통계/목록)는 DB 조회 도구를 사용하세요.
2. 비정형 질문(절차/정책/설명)은 search_documents를 사용하세요.
3. 복합 질문은 두 종류의 도구를 모두 사용하세요.
4. 답변은 반드시 한국어로 작성하세요.
5. 도구 실행 결과의 핵심 정보만 추출하여 자연스러운 문장으로 답변하세요. 원본 JSON이나 딕셔너리를 절대 그대로 출력하지 마세요."""


def build_llm(temperature: float = 0.0) -> Any:
    """환경 변수에 따라 LLM 인스턴스를 생성한다.

    LLM_PROVIDER 환경 변수로 공급자를 결정한다:
      - "openai" → ChatOpenAI (OPENAI_API_KEY 필요)
      - 그 외   → ChatOllama (로컬 Ollama 서버)

    Args:
        temperature: 생성 온도 (0.0~1.0, 낮을수록 일관된 답변).

    Returns:
        LangChain Chat 모델 인스턴스.

    Raises:
        ImportError: 필요한 패키지가 설치되지 않은 경우.
        RuntimeError: LLM 초기화에 실패한 경우.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        except ImportError as e:
            raise ImportError(f"langchain-openai 패키지가 필요합니다: {e}") from e

    # 기본값: Ollama
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
        )
    except ImportError as e:
        raise ImportError(f"langchain-ollama 패키지가 필요합니다: {e}") from e


# ---------------------------------------------------------------------------
# 2. 통합 에이전트 클래스
# ---------------------------------------------------------------------------

class IntegratedAgent:
    """정형 + 비정형 통합 ReAct 에이전트.

    QueryRouter로 질문을 분류한 후, AgentExecutor가 MCP 도구를
    필요한 만큼 반복 실행하여 최종 답변을 생성한다.
    """

    def __init__(self, llm=None) -> None:
        """에이전트를 초기화한다.

        Args:
            llm: LangChain LLM 인스턴스. None이면 build_llm()을 호출.
        """
        self._llm = llm or build_llm()
        self._router = QueryRouter(llm=self._llm)
        self._agent_executor = self._build_agent_executor()

    def _build_agent_executor(self) -> Any:
        """LangChain AgentExecutor를 생성한다.

        create_tool_calling_agent로 ReAct 패턴 에이전트를 구성한다.

        Returns:
            AgentExecutor 인스턴스 또는 None (패키지 없을 시).
        """
        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

            # ① 프롬프트 구성 (system + history + input + scratchpad)
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # ② Tool Calling Agent 생성
            agent = create_tool_calling_agent(
                llm=self._llm,
                tools=ALL_TOOLS,
                prompt=prompt,
            )

            # ③ AgentExecutor 래핑 (중간 단계 반환 활성화)
            return AgentExecutor(
                agent=agent,
                tools=ALL_TOOLS,
                verbose=False,
                return_intermediate_steps=True,
                max_iterations=10,
                handle_parsing_errors=True,
            )
        except Exception as e:
            print(f"[경고] AgentExecutor 초기화 실패: {e}. 폴백 모드로 동작합니다.")
            return None

    def run(self, query: str) -> dict:
        """질문을 처리하고 통합 응답을 반환한다.

        Args:
            query: 사용자 자연어 질문.

        Returns:
            answer, query_type, structured_data, unstructured_data, steps 포함 딕셔너리.
        """
        # ① 질문 유형 분류
        query_type = self._router.classify_query(query)  # ①

        # ② 에이전트 실행
        if self._agent_executor is None:
            return self._fallback_response(query, query_type)

        try:
            result = self._agent_executor.invoke({"input": query})  # ②
            answer = result.get("output", "답변을 생성하지 못했습니다.")
            steps = result.get("intermediate_steps", [])

            # ③ DeepSeek-R1 <think> 태그 제거
            answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()  # ③

            # ④ 중간 단계에서 정형/비정형 데이터 추출
            structured_data, unstructured_data = self._parse_result(steps)  # ④

            return {
                "answer": answer,
                "query_type": query_type,
                "structured_data": structured_data,
                "unstructured_data": unstructured_data,
                "steps": self._serialize_steps(steps),
            }
        except Exception as e:
            return {
                "answer": f"처리 중 오류가 발생했습니다: {e}",
                "query_type": query_type,
                "structured_data": {},
                "unstructured_data": [],
                "steps": [],
            }

    def _parse_result(self, steps: list) -> tuple[dict, list]:
        """에이전트 중간 실행 단계에서 데이터를 추출한다.

        Args:
            steps: AgentExecutor의 intermediate_steps 리스트.

        Returns:
            (structured_data, unstructured_data) 튜플.
        """
        structured_data: dict = {}
        unstructured_data: list = []

        for action, observation in steps:
            tool_name = getattr(action, "tool", "")

            if tool_name in ("leave_balance", "list_employees", "sales_sum"):
                # 정형 데이터: observation은 dict 또는 문자열
                if isinstance(observation, dict):
                    structured_data[tool_name] = observation
                elif isinstance(observation, str):
                    try:
                        structured_data[tool_name] = json.loads(observation)
                    except json.JSONDecodeError:
                        structured_data[tool_name] = {"raw": observation}

            elif tool_name == "search_documents":
                # 비정형 데이터: results 리스트 추출
                if isinstance(observation, dict):
                    docs = observation.get("results", [])
                elif isinstance(observation, str):
                    try:
                        parsed = json.loads(observation)
                        docs = parsed.get("results", []) if isinstance(parsed, dict) else []
                    except json.JSONDecodeError:
                        docs = []
                else:
                    docs = []
                unstructured_data.extend(docs)

        return structured_data, unstructured_data

    def _serialize_steps(self, steps: list) -> list[dict]:
        """중간 단계를 JSON 직렬화 가능한 형태로 변환한다.

        Args:
            steps: AgentExecutor의 intermediate_steps 리스트.

        Returns:
            tool, input, output 키를 포함한 딕셔너리 리스트.
        """
        serialized = []
        for action, observation in steps:
            serialized.append({
                "tool": getattr(action, "tool", "unknown"),
                "input": getattr(action, "tool_input", {}),
                "output": observation if isinstance(observation, (str, int, float, bool)) else str(observation),
            })
        return serialized

    def _fallback_response(self, query: str, query_type: str) -> dict:
        """AgentExecutor 없을 때 직접 LLM 응답을 생성한다.

        Args:
            query: 사용자 질문.
            query_type: QueryRouter가 분류한 질문 유형.

        Returns:
            에이전트 응답과 동일한 구조의 딕셔너리.
        """
        try:
            response = self._llm.invoke(f"다음 질문에 한국어로 답변하세요: {query}")
            answer = response.content if hasattr(response, "content") else str(response)
            answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
        except Exception as e:
            answer = f"LLM 응답 생성 실패: {e}"

        return {
            "answer": answer,
            "query_type": query_type,
            "structured_data": {},
            "unstructured_data": [],
            "steps": [],
        }
