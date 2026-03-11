# CH07 예제 코드 명세 — RAG Q&A 엔진 구현

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. FastAPI 웹앱으로 CH06 ChromaDB 위에 RAG Q&A 엔진 서비스 구축.
인텐트 라우팅(Jinja2 프롬프트 템플릿) → 벡터 검색 → LLM 답변 생성 → 웹 UI 출력 전체 파이프라인.

참고 원본: `legacy/ex02` (FastAPI + LangChain + ChromaDB 기반 사내 AI 비서)

## 2. 디렉토리 구조

```
CH07_RAG_QA엔진구현/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py                    ← FastAPI 앱 + uvicorn 실행
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ui.py                  ← HTML 페이지 라우터 (대시보드, QA 화면)
│   │   └── qa.py                  ← REST API (/admin/qa/query)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py         ← LLM 초기화 (ChatOllama / ChatOpenAI)
│   │   ├── vector_service.py      ← ChromaDB + Ollama 임베딩 검색
│   │   └── qa_service.py          ← 인텐트 라우팅 + RAG 파이프라인 오케스트레이터
│   ├── prompts/
│   │   ├── router_prompt.j2       ← 질문 의도 분석 (structured/unstructured/hybrid)
│   │   └── answer_prompt.j2       ← 최종 답변 생성
│   ├── templates/
│   │   ├── base.html              ← 공통 레이아웃 (사이드바, 헤더)
│   │   ├── dashboard.html         ← 메인 대시보드 (시스템 상태)
│   │   └── qa.html                ← 채팅 UI (AJAX 질문 전송, 출처 표시)
│   └── static/
│       ├── css/
│       │   └── qa.css
│       └── js/
│           └── qa.js              ← 비동기 질문 전송, 응답 렌더링
├── scripts/
│   └── ingest.py                  ← PDF 파싱 → 청킹 → ChromaDB 저장
└── data/
    ├── docs/                      ← 부서별 PDF 파일 (HR, OPS, IT 등)
    │   ├── HR_취업규칙_v1.0.pdf
    │   ├── HR_정보보안서약서.pdf
    │   └── OPS_신규서비스_런칭전략.pdf
    ├── pages/                     ← ingest.py가 저장하는 페이지 이미지
    │   └── HR_취업규칙_v1.0/
    │       ├── page_1.png
    │       └── page_2.png
    ├── markdown/                  ← ingest.py가 저장하는 Vision LLM 결과 MD
    │   └── HR_취업규칙_v1.0.md
    └── chroma_db/                 ← scripts/ingest.py 실행 후 자동 생성
        └── .gitkeep
```

## 3. 파일별 함수 명세

### `app/main.py`

```python
"""
CH07 RAG Q&A 엔진 — FastAPI 앱 진입점.

라우터 등록:
    /             → /admin/dashboard 리다이렉트
    /admin/qa/*   → Q&A REST API (qa_router)
    /admin/*      → HTML 페이지 (ui_router)
    /static/*     → 정적 파일

실행:
    python -m app.main
    uvicorn app.main:app --reload
"""

app = FastAPI(title="RAG Q&A 엔진", version="1.0")
# StaticFiles, 라우터 등록, 루트 리다이렉트
```

### `app/routers/ui.py`

```python
"""HTML 페이지 라우터 — Jinja2 템플릿 렌더링."""

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """메인 대시보드 (ChromaDB 문서 수, 상태 표시)."""

@router.get("/admin/qa", response_class=HTMLResponse)
async def qa_page(request: Request):
    """채팅 Q&A 화면."""
```

### `app/routers/qa.py`

```python
"""Q&A REST API 라우터."""

class QueryRequest(BaseModel):
    query: str

@router.post("/admin/qa/query")
async def query_qa(request: QueryRequest):
    """
    질문 처리 엔드포인트.
    Input : {"query": "연차 신청 방법이 뭔가요?"}
    Process:
        1. qa_service.hybrid_search(query) → 검색 결과
        2. qa_service.get_ai_answer(query, results) → 답변 생성
    Output : {
        "query": str,
        "answer": str,
        "route": "unstructured|hybrid",
        "unstructured_data": [
            {
                "content": str,
                "source": str,
                "score": float,
                "page_num": int,       # ChromaDB 메타데이터에서 추출
                "page_image": str,     # 페이지 이미지 경로 (없으면 "")
                "section_title": str,  # 섹션 제목 (없으면 "")
            }
        ]
    }
    """
```

### `app/services/llm_service.py`

```python
"""
LLM 초기화 서비스. ollama/openai 전환 가능.
Jinja2 프롬프트 템플릿 렌더링 담당.
"""

class LLMService:
    def __init__(self):
        """
        환경변수 LLM_PROVIDER(ollama|openai), LLM_MODEL_NAME으로 초기화.
        - ollama: ChatOllama(base_url, model)
        - openai: ChatOpenAI(model, api_key, temperature)
        Jinja2 Environment는 app/prompts/ 디렉토리를 로더로 사용.
        """

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """Jinja2 템플릿 렌더링. router_prompt.j2, answer_prompt.j2 지원."""

    def invoke(self, prompt: str) -> str:
        """
        LLM 호출 후 문자열 반환.
        - ChatOllama/ChatOpenAI 모두 .invoke() 통일
        - DeepSeek-R1 등 <think>...</think> 사고 과정 자동 제거
        """

    def generate_answer(self, query: str, context: str) -> str:
        """answer_prompt.j2 렌더링 후 LLM 호출."""

    def classify_intent(self, query: str) -> dict:
        """
        router_prompt.j2 렌더링 후 LLM 호출 → JSON 파싱.
        Output: {"route": "unstructured|hybrid", "reason": str}
        실패 시: {"route": "hybrid", "reason": "분석 오류"}
        """

# 싱글톤
llm_service = LLMService()
```

### `app/services/vector_service.py`

```python
"""
ChromaDB 벡터 검색 서비스.
CH06에서 생성한 ChromaDB(nomic-embed-text 임베딩)를 연결.
"""

VECTOR_DB_DIR = "data/chroma_db"

class VectorService:
    def __init__(self):
        """
        OllamaEmbeddings(model=EMBED_MODEL) 초기화.
        Chroma(persist_directory, embedding_function) 연결.
        data/chroma_db가 없으면 경고만 출력 (지연 초기화 지원).
        """

    def search_unstructured(self, query: str, k: int = 3) -> list[dict]:
        """
        비정형 문서 유사도 검색.
        Input : 검색 질문, 반환 문서 수 k
        Process: similarity_search_with_score(query, k)
        Output : [{"content": str, "source": str, "score": float}]
        """

# 싱글톤
vector_service = VectorService()
```

### `app/services/qa_service.py`

```python
"""
RAG Q&A 오케스트레이터.
인텐트 라우팅 → 벡터 검색 → LLM 답변 생성 파이프라인.
"""

class QAService:
    def hybrid_search(self, query: str) -> dict:
        """
        인텐트 라우팅 적용 검색.
        Input : 사용자 질문
        Process:
            1. llm_service.classify_intent(query) → route 결정
            2. route == "unstructured" or "hybrid": vector_service.search_unstructured()
        Output : {
            "query": str,
            "unstructured": [{"content": str, "source": str, "score": float}],
            "route": str
        }
        """

    def get_ai_answer(self, query: str, search_results: dict) -> str:
        """
        검색 결과로 컨텍스트 구성 후 LLM 답변 생성.
        Input : 질문, hybrid_search() 결과
        Process:
            1. unstructured 결과를 "[사내 문서 내용]" 포맷으로 context 구성
            2. llm_service.generate_answer(query, context) 호출
        Output : 답변 문자열 (출처 정보 포함)
        """

# 싱글톤
qa_service = QAService()
```

### `app/prompts/router_prompt.j2`

```jinja2
{# 질문 의도 분석 — 검색 전략 결정 #}
당신은 사내 AI 비서의 질문 분석기(Router)입니다.
사용자의 [질문]을 분석하여 어떤 데이터 소스를 검색해야 할지 결정하세요.

[데이터 소스]
- unstructured: 사내 규정, 가이드라인, 정책 문서 검색이 필요한 경우
- hybrid: 명확히 구분하기 어렵거나 복합 정보가 필요한 경우

[출력 형식] JSON만 출력:
{"route": "unstructured|hybrid", "reason": "..."}

[질문]
{{ query }}
```

### `app/prompts/answer_prompt.j2`

```jinja2
{# 최종 답변 생성 프롬프트 #}
당신은 사내 AI 비서입니다.
아래 [컨텍스트] 정보를 바탕으로 [질문]에 친절하고 정확하게 답변하세요.

[규칙]
- 반드시 한국어로 답변하세요.
- 정보가 부족하면 아는 범위에서만 답변하고 추측하지 마세요.
- 문서 내용은 핵심을 요약하여 답변하세요.

[컨텍스트]
{{ context }}

[질문]
{{ query }}

답변:
```

### `app/templates/qa.html`

채팅 UI 화면. 주요 구성:
- 질문 입력창 + 전송 버튼
- AJAX `POST /admin/qa/query` 전송 (`qa.js`)
- 응답 영역:
  - 답변 텍스트
  - 출처 카드 (source, score 표시)
  - **근거 패널**: 각 출처 카드 클릭 시 `page_image` 썸네일 + `page_num` 표시
    - 이미지 클릭 시 원본 크기 모달
    - Markdown 섹션(`section_title`) 하이라이트 표시

### `app/static/js/qa.js`

```javascript
// 비동기 질문 전송
async function sendQuery(query) {
    // POST /admin/qa/query → {answer, route, unstructured_data}
    // answer 텍스트 렌더링
    // unstructured_data 출처 카드 렌더링:
    //   - source, score 표시
    //   - page_image 있으면 썸네일 이미지 표시
    //   - page_num, section_title 표시
}

// 이미지 모달 표시
function showImageModal(imagePath) {
    // 페이지 이미지 원본 크기 모달 열기
}
```

## 3-1. `scripts/ingest.py` 명세

```python
"""
CH07 문서 인제스트 스크립트.

PDF 페이지를 이미지로 캡처 → Vision LLM이 Markdown으로 파싱 →
헤더 기반 청킹 → Ollama 임베딩 → ChromaDB 저장.
페이지 이미지(data/pages/)와 Markdown(data/markdown/)을 저장하여
채팅 UI에서 답변 근거를 이미지+MD로 표시할 수 있습니다.

파이프라인:
    PDF 페이지 → PNG 저장(data/pages/) + base64 → Vision LLM → MD 저장(data/markdown/)
    → ## 헤더 기반 청킹 (500자 초과 시 overlap 분할)
    → OllamaEmbeddings → ChromaDB (page_num, page_image 메타데이터 포함)

청킹 전략:
    ## 헤더 있음: 섹션 단위 분할 (500자 초과 시 overlap 50자 슬라이딩)
    ## 헤더 없음: 500자 / 50자 overlap 고정 분할 (fallback)

메타데이터:
    source, department, version, section_title, chunk_index, page_num, page_image

실행:
    python scripts/ingest.py                          # data/docs/ 전체 인제스트
    python scripts/ingest.py --file HR_취업규칙_v1.0.pdf  # 파일 지정 인제스트
    python scripts/ingest.py --reset                  # DB 초기화 후 전체 재인제스트

사전 준비:
    ollama pull nomic-embed-text
    ollama pull llava:7b       # Vision LLM (저사양: moondream, 고사양: llava:13b)
"""

def parse_filename_metadata(filename: str) -> dict:
    """
    파일명에서 부서/문서명/버전을 추출.
    HR_취업규칙_v1.0.pdf → {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}
    매핑 실패 시 {"department": "General", "doc_name": filename, "version": "unknown"}.
    """

def pdf_page_to_base64(pdf_path: str, page_num: int, save_dir: str | None = None) -> tuple[str, str | None]:
    """
    fitz(PyMuPDF)로 PDF 특정 페이지를 PNG 이미지로 렌더링 후 base64 인코딩 반환.
    save_dir 지정 시 data/pages/{stem}/page_{page_num+1}.png 로 저장.

    Input : pdf_path, page_num (0-based), save_dir (저장 폴더, None이면 저장 생략)
    Process: fitz.open() → page.get_pixmap(dpi=150) → PNG bytes → base64
             save_dir 지정 시 PNG 파일 저장
    Output : (base64 문자열, 저장된 이미지 경로 또는 None)
    """

def parse_page_with_vision(base64_image: str, llm_base_url: str, vision_model: str) -> str:
    """
    Vision LLM에 페이지 이미지를 전달하여 Markdown 텍스트로 변환.

    Input : base64 이미지, Ollama 서버 URL, Vision 모델명
    Process:
        ChatOllama(model=vision_model).invoke([
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                {"type": "text", "text": "이 문서 페이지를 Markdown 형식으로 변환하세요..."}
            ])
        ])
    Output : Markdown 문자열
    """

def save_markdown(markdown_text: str, pdf_path: str, save_dir: str) -> str:
    """
    Vision LLM 결과 Markdown을 data/markdown/{stem}.md 로 저장.

    Input : markdown_text, pdf_path (원본 PDF 경로), save_dir
    Output : 저장된 MD 파일 경로
    """

def chunk_text(
    text: str,
    source: str,
    department: str,
    version: str,
    page_image_map: dict[int, str],  # page_num → 이미지 경로
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    ## 헤더 기반 청킹 + fallback 고정 크기 청킹.

    Input:
        text: Vision LLM이 생성한 전체 Markdown (전 페이지 합본)
        source: 원본 파일명
        department, version: 파일명 파싱 메타데이터
        page_image_map: {page_num: 이미지 경로} (채팅 UI 근거 표시용)
        chunk_size: 최대 문자 수 (기본 500)
        overlap: 슬라이딩 겹침 문자 수 (기본 50)

    Process:
        ## 헤더(#{1,3}) 감지:
          - 헤더 있음: 섹션 단위 분할
            - 섹션 ≤ chunk_size → 섹션 전체를 하나의 청크
            - 섹션 > chunk_size → (chunk_size - overlap) 간격 슬라이딩
          - 헤더 없음 → (chunk_size - overlap) 간격 슬라이딩 (fallback)
        각 청크 메타데이터에 page_num(청크 시작 페이지 추정), page_image(해당 페이지 이미지 경로) 포함

    Output: [
        {
            "text": str,
            "metadata": {
                "source": str,
                "department": str,
                "version": str,
                "section_title": str,   # 헤더명 또는 "본문"
                "chunk_index": int,
                "page_num": int,         # 청크 시작 페이지 번호 (1-based)
                "page_image": str,       # 해당 페이지 이미지 경로 (없으면 "")
            }
        }
    ]
    """

def ingest(target_file: str | None = None, reset: bool = False) -> None:
    """
    전체 인제스트 파이프라인.

    Args:
        target_file: 특정 파일명 지정 시 해당 파일만 인제스트. None이면 전체.
        reset: True이면 data/chroma_db/ 삭제 후 재인제스트.

    [1/5] PDF 탐색     — data/docs/ 하위 *.pdf (target_file 지정 시 해당 파일만)
    [2/5] 페이지 캡처  — fitz로 각 페이지 → PNG 저장(data/pages/) + base64
    [3/5] Vision 파싱  — Vision LLM → Markdown 저장(data/markdown/) + 합본
    [4/5] 청킹         — chunk_text() (헤더 기반 + overlap fallback, page_num/page_image 메타데이터 포함)
    [5/5] 임베딩+저장  — OllamaEmbeddings → Chroma → data/chroma_db/

    Input : data/docs/ 폴더의 PDF 파일
    Output:
        data/pages/{stem}/page_N.png  (페이지 이미지)
        data/markdown/{stem}.md       (Vision LLM Markdown)
        data/chroma_db/               (ChromaDB 영구 저장소)
    """

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=None, help="특정 PDF 파일명 지정 (예: HR_취업규칙_v1.0.pdf)")
    parser.add_argument("--reset", action="store_true", help="ChromaDB 초기화 후 재인제스트")
    args = parser.parse_args()
    ingest(target_file=args.file, reset=args.reset)
```

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt

# PDF 인제스트 (전체)
python scripts/ingest.py

# 파일 지정 인제스트 (저사양 환경: 한 파일씩 테스트 권장)
python scripts/ingest.py --file HR_취업규칙_v1.0.pdf

# DB 초기화 후 재인제스트
python scripts/ingest.py --reset

# 서버 실행
python -m app.main
# 또는
uvicorn app.main:app --reload

# 브라우저: http://127.0.0.1:8000
```

**기대 동작**:
```
[브라우저] http://127.0.0.1:8000/admin/qa

질문 입력: "연차 신청 기한이 어떻게 되나요?"

[응답]
라우팅: unstructured (사내 문서 검색)

답변:
연차는 사용 전월 말일까지 팀장에게 신청서를 제출해야 합니다...

[출처]
- HR_취업규칙_v1.0.pdf (유사도: 0.87)
- HR_정보보안서약서.pdf (유사도: 0.72)
```

## 5. 의존성

```
# FastAPI
fastapi>=0.111.0
uvicorn>=0.29.0
jinja2>=3.1.0
python-multipart>=0.0.9

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

## 7-1. .env.example

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

# 임베딩 모델 (CH06과 동일)
EMBED_MODEL=nomic-embed-text

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs
```

## 7. 독립 실행 원칙

CH07은 이전 챕터 산출물에 의존하지 않습니다.

| 항목 | 처리 방식 |
|------|---------|
| PDF 문서 | `data/docs/` 폴더에 자체 포함 |
| ChromaDB | `scripts/ingest.py` 실행으로 자체 생성 |
| 임베딩 모델 | Ollama `nomic-embed-text` (로컬 설치 필요) |
| 청킹 패턴 | CH06과 동일 (## 헤더 기반 + overlap fallback) |

## 8. CH08 연결

CH08은 CH07과 같은 독립 실행 구조를 가지며, 추가로 PostgreSQL + MCP Agent를 도입:
- `scripts/ingest.py` 동일 패턴으로 자체 ChromaDB 생성
- `mcp/mcp_server.py` FastMCP 서버 (DB 도구 9개)
- `app/services/mcp_agent_service.py` LangChain ReAct Agent
