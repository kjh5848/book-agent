"""
CH09 LangChain 연결 전략 — LangChain Agent 구성.

Router 전략, RAG Chain, MCP Tools를 결합한 LangChain Agent의 표준 구성을 정의합니다.
Timeout/Retry 설정과 응답 캐시를 통해 운영 환경에 적합한 안정성을 제공합니다.
"""

import logging
import os
import sys
import time
from typing import Any, Optional

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .cache import response_cache
from .monitoring import langfuse_monitor, token_tracker
from .tools import get_leave_balance, get_sales_sum, list_employees, search_documents
from .router import QueryRouter

load_dotenv()

logger = logging.getLogger(__name__)

# --- 설정 상수 ---
AGENT_MAX_ITERATIONS: int = 10   # Agent 최대 반복 횟수
AGENT_TIMEOUT_SECONDS: int = 60  # Agent 실행 최대 대기 시간 (초)
RETRY_MAX_ATTEMPTS: int = 3      # 최대 재시도 횟수
RETRY_DELAY_SECONDS: float = 2.0 # 재시도 간격 (초)

# --- 시스템 프롬프트 ---
SYSTEM_PROMPT = """당신은 Q/A 사내 AI AI 비서입니다.
사내 인사(HR) 시스템과 문서를 연결하여 직원들의 업무 질문에 정확하게 답변합니다.

[보유 도구]
- list_employees: 직원 목록 조회 (부서 필터 가능)
- get_leave_balance: 특정 직원의 휴가 잔여 일수 조회
- get_sales_sum: 부서별 또는 전체 매출 합계 조회
- search_documents: 사내 규정·가이드·정책 문서 검색

[도구 사용 원칙]
1. 직원 이름이나 부서가 포함된 질문 → list_employees 또는 get_leave_balance 사용
2. 매출·실적 관련 질문 → get_sales_sum 사용
3. 규정·정책·절차에 관한 질문 → search_documents 사용
4. 복합 질문(예: "홍길동의 휴가와 연차 규정") → 여러 도구를 순서대로 호출
5. 도구가 필요 없는 일상 대화 → 직접 답변

답변은 항상 한국어로 작성하고, 출처가 있을 경우 함께 표시하십시오.
"""


def _build_llm() -> Any:
    """환경 변수 기반으로 LLM 객체를 생성합니다.

    LLM_PROVIDER 환경 변수에 따라 Ollama 또는 OpenAI LLM을 반환합니다.

    Returns:
        LangChain 호환 LLM 객체 (ChatOllama 또는 ChatOpenAI)

    Raises:
        SystemExit: LLM 초기화에 실패한 경우
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    logger.info("[agent_config] LLM 제공자: %s", provider)

    # --- INPUT ---
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            print(".env 파일에 OPENAI_API_KEY를 입력하십시오. (.env.example 참조)")
            sys.exit(1)

        try:
            from langchain_openai import ChatOpenAI

            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            temperature = 1 if model_name.startswith("o") else 0
            llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=temperature,
                timeout=AGENT_TIMEOUT_SECONDS,
                max_retries=RETRY_MAX_ATTEMPTS,
            )
            logger.info("[agent_config] OpenAI LLM 생성 완료: %s", model_name)
            return llm
        except ImportError:
            print("langchain-openai 패키지가 설치되지 않았습니다.")
            print("설치 명령: pip install langchain-openai")
            sys.exit(1)

    else:
        # Ollama (기본값)
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")

        try:
            from langchain_ollama import ChatOllama

            llm = ChatOllama(
                base_url=ollama_url,
                model=model_name,
                timeout=AGENT_TIMEOUT_SECONDS,
            )
            logger.info("[agent_config] Ollama LLM 생성 완료: %s (URL: %s)", model_name, ollama_url)
            return llm
        except ImportError:
            print("langchain-ollama 패키지가 설치되지 않았습니다.")
            print("설치 명령: pip install langchain-ollama")
            sys.exit(1)
        except Exception as exc:
            print(f"Ollama LLM 초기화 실패: {exc}")
            print(f"Ollama 서버({ollama_url})가 실행 중인지 확인하십시오. (명령: ollama serve)")
            sys.exit(1)


def _build_rag_chain(llm: Any) -> Any:
    """LangChain LCEL 기반 RAG 체인을 구성합니다.

    ChromaDB Retriever와 LLM을 파이프(|) 연산자로 연결합니다.
    ChromaDB가 없으면 None을 반환하고, 도구 검색으로 대체됩니다.

    Args:
        llm: LangChain 호환 LLM 객체

    Returns:
        LCEL RAG 체인 또는 None (ChromaDB 미설정 시)
    """
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    embedding_model = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")

    try:
        import chromadb
        from langchain_chroma import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        # ① 임베딩 모델 초기화
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

        # ② ChromaDB 벡터스토어 연결
        vectorstore = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings,
            collection_name="documents",
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # ③ RAG 프롬프트 정의
        from langchain_core.prompts import ChatPromptTemplate as PromptTemplate

        rag_prompt = PromptTemplate.from_template(
            """다음 참고 문서를 바탕으로 질문에 답변하십시오.
모르는 내용은 "해당 내용을 문서에서 찾을 수 없습니다."라고 답변하십시오.
반드시 출처(source)를 함께 표시하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""
        )

        def format_docs(docs: list) -> str:
            return "\n\n".join(
                f"[출처: {doc.metadata.get('source', '알 수 없음')}]\n{doc.page_content}"
                for doc in docs
            )

        # ④ LCEL 파이프라인 구성
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
            | StrOutputParser()
        )

        logger.info("[agent_config] RAG 체인 구성 완료 (ChromaDB: %s)", chroma_dir)
        return rag_chain

    except Exception as exc:
        logger.warning(
            "[agent_config] RAG 체인 구성 실패 (search_documents 도구로 대체): %s", exc
        )
        return None


def _classify_route(query: str, router: Optional[QueryRouter] = None) -> str:
    """CH08의 QueryRouter를 활용하여 라우팅 경로를 결정합니다.

    3단계 라우팅 전략(규칙 → 스키마 → LLM)을 사용합니다.
    QueryRouter 결과를 에이전트 내부 경로명으로 매핑합니다:
      "structured" → "db", "unstructured" → "rag", "hybrid" → "agent"

    Args:
        query: 사용자 질문 문자열
        router: QueryRouter 인스턴스 (None이면 키워드 기반 폴백)

    Returns:
        라우팅 경로 문자열: "db" (정형 DB), "rag" (문서 검색), "agent" (복합/불명확)
    """
    if router is not None:
        raw_route = router.classify_query(query)
        route_map = {"structured": "db", "unstructured": "rag", "hybrid": "agent"}
        route = route_map.get(raw_route, "agent")
    else:
        # QueryRouter 미사용 시 키워드 기반 폴백
        query_lower = query.lower()
        db_keywords = ["직원", "부서", "목록", "매출", "실적", "합계", "휴가 잔여", "남은 휴가", "연차 잔여"]
        rag_keywords = ["규정", "정책", "절차", "가이드", "어떻게", "방법", "온보딩", "보안"]
        db_score = sum(1 for kw in db_keywords if kw in query_lower)
        rag_score = sum(1 for kw in rag_keywords if kw in query_lower)
        if db_score > 0 and rag_score == 0:
            route = "db"
        elif rag_score > 0 and db_score == 0:
            route = "rag"
        else:
            route = "agent"

    logger.info("[Router] 쿼리 분류 완료: route=%s", route)
    return route


class ConnectHRAgent:
    """Q/A 사내 AI AI 비서 에이전트.

    LangChain Agent, Router, RAG Chain, MCP Tools를 통합하여
    정형/비정형/복합 질문에 모두 대응합니다.

    Attributes:
        llm: LangChain LLM 객체
        tools: MCP 도구 목록
        agent_executor: LangChain AgentExecutor 객체
        rag_chain: LCEL 기반 RAG 체인 (선택사항)
    """

    def __init__(self) -> None:
        """ConnectHRAgent를 초기화합니다."""
        logger.info("[ConnectHRAgent] 초기화 시작...")

        # --- INPUT ---
        self.llm = _build_llm()
        self._router = QueryRouter(llm=self.llm)
        self.tools = [list_employees, get_leave_balance, get_sales_sum, search_documents]
        self.rag_chain = _build_rag_chain(self.llm)

        # --- PROCESS ---
        self.agent_executor = self._build_agent_executor()

        # --- OUTPUT ---
        logger.info(
            "[ConnectHRAgent] 초기화 완료 (도구 수: %d, RAG 체인: %s)",
            len(self.tools),
            "활성" if self.rag_chain else "비활성",
        )

    def _build_agent_executor(self) -> Optional[AgentExecutor]:
        """AgentExecutor를 구성합니다.

        create_tool_calling_agent로 에이전트를 생성하고
        AgentExecutor로 감싸 Timeout, Retry, 에러 처리를 설정합니다.

        Returns:
            구성된 AgentExecutor 객체 또는 None (생성 실패 시)
        """
        try:
            # ① 프롬프트 템플릿 정의
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # ② Tool Calling Agent 생성
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)

            # ③ AgentExecutor 래핑 (운영 설정 포함)
            executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                max_iterations=AGENT_MAX_ITERATIONS,
                max_execution_time=AGENT_TIMEOUT_SECONDS,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
                verbose=True,
            )

            logger.info("[ConnectHRAgent] AgentExecutor 구성 완료")
            return executor

        except Exception as exc:
            logger.error("[ConnectHRAgent] AgentExecutor 구성 실패: %s", exc)
            return None

    def _run_with_retry(self, query: str, chat_history: Optional[list] = None) -> dict[str, Any]:
        """재시도 로직이 포함된 Agent 실행 메서드.

        최대 RETRY_MAX_ATTEMPTS 횟수까지 재시도하며, 매 실패 후
        RETRY_DELAY_SECONDS만큼 대기합니다.

        Args:
            query: 사용자 질문
            chat_history: 이전 대화 기록 (멀티턴 지원)

        Returns:
            Agent 실행 결과 딕셔너리 {"output": str, "intermediate_steps": list}
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, RETRY_MAX_ATTEMPTS + 1):
            try:
                logger.info("[Retry] 시도 %d/%d", attempt, RETRY_MAX_ATTEMPTS)
                result = self.agent_executor.invoke({
                    "input": query,
                    "chat_history": chat_history or [],
                })
                return result
            except Exception as exc:
                last_error = exc
                logger.warning("[Retry] 시도 %d 실패: %s", attempt, exc)
                if attempt < RETRY_MAX_ATTEMPTS:
                    time.sleep(RETRY_DELAY_SECONDS)

        return {
            "output": f"죄송합니다. {RETRY_MAX_ATTEMPTS}회 재시도 후에도 처리에 실패했습니다. ({last_error})",
            "intermediate_steps": [],
        }

    def run(
        self,
        query: str,
        chat_history: Optional[list] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """사용자 질문을 처리하고 답변을 반환합니다.

        Router로 질문 유형을 분류한 후, 적절한 실행 경로(DB/RAG/Agent)를 선택합니다.
        캐시가 활성화된 경우 동일 질문에 대한 재호출을 방지합니다.

        Args:
            query: 사용자 질문 문자열
            chat_history: 이전 대화 기록 목록 (멀티턴 지원)
            use_cache: True이면 응답 캐시를 사용합니다.

        Returns:
            답변과 중간 단계가 담긴 딕셔너리:
            {
                "output": str,              # 최종 답변
                "route": str,               # 선택된 라우팅 경로
                "intermediate_steps": list, # Agent 중간 실행 단계
                "from_cache": bool,         # 캐시에서 응답한 경우 True
            }
        """
        start_time = time.time()

        # --- INPUT ---
        logger.info("[ConnectHRAgent] 질문 수신: %s", query[:80])

        # ① 캐시 조회
        if use_cache:
            cached = response_cache.get(query)
            if cached is not None:
                cached["from_cache"] = True
                logger.info("[ConnectHRAgent] 캐시 응답 반환")
                return cached

        # ② Router로 경로 결정 (CH08의 3단계 QueryRouter 사용)
        route = _classify_route(query, router=self._router)

        # ③ 경로별 실행
        result: dict[str, Any]
        if route == "rag" and self.rag_chain is not None:
            # 비정형 문서 검색 경로
            try:
                answer = self.rag_chain.invoke(query)
                result = {
                    "output": answer,
                    "route": route,
                    "intermediate_steps": [],
                    "from_cache": False,
                }
            except Exception as exc:
                logger.warning("[ConnectHRAgent] RAG 체인 실행 실패, Agent로 폴백: %s", exc)
                result = self._run_with_retry(query, chat_history)
                result["route"] = "agent_fallback"
                result["from_cache"] = False
        elif self.agent_executor is not None:
            # DB 조회 또는 복합 경로 → Agent 실행
            result = self._run_with_retry(query, chat_history)
            result["route"] = route
            result["from_cache"] = False
        else:
            result = {
                "output": "죄송합니다. 에이전트 서비스를 사용할 수 없습니다.",
                "route": "error",
                "intermediate_steps": [],
                "from_cache": False,
            }

        # ④ 토큰 사용량 기록 (Ollama는 토큰 수를 반환하지 않으므로 추정)
        latency_ms = (time.time() - start_time) * 1000
        model = os.getenv("OLLAMA_MODEL", os.getenv("OPENAI_MODEL", "unknown"))
        token_tracker.record(
            model=model,
            input_tokens=len(query.split()) * 2,  # 추정값
            output_tokens=len(result["output"].split()) * 2,  # 추정값
            operation="agent_run",
            latency_ms=latency_ms,
        )

        # ⑤ Langfuse 추적 전송
        langfuse_monitor.trace(
            name="agent_run",
            input_data=query,
            output_data=result["output"],
            metadata={"route": result["route"], "latency_ms": latency_ms},
        )

        # ⑥ 캐시 저장
        if use_cache:
            response_cache.set(query, result)

        # --- OUTPUT ---
        logger.info(
            "[ConnectHRAgent] 처리 완료 (경로: %s, 소요: %.0fms)",
            result["route"],
            latency_ms,
        )
        return result


# --- 싱글톤 인스턴스 ---
_agent_instance: Optional[ConnectHRAgent] = None


def get_agent() -> ConnectHRAgent:
    """ConnectHRAgent 싱글톤 인스턴스를 반환합니다.

    최초 호출 시 에이전트를 초기화하고, 이후 호출에서는 같은 인스턴스를 반환합니다.

    Returns:
        초기화된 ConnectHRAgent 인스턴스
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ConnectHRAgent()
    return _agent_instance
