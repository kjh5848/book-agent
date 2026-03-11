# CH08 예제 코드 명세 — MCP Q&A 에이전트

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. CH07 FastAPI RAG 서버를 확장하여 PostgreSQL + MCP(Model Context Protocol) 기반 자율 Q&A 에이전트 구현.
MCP 서버(FastMCP) → MCP Agent(LangChain ReAct) → FastAPI 웹 UI 통합 전체 파이프라인.

참고 원본: `legacy/ex03` (ex02 + FastMCP 서버 + MCP Agent 추가)

## 2. 디렉토리 구조

```
CH08_MCP_QA에이전트/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml           ← PostgreSQL 컨테이너
├── app/
│   ├── __init__.py
│   ├── main.py                  ← FastAPI 앱 (RAG + MCP Agent 통합)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        ← PostgreSQL 연결 (psycopg2 + SQLAlchemy)
│   │   ├── crud.py              ← DB CRUD 함수 (직원/휴가/매출)
│   │   └── init_db.py           ← 샘플 데이터 초기화 스크립트
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ui.py                ← HTML 페이지 (대시보드, QA, Agent 화면)
│   │   └── qa.py                ← REST API (/admin/qa/query, /admin/qa/agent)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py       ← LLMService (ChatOllama / ChatOpenAI)
│   │   ├── vector_service.py    ← VectorService (ChromaDB + Ollama 임베딩)
│   │   ├── qa_service.py        ← QAService (인텐트 라우팅 + RAG)
│   │   └── mcp_agent_service.py ← MCP Client + LangChain ReAct Agent (신규)
│   ├── prompts/
│   │   ├── router_prompt.j2
│   │   └── answer_prompt.j2
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html       ← PostgreSQL 통계 추가 (직원 수, 매출 합계)
│   │   ├── qa.html              ← RAG 검색 채팅
│   │   └── agent.html           ← MCP Agent 채팅 UI (신규)
│   └── static/
│       ├── css/
│       │   └── qa.css
│       └── js/
│           ├── qa.js
│           └── agent.js         ← MCP Agent 모드 비동기 전송 (신규)
├── mcp/
│   └── mcp_server.py            ← FastMCP 서버 (DB 도구 9개 등록)
├── scripts/
│   └── ingest.py                ← PDF 파싱 → 청킹 → ChromaDB 저장 (CH07과 동일 패턴)
└── data/
    ├── docs/                    ← 부서별 PDF 파일 (CH07과 동일 문서셋)
    │   ├── HR_취업규칙_v1.0.pdf
    │   ├── HR_정보보안서약서.pdf
    │   └── OPS_신규서비스_런칭전략.pdf
    ├── pages/                   ← ingest.py가 저장하는 페이지 이미지
    │   └── HR_취업규칙_v1.0/
    │       ├── page_1.png
    │       └── page_2.png
    ├── markdown/                ← ingest.py가 저장하는 Vision LLM 결과 MD
    │   └── HR_취업규칙_v1.0.md
    └── chroma_db/               ← scripts/ingest.py 실행 후 자동 생성
        └── .gitkeep
```

## 3. 파일별 함수 명세

### `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: company_db
      POSTGRES_USER: company
      POSTGRES_PASSWORD: company1234
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### `app/database/connection.py`

```python
"""PostgreSQL 연결. psycopg2 + SQLAlchemy Engine."""

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://company:company1234@localhost:5432/company_db"
)
engine = create_engine(DATABASE_URL)

class PostgresConnectionWrapper:
    """psycopg2 연결을 DictCursor 기반으로 래핑. execute/commit/rollback/close 지원."""

def get_db_connection() -> PostgresConnectionWrapper:
    """SQLAlchemy raw_connection()을 PostgresConnectionWrapper로 반환."""
```

### `app/database/init_db.py`

```python
def init_db() -> None:
    """
    PostgreSQL 테이블 생성 + 샘플 데이터 삽입.

    테이블:
        employees   (id, name, dept, email, hire_date)
        leave_balance (id, employee_id, year, total, used, remaining)
        sales       (id, dept, amount, date, description)

    샘플:
        - 직원 10명 (인사팀/개발팀/영업팀/마케팅팀/기술지원팀)
        - 직원별 휴가 (연 15일, 0~10일 사용)
        - 매출 30건 (최근 90일)

    실행:
        python -m app.database.init_db
    """
```

### `app/database/crud.py`

```python
# 직원 CRUD
def list_employees(conn) -> list[dict]: ...
def get_employee(conn, employee_id: int) -> dict | None: ...
def create_employee(conn, name, dept, email, hire_date) -> dict: ...
def update_employee(conn, employee_id, **fields) -> dict | None: ...
def delete_employee(conn, employee_id) -> bool: ...

# 휴가 CRUD
def list_leaves(conn) -> list[dict]: ...
def get_leave_by_employee(conn, employee_id: int) -> dict | None: ...
def use_leave(conn, employee_id: int, days: float) -> dict | None: ...

# 매출 CRUD
def list_sales(conn, limit: int = 50) -> list[dict]: ...
def create_sale(conn, dept, amount, date, description) -> dict: ...
def get_sales_period(conn, start: str, end: str) -> list[dict]: ...
def get_sales_by_dept(conn, dept_name: str) -> dict: ...

# 통계 (대시보드용)
def count_employees(conn) -> int: ...
def sum_sales(conn) -> int: ...
```

### `mcp/mcp_server.py`

```python
"""
FastMCP 서버. PostgreSQL DB 도구를 MCP 프로토콜로 노출.
직원/휴가/매출 9개 도구 등록.

실행 (stdio 모드, MCP Client가 서브프로세스로 실행):
    python mcp/mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Company DB Assistant")

# 직원 도구
@mcp.tool()
def list_employees() -> list[dict]:
    """전체 직원 목록을 조회합니다."""

@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """특정 직원의 상세 정보를 조회합니다."""

# 휴가 도구
@mcp.tool()
def list_leaves() -> list[dict]:
    """전체 직원의 휴가 현황을 조회합니다."""

@mcp.tool()
def get_leave_balance(employee_id: int) -> dict:
    """특정 직원의 잔여 휴가를 조회합니다."""

@mcp.tool()
def use_leave(employee_id: int, days: float) -> dict:
    """휴가 사용을 등록하고 잔여량을 자동 차감합니다."""

# 매출 도구
@mcp.tool()
def list_sales(limit: int = 50) -> list[dict]:
    """전체 매출 내역을 조회합니다."""

@mcp.tool()
def create_sale(dept: str, amount: int, date: str, description: str | None) -> dict:
    """매출 데이터를 입력합니다."""

@mcp.tool()
def get_sales_period(start_date: str, end_date: str) -> list[dict]:
    """특정 기간별 매출을 조회합니다. 날짜 형식: YYYY-MM-DD"""

@mcp.tool()
def get_sales_by_dept(dept_name: str) -> dict:
    """부서별 매출 집계 결과를 조회합니다."""

if __name__ == "__main__":
    mcp.run()
```

### `app/services/mcp_agent_service.py`

```python
"""
MCP Client + LangChain ReAct Agent.
MCP 서버를 StdioServerParameters로 서브프로세스 실행 후,
MCP 도구를 LangChain Tool로 변환하여 ReAct 에이전트에 주입.
"""

class MCPToolWrapper:
    """MCP 도구 → LangChain Tool 변환 래퍼."""
    def __init__(self, session: ClientSession, tool_info):
        """tool_info.name, description, inputSchema로 초기화."""

    async def _call(self, **kwargs) -> str:
        """session.call_tool() 호출 → 텍스트 결과 반환."""

    def to_langchain_tool(self) -> Tool:
        """
        동기 호출 가능한 LangChain Tool 반환.
        func: JSON 문자열 파싱 → asyncio.run(_call(**params))
        """

REACT_PROMPT = PromptTemplate.from_template("""
다음 도구를 활용하여 질문에 답변하세요:
{tools}

형식:
Question: 질문
Thought: 생각
Action: 도구명 [{tool_names}]
Action Input: JSON 입력
Observation: 도구 결과
...
Final Answer: 최종 답변 (한국어)

질문: {input}
Thought:{agent_scratchpad}
""")

class MCPAgentService:
    def run_agent(self, query: str) -> dict:
        """
        MCP Agent 실행.
        Input : 자연어 질문
        Process:
            1. StdioServerParameters로 mcp_server.py 서브프로세스 실행
            2. ClientSession.list_tools() → MCPToolWrapper → LangChain Tools
            3. create_react_agent(llm, tools, REACT_PROMPT)
            4. AgentExecutor.invoke({"input": query})
        Output : {
            "answer": str,          ← Final Answer
            "steps": [              ← 중간 도구 호출 기록
                {"tool": str, "input": str, "output": str}
            ]
        }
        """

# 싱글톤
mcp_agent_service = MCPAgentService()
```

### `app/routers/qa.py` (CH07에서 확장)

```python
# CH07 기존 엔드포인트
@router.post("/admin/qa/query")
async def query_qa(request: QueryRequest):
    """RAG 하이브리드 검색 (CH07 동일)."""

# CH08 신규 엔드포인트
@router.post("/admin/qa/agent")
async def query_agent(request: QueryRequest):
    """
    MCP Agent 모드 질문 처리.
    Input : {"query": "홍길동의 남은 연차는?"}
    Process: mcp_agent_service.run_agent(query)
    Output : {
        "query": str,
        "answer": str,
        "steps": [{"tool": str, "input": str, "output": str}],
        "mode": "mcp_agent"
    }
    """
```

### `app/templates/agent.html`

MCP Agent 채팅 화면. 주요 구성:
- 질문 입력창 + 전송 버튼
- AJAX `POST /admin/qa/agent` 전송 (`agent.js`)
- 응답 영역:
  - 최종 답변 텍스트
  - "도구 사용 기록" 아코디언 (tool → input → output 순서로 표시)
  - **RAG 근거 패널** (unstructured_data 포함 시):
    - 출처 카드 (source, score)
    - `page_image` 썸네일 + `page_num`, `section_title` 표시
    - 이미지 클릭 시 원본 크기 모달

### `app/static/js/agent.js`

```javascript
// MCP Agent 비동기 질문 전송
async function sendAgentQuery(query) {
    // POST /admin/qa/agent → {answer, steps, mode}
    // answer 텍스트 렌더링
    // steps 아코디언: 도구명, JSON 입력, 실행 결과
}
```

## 3-1. `scripts/ingest.py` 명세

CH07의 `scripts/ingest.py`와 동일한 패턴. (Vision LLM 파싱 + ## 헤더 기반 청킹 + overlap fallback + 페이지 이미지/MD 저장)

```python
"""
CH08 문서 인제스트 스크립트.

PDF 페이지를 이미지로 캡처 → Vision LLM이 Markdown으로 파싱 →
헤더 기반 청킹 → Ollama 임베딩 → ChromaDB 저장.
페이지 이미지(data/pages/)와 Markdown(data/markdown/)을 저장하여
채팅 UI에서 답변 근거를 이미지+MD로 표시할 수 있습니다.

CH07 ingest.py와 동일 구조:
    parse_filename_metadata(filename) → dict
    pdf_page_to_base64(pdf_path, page_num, save_dir) → (str, str|None)
    parse_page_with_vision(base64_image, llm_base_url, vision_model) → str
    save_markdown(markdown_text, pdf_path, save_dir) → str
    chunk_text(text, source, department, version, page_image_map,
               chunk_size=500, overlap=50) → list[dict]
      메타데이터: source, department, version, section_title, chunk_index, page_num, page_image
    ingest(target_file=None, reset=False) → None
      [1/5] PDF 탐색 → [2/5] 페이지 캡처+이미지 저장 → [3/5] Vision 파싱+MD 저장
      → [4/5] 청킹(page_num/page_image 메타데이터 포함) → [5/5] 임베딩+저장

실행:
    python scripts/ingest.py                              # 전체
    python scripts/ingest.py --file HR_취업규칙_v1.0.pdf  # 파일 지정
    python scripts/ingest.py --reset                      # DB 초기화 후 재인제스트
"""
```

## 4. 실행 시나리오

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. PostgreSQL 실행
docker-compose up -d

# 3. DB 초기화
python -m app.database.init_db

# 4. PDF 인제스트 (전체)
python scripts/ingest.py

# 4-1. 파일 지정 인제스트 (저사양 환경: 한 파일씩 테스트 권장)
python scripts/ingest.py --file HR_취업규칙_v1.0.pdf

# 4-2. DB 초기화 후 재인제스트
python scripts/ingest.py --reset

# 5. 서버 실행
python -m app.main

# 브라우저: http://127.0.0.1:8000
```

**MCP Agent 동작 예시**:
```
[브라우저] http://127.0.0.1:8000/admin/agent

질문 입력: "홍길동의 남은 연차가 며칠이고, 연차 신청 기한이 어떻게 되나요?"

[에이전트 실행 과정]
Thought: 직원 정보와 규정 문서 모두 필요
Action: list_employees
→ [{id:1, name:"홍길동", dept:"인사팀", ...}]

Action: get_leave_balance (employee_id=1)
→ {total:15, used:5, remaining:10}

[최종 답변]
홍길동 님의 남은 연차는 10일입니다.
연차 신청은 사용 전월 말일까지 팀장에게 제출해야 합니다. (HR규정 참조)

[도구 사용 기록]
1. list_employees → 홍길동 (인사팀, id=1) 확인
2. get_leave_balance(1) → 잔여 10일
```

## 5. 의존성

```
# FastAPI
fastapi>=0.111.0
uvicorn>=0.29.0
jinja2>=3.1.0
python-multipart>=0.0.9

# PostgreSQL
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# MCP
mcp[cli]>=1.0.0

# LangChain + LLM
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
langchain-openai>=0.2.0

# 벡터 DB
chromadb>=0.5.0

# PDF → 이미지 변환 (Vision LLM 파싱용)
pymupdf>=1.24.0

# 유틸
python-dotenv>=1.0.0
```

## 6. 사양별 모델 선택 가이드

README에 아래 표를 포함한다. RAM 용량에 따라 Vision 모델과 LLM 모델을 선택하도록 안내.

| RAM | Vision 모델 (`LLM_MODEL_NAME`) | 채팅 LLM | 인제스트 예상 시간(파일당) |
|-----|-------------------------------|---------|--------------------------|
| 8GB 이하 | `moondream` | `deepseek-r1:1.5b` | 1-2분 |
| 16GB | `llava:7b` | `deepseek-r1:1.5b` | 3-5분 |
| 32GB+ | `llava:13b` | `qwen2.5:7b` | 1-2분 |

> **권장**: RAM 8GB 이하 환경에서는 `--file` 옵션으로 한 파일씩 테스트한 뒤 전체 인제스트를 진행하십시오.

## 6-1. .env.example

```
# LLM Provider (ollama | openai)
LLM_PROVIDER=ollama

# LLM 모델명
# Ollama: deepseek-r1:1.5b, deepseek-r1:8b, llama3
# OpenAI: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 서버
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI (PROVIDER=openai 시 필요)
# OPENAI_API_KEY=sk-proj-...

# 임베딩 모델 (CH07과 동일)
EMBED_MODEL=nomic-embed-text

# ChromaDB (CH07 산출물)
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs

# PostgreSQL
DATABASE_URL=postgresql://company:company1234@localhost:5432/company_db
```

## 7. 독립 실행 원칙

CH08은 이전 챕터 산출물에 의존하지 않습니다.

| 항목 | 처리 방식 |
|------|---------|
| PDF 문서 | `data/docs/` 폴더에 자체 포함 (CH07과 동일 문서셋) |
| ChromaDB | `scripts/ingest.py` 실행으로 자체 생성 (CH07과 동일 패턴) |
| PostgreSQL | `docker-compose up -d` + `python -m app.database.init_db` |
| 임베딩 모델 | Ollama `nomic-embed-text` (로컬 설치 필요) |
| 청킹 패턴 | CH07과 동일 (## 헤더 기반 + overlap fallback) |

## 8. CH09 연결

CH08의 MCP 서버 도구를 CH09에서 성능·안정성 관점으로 심화:
- MCP 도구에 캐싱 레이어 추가
- 타임아웃 처리
- 에러 핸들링 강화
- 평가 지표 (응답 시간, 정확도)
