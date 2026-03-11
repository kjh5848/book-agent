"""
CH09 LangChain 최종 연결 — AgentExecutor 구성 모듈.

MCP 도구 3종(연차 조회, 매출 조회, 직원 정보)과 RAG 도구 1종(사내 문서 검색)을
자동 선택하는 ReAct Agent를 구성합니다.

도구 목록:
    - get_leave_balance      : 직원 잔여 연차 조회 (CH04 FastAPI)
    - get_sales_summary      : 부서별 매출 집계 조회 (CH04 FastAPI)
    - get_employee_info      : 직원 기본 정보 조회 (CH04 FastAPI)
    - search_company_documents: 사내 문서 검색 (CH07 ChromaDB)

참고:
    LangChain 1.x 이상에서는 AgentExecutor와 create_react_agent가
    langchain_classic 패키지로 이동되었습니다.
    requirements.txt에 langchain-classic 패키지가 포함되어 있습니다.
"""

import logging
import time
from typing import Any

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_ollama import OllamaLLM

from src.config import AppConfig
from src.mcp_tools import MCP_TOOLS
from src.monitor import MetricsCollector, RequestMetrics
from src.rag_tool import RAG_TOOL

logger = logging.getLogger("ch09.agent")

# ReAct Agent용 프롬프트 템플릿
_REACT_PROMPT_TEMPLATE = """당신은 사내 업무를 지원하는 AI 비서입니다.
아래 도구를 활용하여 직원의 질문에 정확하고 친절하게 답변하십시오.

사용 가능한 도구:
{tools}

도구 이름 목록: {tool_names}

질문에 답하려면 다음 형식을 반드시 따르십시오:

Thought: 어떤 도구를 사용해야 할지 판단합니다.
Action: 사용할 도구 이름 (위 도구 이름 목록 중 하나)
Action Input: 도구에 전달할 입력값
Observation: 도구 실행 결과
... (이 Thought/Action/Action Input/Observation 사이클을 필요한 만큼 반복합니다)
Thought: 이제 최종 답변을 작성할 수 있습니다.
Final Answer: 사용자에게 전달할 최종 답변 (한국어로 친절하게 작성)

시작합니다!

질문: {input}
{agent_scratchpad}"""


def build_agent(config: AppConfig) -> AgentExecutor:
    """LangChain AgentExecutor를 구성하여 반환합니다.

    OllamaLLM과 Tool 목록(MCP 3종 + RAG 1종)을 조합하여
    ReAct 방식으로 동작하는 AgentExecutor를 생성합니다.

    Args:
        config: 애플리케이션 설정 객체 (LLM 설정, 타임아웃 등 포함).

    Returns:
        AgentExecutor: 실행 준비된 에이전트 실행기.

    Raises:
        RuntimeError: LLM 초기화 또는 에이전트 구성에 실패하는 경우.
    """
    # --- Input ---
    llm_config = config.llm

    # --- Process ---
    # 1. OllamaLLM 초기화 (timeout, max_retries 적용)
    try:
        llm = OllamaLLM(
            model=llm_config.model,
            base_url=llm_config.base_url,
            temperature=llm_config.temperature,
            timeout=llm_config.timeout,
            num_predict=1024,
        )
        logger.info(
            "OllamaLLM 초기화 완료 — 모델: %s, URL: %s",
            llm_config.model,
            llm_config.base_url,
        )
    except Exception as exc:
        raise RuntimeError(
            f"OllamaLLM 초기화에 실패했습니다: {exc}\n"
            f"Ollama 서버({llm_config.base_url})가 실행 중인지 확인하십시오."
        ) from exc

    # 2. Tool 목록: MCP_TOOLS + [RAG_TOOL]
    tools: list[BaseTool] = list(MCP_TOOLS) + [RAG_TOOL]
    logger.info(
        "도구 등록 완료 — %d개: %s",
        len(tools),
        [t.name for t in tools],
    )

    # 3. ReAct 프롬프트 및 에이전트 생성
    prompt = PromptTemplate.from_template(_REACT_PROMPT_TEMPLATE)

    try:
        agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    except Exception as exc:
        raise RuntimeError(f"ReAct 에이전트 생성에 실패했습니다: {exc}") from exc

    # 4. AgentExecutor 구성 (max_iterations=5, verbose=True)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        verbose=True,
        handle_parsing_errors=(
            "에이전트가 올바른 형식으로 응답하지 못했습니다. 다시 시도합니다."
        ),
        return_intermediate_steps=True,
    )

    # --- Output ---
    return agent_executor


def run_with_metrics(
    agent: AgentExecutor,
    question: str,
    collector: MetricsCollector,
    session_id: str = "default",
) -> str:
    """메트릭을 수집하며 에이전트를 실행하고 최종 답변을 반환합니다.

    에이전트 실행 전후의 시간을 측정하고, 호출된 Tool 이름 목록과
    캐시 히트 여부를 MetricsCollector에 기록합니다.

    Args:
        agent: 실행할 AgentExecutor 인스턴스.
        question: 사용자가 입력한 질문 문자열.
        collector: 메트릭을 수집할 MetricsCollector 인스턴스.
        session_id: 세션 식별자 (로그 구분용, 기본값: "default").

    Returns:
        str: 에이전트가 생성한 최종 답변 문자열.
             실행 오류 발생 시 한국어 오류 안내 메시지를 반환합니다.
    """
    # --- Input ---
    logger.info("[세션: %s] 질문 수신: %s", session_id, question)
    start_time = time.time()
    tool_calls: list[str] = []
    cached = False

    # --- Process ---
    try:
        result: dict[str, Any] = agent.invoke({"input": question})
        answer: str = result.get("output", "답변을 생성하지 못했습니다.")

        # 중간 실행 단계에서 호출된 Tool 이름 수집
        intermediate_steps = result.get("intermediate_steps", [])
        for action, _observation in intermediate_steps:
            tool_name = getattr(action, "tool", None)
            if tool_name and tool_name not in tool_calls:
                tool_calls.append(tool_name)

    except Exception as exc:
        elapsed_error = int((time.time() - start_time) * 1000)
        error_msg = (
            f"에이전트 실행 중 오류가 발생했습니다: {exc}\n"
            "Ollama 서버와 FastAPI 서버가 정상 동작 중인지 확인하십시오."
        )
        logger.error("[세션: %s] 실행 오류: %s", session_id, exc)

        # 오류 발생 시에도 메트릭 기록
        collector.record(
            RequestMetrics(
                question=question,
                response_time_ms=elapsed_error,
                tool_calls=tool_calls,
                cached=False,
            )
        )
        return error_msg

    elapsed_ms = int((time.time() - start_time) * 1000)
    elapsed_sec = elapsed_ms / 1000

    # 캐시 히트 여부: 응답 시간이 매우 짧으면(0.5초 미만) 캐시에서 반환된 것으로 판단
    cached = elapsed_ms < 500

    # 메트릭 기록
    collector.record(
        RequestMetrics(
            question=question,
            response_time_ms=elapsed_ms,
            tool_calls=tool_calls,
            cached=cached,
        )
    )

    # 응답 시간 및 캐시 상태 출력
    cache_label = "HIT" if cached else "MISS"
    print(f"\n응답 시간: {elapsed_sec:.1f}초 | 캐시: {cache_label}")
    if tool_calls:
        print(f"호출된 도구: {', '.join(tool_calls)}")

    logger.info(
        "[세션: %s] 완료 — 응답 시간: %dms, 도구: %s, 캐시: %s",
        session_id,
        elapsed_ms,
        tool_calls,
        cache_label,
    )

    # --- Output ---
    return answer
