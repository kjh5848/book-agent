# CH08 예제 코드 명세 — 통합 에이전트 설계 (MCP + RAG)

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. CH04 FastAPI + CH07 RAG Chain을 연결하는 질문 라우터 + 통합 에이전트.

## 2. 디렉토리 구조

```
CH08_통합에이전트MCP_RAG/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py           ← 시나리오 일괄 실행 진입점
│   ├── router.py         ← 질문 라우팅 (규칙 기반 + LLM 판단)
│   ├── mcp_client.py     ← CH04 FastAPI 호출 클라이언트
│   ├── rag_client.py     ← CH07 RAG Chain 래퍼
│   ├── agent.py          ← 통합 응답 합성
│   └── scenarios.py      ← 10개 테스트 시나리오 정의
└── outputs/
    ├── .gitkeep
    └── scenario_results.json   ← 실행 결과 저장 (자동 생성)
```

## 3. 파일별 함수 명세

### `src/router.py`

```python
QuestionType = Literal["structured", "unstructured", "hybrid"]

def classify_by_rules(question: str) -> QuestionType:
    """
    키워드 기반 규칙 라우팅 (빠름, 단순).
    Input : 사용자 질문 문자열
    Process:
      - DB 키워드 패턴: ["잔여 연차", "남은 연차", "매출", "실적", "인원수"]
      - 문서 키워드 패턴: ["규정", "정책", "방법", "기준", "가이드"]
      - 둘 다 포함: "hybrid"
    Output : "structured" | "unstructured" | "hybrid"
    """

def classify_by_llm(question: str) -> QuestionType:
    """
    LLM 판단 기반 라우팅 (정확, 느림).
    Input : 사용자 질문
    Process:
      Ollama에 분류 프롬프트 전송:
      "다음 질문이 DB 조회(structured), 문서 검색(unstructured),
       또는 두 가지 모두(hybrid) 중 어느 것인지 한 단어로 답하시오."
    Output : "structured" | "unstructured" | "hybrid"
    """

def route(
    question: str,
    use_llm: bool = False
) -> QuestionType:
    """
    라우팅 전략 선택 후 결과 반환.
    Input : 질문, LLM 사용 여부 (기본: 규칙 기반)
    Output : QuestionType
    """
```

### `src/mcp_client.py`

```python
def get_leave_balance(employee_name: str) -> dict:
    """
    CH04 FastAPI에서 직원 잔여 연차 조회.
    Input : 직원 이름
    Process: GET /employees?name={name} → GET /employees/{id}/leave-balance
    Output : {"employee_id": int, "name": str, "remaining_days": int}
    오류 시: {"error": "직원을 찾을 수 없습니다: {name}"}
    """

def get_sales_summary(department: str | None = None, quarter: str | None = None) -> dict:
    """
    CH04 FastAPI에서 매출 집계 조회.
    Input : 부서명 (선택), 분기 (선택, 예: "2024-Q4")
    Process: GET /sales/summary?department={dept}&quarter={q}
    Output : {"total": float, "by_department": dict, "by_quarter": dict}
    """
```

### `src/rag_client.py`

```python
def ask_rag(question: str, session_id: str = "default") -> dict:
    """
    CH07 RAG Chain을 직접 임포트하여 질의.
    Input : 질문, 세션 ID
    Process: build_multiturn_rag_chain() 호출 후 invoke
    Output : {"answer": str, "sources": list[dict]}
    """
```

### `src/agent.py`

```python
def integrated_response(
    question: str,
    question_type: QuestionType,
    session_id: str = "default"
) -> dict:
    """
    질문 유형에 따라 MCP + RAG를 호출하고 응답 합성.
    Input : 질문, 라우팅 결과, 세션 ID
    Process:
      - "structured"  : mcp_client만 호출 → 결과 포맷
      - "unstructured": rag_client만 호출
      - "hybrid"      : 두 클라이언트 병렬 호출 → LLM으로 통합 합성
    Output : {
      "question": str,
      "question_type": str,
      "answer": str,
      "sources": list,  # RAG 출처 (비정형 포함 시)
      "db_result": dict | None  # DB 조회 결과 (정형 포함 시)
    }
    """

def synthesize_hybrid_response(
    question: str,
    db_result: dict,
    rag_result: dict
) -> str:
    """
    DB + RAG 결과를 LLM으로 자연어 통합.
    프롬프트: "DB 조회 결과: {db_result}\n문서 검색 결과: {rag_answer}\n질문: {question}"
    """
```

### `src/scenarios.py`

```python
# 10개 시나리오 정의
SCENARIOS: list[dict] = [
    # 정형 (4개)
    {"id": 1, "type": "structured",   "question": "김철수 씨의 남은 연차는 며칠입니까?"},
    {"id": 2, "type": "structured",   "question": "2024년 4분기 마케팅팀 매출은 얼마입니까?"},
    {"id": 3, "type": "structured",   "question": "현재 영업팀 직원은 몇 명입니까?"},
    {"id": 4, "type": "structured",   "question": "이영희 씨는 연차를 몇 일 사용했습니까?"},

    # 비정형 (3개)
    {"id": 5, "type": "unstructured", "question": "연차 신청은 며칠 전에 해야 합니까?"},
    {"id": 6, "type": "unstructured", "question": "재택근무 신청 방법은 무엇입니까?"},
    {"id": 7, "type": "unstructured", "question": "비밀번호 변경 주기는 얼마입니까?"},

    # 복합 (3개)
    {"id": 8, "type": "hybrid", "question": "김철수 씨 남은 연차와 연차 사용 기준을 알려주십시오."},
    {"id": 9, "type": "hybrid", "question": "4분기 영업팀 실적과 성과 보상 기준은 무엇입니까?"},
    {"id": 10,"type": "hybrid", "question": "박지성 씨의 연차 현황과 신청 절차를 함께 설명해 주십시오."},
]

def run_all_scenarios(use_llm_router: bool = False) -> list[dict]:
    """10개 시나리오 순서대로 실행, 결과 수집 후 반환."""
```

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt

# 전제조건: CH04 docker-compose up 실행 중, CH07 ChromaDB 준비됨
python src/main.py

# 기대 출력:
# === 시나리오 실행 (총 10개) ===
# [1/10] 정형 질문: "김철수 씨의 남은 연차..."
#   라우팅: structured (규칙 기반)
#   DB 조회: 남은 연차 5일
#   답변: 김철수 씨의 남은 연차는 5일입니다.
# ...
# [8/10] 복합 질문: "김철수 씨 남은 연차와 연차 사용 기준..."
#   라우팅: hybrid
#   DB 조회: 남은 연차 5일
#   RAG 검색: 연차 사용 기준 문서 2건
#   합성 답변: 김철수 씨의 남은 연차는 5일이며, 연차 사용 기준은...
#
# 결과 저장: outputs/scenario_results.json
```

## 5. 의존성

```
requests>=2.31.0          # mcp_client (FastAPI 호출)
langchain>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
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

# 연결 서비스 설정
FASTAPI_BASE_URL=http://localhost:8000
CHROMA_PERSIST_DIR=../CH07_RAG_QA엔진구현/data/chroma_db
COLLECTION_NAME=rag_docs

# 라우터 설정
USE_LLM_ROUTER=false
```

## 7. 의존 챕터 연결

| 의존 | 연결 방법 |
|------|---------|
| CH04 FastAPI | `FASTAPI_BASE_URL`로 HTTP 호출 (docker-compose up 필요) |
| CH07 ChromaDB | `CHROMA_PERSIST_DIR`로 직접 접근 (파일 경로) |
| CH07 RAG Chain | `from sys import path; path.insert(0, '../CH07...')` 또는 패키지 복사 |
