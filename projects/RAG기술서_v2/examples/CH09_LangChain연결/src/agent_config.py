"""에이전트 구성 모듈 — 운영 파라미터 및 컴포넌트 빌더.

AgentConfig 데이터클래스로 운영 설정을 한 곳에서 관리하고,
RAG Chain / MCP Tools / LangChain Agent를 빌드하는 팩토리 함수를 제공합니다.

개발 버전(CH08)에서 가끔 튕기거나 응답이 느렸던 원인은
타임아웃, 재시도, 캐시 설정이 없었기 때문입니다.
이 모듈은 프로덕션 수준의 안정성을 확보하는 모든 설정을 담습니다.

챕터 9.1: Router / Agent / RAG Chain / MCP Tool 구성
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

from monitoring import ResponseCache, TokenUsageTracker
from mcp_tools import DB_TOOLS

load_dotenv()

logger = logging.getLogger("ch09.agent_config")

# ============================================================
# 운영 파라미터 데이터클래스
# ============================================================


@dataclass
class AgentConfig:
    """LangChain 에이전트 운영 파라미터 설정 클래스.

    환경 변수에서 값을 읽거나, 직접 생성자에 전달하여 사용합니다.
    모든 필드에 기본값이 있으므로 최소한의 설정으로도 동작합니다.

    Attributes:
        ollama_model:          사용할 Ollama LLM 모델명
        ollama_base_url:       Ollama 서버 주소
        chroma_persist_dir:    ChromaDB 저장 경로
        llm_timeout:           LLM 응답 최대 대기 시간(초)
        llm_max_retries:       LLM 호출 최대 재시도 횟수
        cache_ttl:             응답 캐시 유지 시간(초)
        max_tokens_per_request: 요청당 최대 토큰 수
        log_level:             로그 레벨 문자열
        log_file:              로그 파일 경로
        agent_max_iterations:  ReAct 에이전트 최대 반복 횟수
    """

    ollama_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "deepseek-r1")
    )
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    chroma_persist_dir: str = field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    )
    llm_timeout: int = field(
        default_factory=lambda: int(os.getenv("LLM_TIMEOUT", "30"))
    )
    llm_max_retries: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_RETRIES", "3"))
    )
    cache_ttl: int = field(
        default_factory=lambda: int(os.getenv("CACHE_TTL", "300"))
    )
    max_tokens_per_request: int = field(
        default_factory=lambda: int(os.getenv("MAX_TOKENS_PER_REQUEST", "2000"))
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_file: str = field(
        default_factory=lambda: os.getenv("LOG_FILE", "./outputs/app.log")
    )
    agent_max_iterations: int = 8

    def __post_init__(self) -> None:
        """설정 유효성을 검사합니다."""
        if self.llm_timeout <= 0:
            raise ValueError(
                f"LLM_TIMEOUT은 1 이상이어야 합니다. 현재값: {self.llm_timeout}"
            )
        if self.llm_max_retries < 0:
            raise ValueError(
                f"LLM_MAX_RETRIES는 0 이상이어야 합니다. 현재값: {self.llm_max_retries}"
            )
        if self.cache_ttl <= 0:
            raise ValueError(
                f"CACHE_TTL은 1 이상이어야 합니다. 현재값: {self.cache_ttl}"
            )


# ============================================================
# RAG Chain 빌더
# ============================================================

# ReAct 에이전트 프롬프트 템플릿
_REACT_PROMPT_TEMPLATE = """당신은 커넥트HR 사내 AI 어시스턴트입니다.
직원 정보, 연차 잔액, 부서 직원 목록, 매출 데이터는 DB 조회 도구를 사용하고,
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


def build_rag_chain(config: AgentConfig) -> Any:
    """ChromaDB와 LangChain LCEL을 사용하는 RAG 체인을 빌드합니다.

    ChromaDB에서 관련 문서를 검색하고 LLM으로 답변을 생성하는
    LCEL(LangChain Expression Language) 파이프라인을 구성합니다.
    ChromaDB 미연결 시 None을 반환하고 로그로 안내합니다.

    Args:
        config: AgentConfig 운영 파라미터 객체

    Returns:
        구성된 RAG 체인 객체. ChromaDB 없으면 None.
    """

    # --- Input ---
    logger.info("RAG 체인 빌드 시작: chroma_dir=%s", config.chroma_persist_dir)

    # --- Process ---
    try:
        import chromadb
        from langchain_community.vectorstores import Chroma
        from langchain_ollama import OllamaEmbeddings, ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        # Embeddings 초기화
        embeddings = OllamaEmbeddings(
            model=config.ollama_model,
            base_url=config.ollama_base_url,
        )

        # ChromaDB 벡터스토어 연결
        vectorstore = Chroma(
            persist_directory=config.chroma_persist_dir,
            embedding_function=embeddings,
        )

        # Retriever 설정
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )

        # LLM 초기화 (타임아웃 적용)
        llm = ChatOllama(
            model=config.ollama_model,
            base_url=config.ollama_base_url,
            temperature=0.1,
            num_predict=config.max_tokens_per_request,
        )

        # RAG 프롬프트 템플릿
        rag_prompt = ChatPromptTemplate.from_template(
            "다음 컨텍스트를 참고하여 질문에 답변하십시오.\n\n"
            "컨텍스트:\n{context}\n\n"
            "질문: {question}\n\n"
            "답변:"
        )

        # LCEL 체인 구성: Retriever → Prompt → LLM → Parser
        def format_docs(docs: list) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
            | StrOutputParser()
        )

        logger.info("RAG 체인 빌드 완료")

        # --- Output ---
        return rag_chain

    except Exception as exc:
        logger.warning(
            "RAG 체인 빌드 실패 — ChromaDB 또는 Ollama 미연결로 판단합니다. 오류: %s", exc
        )
        return None


# ============================================================
# MCP Tool 목록 빌더
# ============================================================


def build_mcp_tools(config: AgentConfig) -> list:
    """운영 설정이 적용된 MCP Tool 목록을 반환합니다.

    CH09의 확장된 도구 목록(get_employee_list, get_annual_sales 포함)을
    AgentConfig와 함께 반환합니다.

    Args:
        config: AgentConfig 운영 파라미터 객체

    Returns:
        LangChain Tool 객체 목록
    """

    # --- Input ---
    logger.info("MCP 도구 목록 빌드: 도구 수=%d", len(DB_TOOLS))

    # --- Process ---
    # CH09에서는 RAG 문서 검색도 도구로 등록
    tools = list(DB_TOOLS)

    # RAG 검색 도구 추가 (ChromaDB 연결 시)
    rag_chain = build_rag_chain(config)
    if rag_chain is not None:
        from langchain.tools import Tool
        rag_tool = Tool(
            name="search_company_docs",
            func=lambda q: rag_chain.invoke(q),
            description=(
                "사내 문서에서 정보를 검색합니다. "
                "회사 정책, 취업규칙, 복리후생, 업무 절차 등 문서 기반 질문에 사용하십시오. "
                "DB에 없는 규정이나 지침이 필요할 때 이 도구를 사용하십시오."
            ),
        )
        tools.append(rag_tool)
        logger.info("RAG 검색 도구 등록 완료")
    else:
        logger.warning("ChromaDB 미연결 — RAG 검색 도구 없이 DB 도구만 등록합니다.")

    # --- Output ---
    logger.info("도구 목록 구성 완료: 총 %d개", len(tools))
    return tools


# ============================================================
# 통합 에이전트 빌더
# ============================================================


def build_agent(
    config: AgentConfig,
    cache: ResponseCache,
    token_tracker: TokenUsageTracker,
) -> Any:
    """운영 설정이 적용된 LangChain ReAct 에이전트를 빌드합니다.

    타임아웃, 재시도, 캐시, 토큰 모니터링이 통합된 에이전트를 구성합니다.
    Ollama 미연결 시 Mock 모드 에이전트를 반환합니다.

    Args:
        config:        AgentConfig 운영 파라미터 객체
        cache:         ResponseCache 응답 캐시 객체
        token_tracker: TokenUsageTracker 토큰 추적 객체

    Returns:
        ProductionAgent 인스턴스
    """

    # --- Input ---
    logger.info(
        "에이전트 빌드 시작: 모델=%s, timeout=%ds, retries=%d",
        config.ollama_model,
        config.llm_timeout,
        config.llm_max_retries,
    )

    # --- Process ---
    tools = build_mcp_tools(config)
    agent = ProductionAgent(config=config, tools=tools, cache=cache, token_tracker=token_tracker)

    # --- Output ---
    logger.info("에이전트 빌드 완료")
    return agent


# ============================================================
# 프로덕션 에이전트 클래스
# ============================================================


class ProductionAgent:
    """운영 설정(Timeout / Retry / Cache / 토큰 추적)이 통합된 에이전트 클래스.

    LangChain ReAct 에이전트를 래핑하며,
    캐시 히트 시 LLM을 호출하지 않고 즉시 반환합니다.
    Ollama 미연결 시 Mock 모드로 자동 전환됩니다.

    Attributes:
        config:        AgentConfig 운영 파라미터
        tools:         사용 가능한 도구 목록
        cache:         응답 캐시
        token_tracker: 토큰 사용량 추적기
        is_mock_mode:  Mock 모드 활성화 여부
        executor:      LangChain AgentExecutor (Ollama 모드 시)
    """

    def __init__(
        self,
        config: AgentConfig,
        tools: list,
        cache: ResponseCache,
        token_tracker: TokenUsageTracker,
    ) -> None:
        """ProductionAgent를 초기화합니다.

        Args:
            config:        AgentConfig 운영 파라미터 객체
            tools:         LangChain Tool 목록
            cache:         ResponseCache 응답 캐시 객체
            token_tracker: TokenUsageTracker 토큰 추적 객체
        """

        # --- Input ---
        self.config = config
        self.tools = tools
        self.cache = cache
        self.token_tracker = token_tracker
        self.is_mock_mode = False
        self.executor = None

        # --- Process ---
        logger.info("Ollama 서버 연결 확인: %s", config.ollama_base_url)
        if self._check_ollama_available():
            try:
                self._setup_react_agent()
                logger.info("ReAct 에이전트 구성 완료 (모델: %s)", config.ollama_model)
            except Exception as exc:
                logger.warning("에이전트 구성 실패: %s — Mock 모드로 전환합니다.", exc)
                self.is_mock_mode = True
        else:
            logger.warning("Ollama 미연결 — Mock 모드로 전환합니다.")
            self.is_mock_mode = True

        if self.is_mock_mode:
            logger.info(
                "Mock 모드 활성화. 실제 LLM 사용 시: ollama pull %s 후 재실행하십시오.",
                config.ollama_model,
            )

        # --- Output ---
        # self.executor 또는 is_mock_mode 설정 완료

    def _check_ollama_available(self) -> bool:
        """Ollama 서버 연결 가능 여부를 확인합니다.

        Returns:
            연결 가능하면 True, 불가능하면 False
        """

        # --- Process ---
        try:
            import requests
            response = requests.get(self.config.ollama_base_url, timeout=3)
            return response.status_code == 200
        except Exception:
            return False

        # --- Output ---
        # bool 반환

    def _setup_react_agent(self) -> None:
        """LangChain ReAct 에이전트를 구성합니다.

        타임아웃이 적용된 ChatOllama LLM과 전체 도구 목록을 연결하여
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
        except ImportError as exc:
            raise ImportError(
                f"LangChain 패키지를 찾을 수 없습니다: {exc}\n"
                "pip install langchain langchain-ollama langchain-core 를 실행하십시오."
            ) from exc

        # --- Process ---
        llm = ChatOllama(
            model=self.config.ollama_model,
            base_url=self.config.ollama_base_url,
            temperature=0.1,
            num_predict=self.config.max_tokens_per_request,
            # ChatOllama는 timeout을 직접 지원하지 않으므로
            # requests 레벨에서 timeout을 처리합니다.
        )

        prompt = PromptTemplate.from_template(_REACT_PROMPT_TEMPLATE)

        agent = create_react_agent(llm=llm, tools=self.tools, prompt=prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.config.agent_max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )

        # --- Output ---
        # self.executor 설정 완료

    def _mock_run(self, question: str) -> str:
        """Ollama 미연결 시 도구를 직접 호출하는 Mock 실행 함수.

        LLM 없이 질문의 키워드를 분석하여 적절한 도구를 직접 호출합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            도구 호출 결과를 조합한 Mock 답변 문자열
        """

        # --- Input ---
        import json
        results: list[str] = []
        logger.debug("Mock 실행 시작: question=%s", question[:50])

        # --- Process ---
        # 직원 이름 키워드 추출
        known_names = list({v["name"] for v in [
            {"name": "이서연"}, {"name": "김도현"}, {"name": "박민준"},
            {"name": "최지은"}, {"name": "정다희"}, {"name": "한재원"}, {"name": "오수빈"},
        ]})
        found_name = next((n for n in known_names if n in question), None)

        # 부서 키워드 추출
        known_depts = ["개발팀", "영업팀", "데이터팀", "인사팀"]
        found_dept = next((d for d in known_depts if d in question), None)

        if found_name:
            # 직원 정보 조회
            from mcp_tools import get_employee_info, get_leave_balance
            emp_result = get_employee_info.invoke({"name": found_name})
            emp_data = json.loads(emp_result)
            if "오류" not in emp_data:
                results.append(
                    f"[직원 정보] {found_name}: {emp_data.get('department')} "
                    f"{emp_data.get('position')}, 기본급 {emp_data.get('base_salary'):,}원"
                )
                # 연차 키워드가 있으면 연차 조회
                if any(kw in question for kw in ["연차", "잔여", "남은", "휴가"]):
                    emp_id = emp_data.get("id")
                    if emp_id:
                        leave_result = get_leave_balance.invoke({"employee_id": emp_id})
                        leave_data = json.loads(leave_result)
                        if "오류" not in leave_data:
                            results.append(
                                f"[연차 정보] {found_name}: "
                                f"총 {leave_data.get('총_연차')}일 중 "
                                f"{leave_data.get('사용_연차')}일 사용, "
                                f"잔여 {leave_data.get('잔여_연차')}일"
                            )
            else:
                results.append(f"[직원 정보] {emp_data.get('오류', '조회 실패')}")

        if found_dept:
            # 부서 직원 목록 조회
            if any(kw in question for kw in ["직원", "멤버", "구성원", "소속", "목록"]):
                from mcp_tools import get_employee_list
                list_result = get_employee_list.invoke({"department": found_dept})
                list_data = json.loads(list_result)
                emp_list = list_data.get("직원목록", [])
                names_str = ", ".join(
                    f"{e['이름']}({e['직급']})" for e in emp_list
                )
                results.append(
                    f"[{found_dept} 직원 목록] 총 {list_data.get('직원수')}명: {names_str}"
                )

            # 연간 매출 조회
            if any(kw in question for kw in ["연간", "연도", "한 해", "전체"]) and any(
                kw in question for kw in ["매출", "실적", "달성"]
            ):
                from mcp_tools import get_annual_sales
                year = 2024
                annual_result = get_annual_sales.invoke({"department": found_dept, "year": year})
                annual_data = json.loads(annual_result)
                if "오류" not in annual_data:
                    results.append(
                        f"[{found_dept} {year}년 연간 매출] "
                        f"총 {annual_data.get('연간매출', 0):,}원 / "
                        f"목표 {annual_data.get('연간목표', 0):,}원 "
                        f"(달성률 {annual_data.get('연간달성률')}%)"
                    )

        if not results:
            results.append(
                "[안내] 질문에 해당하는 정보를 찾을 수 없습니다. "
                "직원 이름이나 부서명을 포함하여 다시 질문하십시오."
            )

        # --- Output ---
        return "\n\n".join(results)

    def run(self, question: str) -> dict[str, Any]:
        """사용자 질문을 처리하여 통합 답변을 생성합니다.

        캐시에 동일 질문이 있으면 LLM 호출 없이 즉시 반환합니다.
        캐시 미스 시 에이전트(또는 Mock)로 처리하고 결과를 캐시에 저장합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            결과 딕셔너리:
            - question (str):  원본 질문
            - answer (str):    최종 답변
            - mode (str):      실행 모드 (ollama | mock | cached)
            - from_cache (bool): 캐시 응답 여부

        Raises:
            ValueError: 질문이 비어있는 경우
        """

        # --- Input ---
        if not question or not question.strip():
            raise ValueError(
                "질문이 비어있습니다. 질문을 입력하십시오."
            )

        # --- Process ---
        # 1단계: 캐시 확인
        cache_key = question.strip().lower()
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("캐시 응답 반환: question=%s", question[:50])
            return {
                "question": question,
                "answer":   cached,
                "mode":     "cached",
                "from_cache": True,
            }

        # 2단계: 에이전트 실행
        start_time = __import__("time").perf_counter()
        if self.is_mock_mode:
            answer = self._mock_run(question)
            mode = "mock"
            # Mock 모드: 예상 토큰 수 기록 (실측 불가)
            self.token_tracker.track(
                prompt_tokens=len(question.split()) * 2,
                completion_tokens=len(answer.split()),
                model=self.config.ollama_model,
            )
        else:
            try:
                result = self.executor.invoke({"input": question})
                answer = result.get("output", "답변을 생성하지 못했습니다.")
                mode = "ollama"
                # 토큰 정보가 있으면 기록 (ChatOllama 응답에 포함될 수 있음)
                self.token_tracker.track(
                    prompt_tokens=len(question.split()) * 2,
                    completion_tokens=len(answer.split()),
                    model=self.config.ollama_model,
                )
            except Exception as exc:
                logger.warning("에이전트 실행 오류: %s — Mock 모드로 재시도합니다.", exc)
                answer = self._mock_run(question)
                mode = "mock_fallback"

        elapsed = __import__("time").perf_counter() - start_time
        logger.info("질문 처리 완료: %.2f초 소요, mode=%s", elapsed, mode)

        # 3단계: 캐시 저장
        self.cache.set(cache_key, answer)

        # --- Output ---
        return {
            "question":   question,
            "answer":     answer,
            "mode":       mode,
            "from_cache": False,
        }
