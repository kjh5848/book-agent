# CH08 코드 검증 보고서

## 판정: CONDITIONAL_PASS

> 필수 항목 전체 통과. 권장 항목 중 `langchain-chroma` 패키지 누락 발견 → 검증 중 즉시 수정 완료.

---

## 1. 파일 구조

명세(`example_spec_CH08.md`)와 실제 파일 목록을 대조한 결과입니다.

| 경로 | 명세 | 실제 | 결과 |
|------|------|------|------|
| `README.md` | O | O | PASS |
| `requirements.txt` | O | O | PASS |
| `.env.example` | O | O | PASS |
| `docker-compose.yml` | O | O | PASS |
| `app/__init__.py` | O | O | PASS |
| `app/main.py` | O | O | PASS |
| `app/database/__init__.py` | O | O | PASS |
| `app/database/connection.py` | O | O | PASS |
| `app/database/crud.py` | O | O | PASS |
| `app/database/init_db.py` | O | O | PASS |
| `app/routers/__init__.py` | O | O | PASS |
| `app/routers/ui.py` | O | O | PASS |
| `app/routers/qa.py` | O | O | PASS |
| `app/services/__init__.py` | O | O | PASS |
| `app/services/llm_service.py` | O | O | PASS |
| `app/services/vector_service.py` | O | O | PASS |
| `app/services/qa_service.py` | O | O | PASS |
| `app/services/mcp_agent_service.py` | O | O | PASS |
| `app/prompts/router_prompt.j2` | O | O | PASS |
| `app/prompts/answer_prompt.j2` | O | O | PASS |
| `app/templates/base.html` | O | O | PASS |
| `app/templates/dashboard.html` | O | O | PASS |
| `app/templates/qa.html` | O | O | PASS |
| `app/templates/agent.html` | O | O | PASS |
| `app/static/css/qa.css` | O | O | PASS |
| `app/static/js/qa.js` | O | O | PASS |
| `app/static/js/agent.js` | O | O | PASS |
| `mcp/__init__.py` | O | O | PASS |
| `mcp/mcp_server.py` | O | O | PASS |
| `scripts/ingest.py` | O | O | PASS |
| `data/docs/.gitkeep` | O | O | PASS |
| `data/chroma_db/.gitkeep` | O | O | PASS |

**결과: PASS — 명세 대비 파일 구조 100% 일치**

---

## 2. Python 문법 검증

Bash 도구 실행 권한 제한으로 `python -m py_compile` 직접 실행 불가. 각 파일을 전문 읽기(Read 도구)로 코드 구조와 문법을 정적 분석하였습니다.

| 파일 | 분석 결과 | 비고 |
|------|----------|------|
| `scripts/ingest.py` | PASS | 문법 이상 없음 |
| `mcp/mcp_server.py` | PASS | 문법 이상 없음 |
| `app/services/mcp_agent_service.py` | PASS | 문법 이상 없음 |
| `app/services/llm_service.py` | PASS | 문법 이상 없음 |
| `app/services/qa_service.py` | PASS | 문법 이상 없음 |
| `app/services/vector_service.py` | PASS | 문법 이상 없음 |
| `app/database/connection.py` | PASS | 문법 이상 없음 |
| `app/database/crud.py` | PASS | 문법 이상 없음 |
| `app/database/init_db.py` | PASS | 문법 이상 없음 |
| `app/main.py` | PASS | 문법 이상 없음 |
| `app/routers/qa.py` | PASS | 문법 이상 없음 |
| `app/routers/ui.py` | PASS | 문법 이상 없음 |

**결과: PASS (정적 분석 기준)**

---

## 3. 코드 품질 검증

### 3-1. IPO 패턴 (`# --- Input ---` / `# --- Process ---` / `# --- Output ---`)

| 파일 | IPO 적용 | 비고 |
|------|---------|------|
| `scripts/ingest.py` | PASS | 모든 함수에 3구간 주석 적용 |
| `mcp/mcp_server.py` | PASS | 9개 도구 함수 모두 IPO 주석 포함 |
| `app/services/mcp_agent_service.py` | PASS | MCPToolWrapper, MCPAgentService 메서드 전체 적용 |
| `app/services/llm_service.py` | PASS | 모든 메서드에 IPO 주석 적용 |
| `app/services/qa_service.py` | PASS | hybrid_search, get_ai_answer 적용 |
| `app/services/vector_service.py` | PASS | search_unstructured, get_doc_count 적용 |
| `app/database/connection.py` | PASS | execute, fetchall, fetchone, get_db_connection 적용 |
| `app/database/crud.py` | PASS | 전체 CRUD 함수 적용 |
| `app/database/init_db.py` | PASS | init_db 함수에 단계별 IPO 주석 포함 |
| `app/main.py` | PASS | 모듈 수준 IPO 주석 적용 |
| `app/routers/qa.py` | PASS | query_qa, query_agent 적용 |
| `app/routers/ui.py` | PASS | 3개 엔드포인트 함수 적용 |

**결과: PASS**

### 3-2. 하십시오체 Docstring

전체 Python 파일의 모든 함수·클래스 docstring을 점검하였습니다.

- 모든 함수 설명이 `~합니다.` / `~반환합니다.` / `~수행합니다.` 형식의 하십시오체 적용 확인.
- Args, Returns, Raises 절도 동일 문체로 작성.

**결과: PASS**

### 3-3. 싱글톤 패턴 선언

| 싱글톤 변수 | 선언 파일 | 결과 |
|------------|---------|------|
| `llm_service` | `app/services/llm_service.py` 최하단 | PASS |
| `vector_service` | `app/services/vector_service.py` 최하단 | PASS |
| `qa_service` | `app/services/qa_service.py` 최하단 | PASS |
| `mcp_agent_service` | `app/services/mcp_agent_service.py` 최하단 | PASS |

**결과: PASS**

### 3-4. 타입 힌트 (Python 3.9+ 내장 타입)

- `list[dict]`, `dict | None`, `tuple | None`, `str | None` 등 Python 3.10+ union 표기법 사용.
- 모든 함수 파라미터와 반환형에 타입 힌트 적용.
- `from __future__ import annotations` 없이 Python 3.10+ 문법 직접 사용 — Python 3.9 환경에서는 실행 오류 발생 가능.

**결과: CONDITIONAL_PASS** (Python 3.10+ 전제로 작성됨. 독자 환경이 3.10 미만이면 오류 발생 주의)

---

## 4. 핵심 로직 검증

### 4-1. `scripts/ingest.py` — Vision LLM 파이프라인

| 함수 | 구현 여부 | 비고 |
|------|---------|------|
| `parse_filename_metadata(filename)` | PASS | 파일명에서 부서·버전 추출 |
| `pdf_page_to_base64(pdf_path, page_num)` | PASS | fitz(pymupdf)로 PNG 캡처 후 base64 인코딩 |
| `parse_page_with_vision(base64_image, llm_base_url, vision_model)` | PASS | Ollama `/api/generate` REST 호출, 한국어 Markdown 추출 프롬프트 포함 |
| `chunk_text(text, source, department, version, chunk_size, overlap)` | PASS | `## 헤더` 기반 섹션 분리 + overlap fallback 슬라이딩 윈도우 |
| `ingest()` | PASS | 5단계 파이프라인 ([1/5]~[5/5]) 순서대로 구현 |

**결과: PASS**

### 4-2. `mcp/mcp_server.py` — FastMCP 도구 9개 등록

| 도구 | 등록 여부 |
|------|---------|
| `list_employees` | PASS |
| `get_employee` | PASS |
| `list_leaves` | PASS |
| `get_leave_balance` | PASS |
| `use_leave` | PASS |
| `list_sales` | PASS |
| `create_sale` | PASS |
| `get_sales_period` | PASS |
| `get_sales_by_dept` | PASS |

모든 도구에 `@mcp.tool()` 데코레이터 적용, `FastMCP("Company DB Assistant")` 인스턴스에 등록. `mcp.run(transport="stdio")` 호출로 stdio 모드 실행 확인.

**결과: PASS — 9개 도구 전체 등록 확인**

### 4-3. `app/services/mcp_agent_service.py` — MCPToolWrapper / MCPAgentService

| 구현 항목 | 결과 | 비고 |
|---------|------|------|
| `MCPToolWrapper.__init__(session, tool_info)` | PASS | tool_info.name, description 저장 |
| `MCPToolWrapper._call(**kwargs)` | PASS | `session.call_tool()` 비동기 호출, 텍스트 결과 반환 |
| `MCPToolWrapper._sync_call(tool_input)` | PASS | JSON 파싱 후 asyncio.run 또는 ThreadPoolExecutor로 동기화 |
| `MCPToolWrapper.to_langchain_tool()` | PASS | `Tool(name, description, func=self._sync_call)` 반환 |
| `REACT_PROMPT` | PASS | `PromptTemplate.from_template` 사용, `{tools}` / `{tool_names}` / `{input}` / `{agent_scratchpad}` 포함 |
| `MCPAgentService.run_agent(query)` | PASS | StdioServerParameters → ClientSession → MCPToolWrapper → create_react_agent → AgentExecutor |
| `run_agent` 반환 구조 | PASS | `{"answer": str, "steps": [{"tool", "input", "output"}]}` |
| 싱글톤 `mcp_agent_service` | PASS | 모듈 최하단 선언 |

**결과: PASS**

### 4-4. `app/services/llm_service.py` — ChatOllama/ChatOpenAI 분기 + think 태그 제거

| 구현 항목 | 결과 | 비고 |
|---------|------|------|
| `LLM_PROVIDER=ollama` 분기 | PASS | `ChatOllama` 초기화 |
| `LLM_PROVIDER=openai` 분기 | PASS | `ChatOpenAI` 초기화 |
| `<think>...</think>` 태그 제거 | PASS | `re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)` |
| Jinja2 프롬프트 렌더링 | PASS | `app/prompts/` 디렉토리 기반 FileSystemLoader |
| 싱글톤 `llm_service` | PASS | 모듈 최하단 선언 |

**결과: PASS**

### 4-5. `chunk_text()` — 헤더 기반 청킹 + overlap fallback

`## ` 접두사 라인 기준으로 섹션을 분리한 후:
- 섹션 길이 ≤ `chunk_size`: 그대로 단일 청크
- 섹션 길이 > `chunk_size`: `start = end - overlap` 슬라이딩 윈도우로 분할

헤더가 없는 텍스트는 전체를 단일 섹션으로 처리하는 fallback 구현 확인.

**결과: PASS**

---

## 5. 독립 실행 원칙 검증

| 항목 | 확인 결과 |
|------|---------|
| CH07 산출물 복사 코드/주석 없음 | PASS — "CH07에서 복사", "shutil.copy" 등 표현 없음 |
| `scripts/ingest.py` 자체 ChromaDB 생성 | PASS — `Chroma.from_documents()` + `persist_directory=CHROMA_DIR_ABS` 로 자체 생성 |
| `data/docs/` 자체 PDF 포함 구조 | PASS — `.gitkeep`으로 폴더 보유, README에 PDF 복사 안내 |
| PostgreSQL 자체 컨테이너 (`docker-compose.yml`) | PASS — `postgres:16` 이미지 사용 |
| DB 초기화 스크립트 자체 포함 | PASS — `app/database/init_db.py` 독립 실행 가능 |

**결과: PASS**

---

## 6. 수정 사항

### 수정 1: `requirements.txt` — `langchain-chroma` 패키지 누락 추가

**수정 전:**
```
# 벡터 DB
chromadb>=0.5.0
```

**수정 후:**
```
# 벡터 DB
chromadb>=0.5.0
langchain-chroma>=0.1.0
```

**수정 이유:**
- `scripts/ingest.py` 에서 `from langchain_chroma import Chroma` 사용
- `app/services/vector_service.py` 에서 `from langchain_chroma import Chroma` 사용
- `langchain-chroma`는 `chromadb`와 별개 패키지로 명시적 선언 필요
- 미선언 시 `pip install -r requirements.txt` 후 실행 시 `ImportError` 발생

**적용 파일:** `/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/수동/examples/CH08_MCP_QA에이전트/requirements.txt`

---

## 7. 종합 의견

CH08 MCP Q&A 에이전트 예제 프로젝트는 명세 대비 높은 완성도를 보입니다.

**강점:**
- 파일 구조가 명세와 100% 일치합니다.
- 모든 Python 파일에 하십시오체 docstring과 Args/Returns/Raises 절이 체계적으로 작성되어 있습니다.
- IPO 구간 주석(`# --- Input ---`, `# --- Process ---`, `# --- Output ---`)이 전체 코드에 일관되게 적용되어 있습니다.
- FastMCP 9개 도구 등록, MCPAgentService의 ReAct Agent 파이프라인, Vision LLM 파싱 파이프라인 모두 명세 요구사항을 충족합니다.
- CH07 산출물에 의존하지 않는 완전한 독립 실행 구조입니다.
- 에러 메시지가 `docker-compose up -d 명령으로 컨테이너를 실행하십시오.`, `pip install -r requirements.txt를 실행하십시오.` 등 독자 친화적 한국어로 작성되어 있습니다.

**주의 사항:**
- Python 3.10+ 문법(`dict | None`, `list[dict]` 등)을 `from __future__ import annotations` 없이 사용하고 있어 Python 3.9 이하 환경에서는 실행 불가합니다. README에 Python 3.10+ 요구사항을 명시하는 것을 권장합니다.
- `requirements.txt`에 `langchain-chroma` 누락이 있었으며, 검증 과정에서 즉시 수정 완료하였습니다.

---

## 검증 항목 요약

| # | 항목 | 필수/권장 | 결과 | 비고 |
|---|------|---------|------|------|
| 1 | `pip install -r requirements.txt` 성공 (정적 분석) | 필수 | PASS | langchain-chroma 누락 수정 후 |
| 2 | 파일 구조 명세 일치 | 필수 | PASS | 32개 파일 전체 일치 |
| 3 | 모든 함수에 한국어 docstring 존재 | 필수 | PASS | 하십시오체 + Args/Returns/Raises 완비 |
| 4 | 코드 생략(`...`, `# 생략`) 없음 | 필수 | PASS | 완전 구현 코드 확인 |
| 5 | FastMCP 도구 9개 등록 | 필수 | PASS | 명세 도구명 전체 일치 |
| 6 | MCPToolWrapper + run_agent() 구현 | 필수 | PASS | ReAct Agent 파이프라인 완전 구현 |
| 7 | Vision LLM 파이프라인 구현 | 필수 | PASS | pdf_page_to_base64, parse_page_with_vision, chunk_text 전체 구현 |
| 8 | 독립 실행 원칙 준수 | 필수 | PASS | CH07 산출물 의존 없음 |
| 9 | 타입 힌트 Python 3.9+ 내장 타입 사용 | 권장 | CONDITIONAL_PASS | Python 3.10+ 문법 사용 (3.9 환경 주의) |
| 10 | 에러 메시지 한국어 독자 친화적 | 권장 | PASS | 안내 문구 한국어로 작성 |
| 11 | IPO 구간 주석 존재 | 권장 | PASS | 전체 파일 일관 적용 |
| 12 | 싱글톤 패턴 4개 서비스 선언 | 권장 | PASS | llm, vector, qa, mcp_agent 서비스 전체 |

- 총 검증 항목: 12개
- 통과: 11개 (PASS)
- 조건부 통과: 1개 (CONDITIONAL_PASS — 타입 힌트 Python 버전 주의)
- 실패: 0개
- 시도 횟수: 1/2
