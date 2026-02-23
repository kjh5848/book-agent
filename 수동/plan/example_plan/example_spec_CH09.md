# CH09 예제 코드 명세 — LangChain 최종 연결

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. CH08 통합 에이전트를 LangChain Tool 규격으로 재구현 + 운영 설정(timeout, retry, 로깅, 캐싱) 추가.

## 2. 디렉토리 구조

```
CH09_LangChain최종연결/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py           ← 통합 파이프라인 진입점 (대화 루프)
│   ├── mcp_tools.py      ← LangChain Tool 규격 MCP 도구 3종
│   ├── rag_tool.py       ← RAG Chain을 LangChain Tool로 래핑
│   ├── agent.py          ← LangChain Agent 구성 (Tool 자동 선택)
│   ├── config.py         ← timeout, retry, logging, cache 설정
│   └── monitor.py        ← 토큰 카운터, 응답 시간 측정
└── outputs/
    ├── .gitkeep
    └── logs/
        └── .gitkeep
```

## 3. 파일별 함수 명세

### `src/mcp_tools.py`

```python
@tool
def get_leave_balance(employee_name: str) -> str:
    """
    직원의 잔여 연차를 조회합니다.
    Args:
        employee_name: 조회할 직원의 이름 (예: "김철수")
    Returns:
        잔여 연차 정보 문자열
    """
    # CH04 FastAPI GET /employees/{id}/leave-balance 호출

@tool
def get_sales_summary(department: str = "", quarter: str = "") -> str:
    """
    부서별, 분기별 매출 집계를 조회합니다.
    Args:
        department: 부서명 (비워두면 전체, 예: "마케팅")
        quarter: 분기 (비워두면 전체, 예: "2024-Q4")
    Returns:
        매출 집계 문자열
    """
    # CH04 FastAPI GET /sales/summary 호출

@tool
def get_employee_info(employee_name: str) -> str:
    """
    직원의 기본 정보(부서, 직급)를 조회합니다.
    Args:
        employee_name: 직원 이름
    Returns:
        직원 정보 문자열
    """
    # CH04 FastAPI GET /employees?name={name} 호출

MCP_TOOLS: list = [get_leave_balance, get_sales_summary, get_employee_info]
```

### `src/rag_tool.py`

```python
@tool
def search_company_documents(query: str) -> str:
    """
    사내 문서(규정, 가이드, 정책)를 검색하여 관련 내용을 반환합니다.
    Args:
        query: 검색할 내용 (예: "연차 신청 기한", "재택근무 정책")
    Returns:
        관련 문서 내용과 출처 정보
    """
    # CH07 RAG Chain invoke

RAG_TOOL = search_company_documents
```

### `src/config.py`

```python
@dataclass
class LLMConfig:
    model: str
    base_url: str
    temperature: float = 0.1
    timeout: int = 60           # 초 (로컬 LLM은 응답이 느림)
    max_retries: int = 2

@dataclass
class AppConfig:
    llm: LLMConfig
    log_level: str = "INFO"
    log_file: str = "./outputs/logs/app.log"
    enable_cache: bool = True
    cache_dir: str = "./outputs/cache"

def load_config() -> AppConfig:
    """
    .env에서 설정 로딩, AppConfig 반환.
    캐시 디렉토리 없으면 생성.
    """

def setup_logging(config: AppConfig) -> logging.Logger:
    """
    파일 + 콘솔 듀얼 핸들러 로거 설정.
    포맷: "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    """

def setup_cache(config: AppConfig) -> SQLiteCache:
    """
    LangChain SQLiteCache 설정 및 set_llm_cache() 등록.
    동일 프롬프트 재질의 시 캐시에서 즉시 반환.
    """
```

### `src/monitor.py`

```python
@dataclass
class RequestMetrics:
    question: str
    response_time_ms: int
    tool_calls: list[str]     # 호출된 Tool 이름 목록
    cached: bool

class MetricsCollector:
    def __init__(self):
        self._records: list[RequestMetrics] = []

    def record(self, metrics: RequestMetrics) -> None:
        """메트릭 기록."""

    def summary(self) -> dict:
        """
        수집된 메트릭 요약 반환.
        Output: {
          "total_requests": int,
          "avg_response_ms": float,
          "cache_hit_rate": float,
          "tool_usage": dict[str, int]  # 도구별 호출 횟수
        }
        """

    def print_summary(self) -> None:
        """콘솔에 요약 출력."""
```

### `src/agent.py`

```python
def build_agent(config: AppConfig) -> AgentExecutor:
    """
    LangChain AgentExecutor 구성.
    Input : AppConfig
    Process:
      1. OllamaLLM 초기화 (timeout, retry 적용)
      2. Tool 목록: MCP_TOOLS + RAG_TOOL
      3. create_react_agent() 또는 create_tool_calling_agent() 사용
      4. AgentExecutor(agent, tools, max_iterations=3, verbose=True)
    Output : AgentExecutor
    """

def run_with_metrics(
    agent: AgentExecutor,
    question: str,
    collector: MetricsCollector,
    session_id: str = "default"
) -> str:
    """
    메트릭 수집하며 에이전트 실행.
    응답 시간, 호출된 Tool, 캐시 히트 여부 기록.
    """
```

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt

# 전제조건: CH04 docker-compose up, CH07 ChromaDB 준비
python src/main.py

# 기대 출력:
# === AI 업무 비서 v2 (LangChain Agent) ===
# 설정: DeepSeek R1 | Timeout 60s | 캐시 ON | 로그: outputs/logs/app.log
#
# 질문: 김철수 남은 연차와 연차 규정 알려줘
# [Tool 호출] get_leave_balance("김철수") → 5일
# [Tool 호출] search_company_documents("연차 신청 규정") → 문서 3건
# 답변: 김철수 씨의 남은 연차는 5일입니다. 연차 규정에 따르면...
# 응답 시간: 4.2초 | 캐시: MISS
#
# 질문: 김철수 남은 연차와 연차 규정 알려줘  ← 동일 질문 재입력
# 답변: (즉시) 김철수 씨의 남은 연차는 5일입니다...
# 응답 시간: 0.01초 | 캐시: HIT ✓
```

## 5. 의존성

```
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## 6. .env.example

```
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# LLM 모델명 설정
# Ollama 예시: deepseek-r1:1.5b, deepseek-r1:8b, llama3, mistral
# OpenAI 예시: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 설정 (PROVIDER가 ollama인 경우 필요)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 설정 (PROVIDER가 openai인 경우 필요)
# OPENAI_API_KEY=sk-proj-...

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# 연결 서비스 설정
FASTAPI_BASE_URL=http://localhost:8000
CHROMA_PERSIST_DIR=../CH07_RAG_QA엔진구현/data/chroma_db
COLLECTION_NAME=rag_docs

# 성능 튜닝
LLM_TIMEOUT=60
MAX_RETRIES=2
ENABLE_CACHE=true
LOG_LEVEL=INFO
```
