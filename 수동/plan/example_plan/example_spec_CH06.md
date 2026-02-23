# CH06 예제 코드 명세 — 벡터 DB 구축

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조.
PDF → (규칙 기반 파싱 또는 Vision LLM) → Markdown → 청킹 → 임베딩 → ChromaDB 저장 전체 파이프라인.

## 2. 디렉토리 구조

```
CH06_벡터DB구축/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── create_sample_pdfs.py         ← reportlab으로 샘플 PDF 자동 생성 스크립트
│   ├── HR_취업규칙_v1.0.pdf          ← create_sample_pdfs.py 실행 후 생성됨
│   └── FIN_매출현황_v1.0.pdf         ← create_sample_pdfs.py 실행 후 생성됨
├── src/
│   ├── __init__.py
│   ├── main.py                       ← 엔드투엔드 파이프라인 실행
│   ├── extractor.py                  ← 규칙 기반 PDF 파싱 (pdfplumber)
│   ├── vision_extractor.py           ← Vision LLM 기반 PDF → Markdown (AI 교정)
│   ├── chunker.py                    ← Markdown 구조 인식 청킹
│   ├── embedder.py                   ← Ollama 임베딩 (requests 직접 호출)
│   └── store.py                      ← ChromaDB 영속 저장 및 검색
└── outputs/
    ├── markdown/                     ← 전처리 완료 Markdown 저장
    │   └── .gitkeep
    └── chroma_db/                    ← ChromaDB 영속 저장소 (자동 생성)
        └── .gitkeep
```

## 3. 파일별 함수 명세

### `data/create_sample_pdfs.py`

```python
"""
실습용 샘플 PDF 자동 생성 스크립트.
reportlab 사용. 처음 1회만 실행 필요.

생성 파일:
  - HR_취업규칙_v1.0.pdf  : 텍스트+표 혼합, 3페이지 (규칙 기반 파싱 실습용)
  - FIN_매출현황_v1.0.pdf : 다중 컬럼 레이아웃, 2페이지 (Vision LLM 실습용)

실행: python data/create_sample_pdfs.py
"""

def create_hr_policy_pdf(output_path: str) -> None:
    """
    HR 취업규칙 PDF 생성 (3페이지).
    - 페이지1: 제목 + 연차 규정 (조항 형식)
    - 페이지2: 보안 USB 정책 + 표 포함
    - 페이지3: 복리후생 규정
    네이밍: HR_취업규칙_v1.0.pdf
    """

def create_finance_pdf(output_path: str) -> None:
    """
    매출 현황 PDF 생성 (2페이지, 다중 컬럼).
    - 페이지1: 결재란 (상단) + 2단 레이아웃 (좌: 요약, 우: 부서별 매출)
    - 페이지2: 분기별 매출 표
    네이밍: FIN_매출현황_v1.0.pdf
    """

def main() -> None:
    """두 PDF 생성 후 파일 크기 및 경로 출력."""
```

### `src/extractor.py`

```python
def extract_text_pdfplumber(pdf_path: str) -> list[dict]:
    """
    pdfplumber로 PDF 페이지별 텍스트 추출 (규칙 기반, 표 포함 PDF에 강함).
    Input : PDF 파일 경로
    Process:
      - pdfplumber.open() → 페이지 순회 → extract_text()
      - 표 감지 시 extract_table()로 셀 내용 보존
    Output : [{"page": int, "text": str, "source": str, "has_table": bool}]
    """

def extract_text_pymupdf(pdf_path: str) -> list[dict]:
    """
    PyMuPDF로 PDF 페이지별 텍스트 추출 (빠른 추출, 비교용).
    Input : PDF 파일 경로
    Process: fitz.open() → 페이지 순회 → get_text("text")
    Output : [{"page": int, "text": str, "source": str}]
    """

def is_complex_layout(pages: list[dict], threshold: float = 0.3) -> bool:
    """
    규칙 기반 파싱으로 추출된 텍스트가 충분한지 판단.
    - 페이지당 평균 글자 수가 threshold*(전체 기대 글자 수) 미만이면 복합 레이아웃으로 판단
    - True → Vision LLM 사용 권장, False → 규칙 기반으로 충분
    """

def parse_filename_metadata(pdf_path: str) -> dict:
    """
    파일명에서 메타데이터 자동 추출.
    HR_취업규칙_v1.0.pdf → {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}
    """
```

### `src/vision_extractor.py`

```python
"""
Vision LLM 기반 PDF → Markdown 변환기.
규칙 기반 파싱이 실패한 복합 레이아웃(다단, 도해, 스캔본)에서만 사용.

흐름:
  PDF 파일 → 페이지별 이미지 캡처(fitz) → Vision LLM 호출 → Markdown 텍스트 반환
"""

def pdf_page_to_image(pdf_path: str, page_num: int, dpi: int = 150) -> bytes:
    """
    PDF 특정 페이지를 PNG 이미지로 변환.
    Input : PDF 경로, 페이지 번호 (0-indexed), 해상도
    Process: fitz.open() → get_pixmap(dpi) → tobytes("png")
    Output : PNG 이미지 bytes
    """

def image_to_base64(image_bytes: bytes) -> str:
    """이미지 bytes → base64 인코딩 문자열."""

def call_vision_llm(image_base64: str, page_num: int) -> str:
    """
    Vision LLM에 이미지 + 프롬프트 전달 → Markdown 텍스트 반환.
    Input : base64 이미지, 페이지 번호
    Process:
      - LLM_PROVIDER=ollama → POST http://localhost:11434/api/generate
        (model: LLM_MODEL_NAME, images: [base64])
      - LLM_PROVIDER=openai → OpenAI Chat Completions API
        (model: LLM_MODEL_NAME, content: [text, image_url])
      - 프롬프트: "이 PDF 페이지의 내용을 Markdown 형식으로 변환해주세요.
                   표는 Markdown 표(|)로, 제목은 #으로, 목록은 -으로 표현하세요."
    Output : Markdown 텍스트 문자열
    """

def extract_pdf_to_markdown(
    pdf_path: str,
    output_dir: str = "./outputs/markdown"
) -> str:
    """
    PDF 전체를 Vision LLM으로 Markdown 변환 후 파일 저장.
    Input : PDF 경로, 출력 디렉토리
    Process: 페이지별 이미지 캡처 → call_vision_llm() → 페이지 결합 → .md 파일 저장
    Output : 저장된 Markdown 파일 경로
    네이밍: HR_취업규칙_v1.0.md (PDF와 동일한 이름, 확장자만 변경)
    """
```

### `src/chunker.py`

```python
def markdown_chunk(
    markdown_text: str,
    source: str,
    max_chunk_size: int = 500
) -> list[dict]:
    """
    Markdown 헤더(#) 기준 의미 단위 청킹.
    Input : Markdown 텍스트, 출처 파일명, 최대 청크 크기
    Process:
      1. ## 헤더 기준으로 섹션 분리
      2. 각 섹션이 max_chunk_size 초과 시 추가 분할 (빈 줄 기준)
      3. chunk_id: f"{source}_chunk_{index}"
      4. metadata: {"source": str, "section_title": str, "chunk_index": int, "department": str}
    Output : [{"chunk_id": str, "text": str, "metadata": dict}]
    """

def fixed_size_chunk(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50
) -> list[dict]:
    """
    고정 크기 청킹 (규칙 기반 추출 결과에 적용).
    Input : 페이지 목록, 청크 크기(자), 오버랩(자)
    Process: 전체 텍스트 이어붙이기 → 슬라이딩 윈도우
    Output : [{"chunk_id": str, "text": str, "metadata": dict}]
             metadata: {"source": str, "page": int, "chunk_index": int, "department": str}
    """

def compare_strategies(pages: list[dict], markdown_path: str) -> None:
    """
    fixed_size vs markdown_chunk 결과 비교 출력.
    (청크 수, 평균 길이, 섹션 보존 여부)
    """
```

### `src/embedder.py`

```python
def get_embedding_model(model_name: str = "nomic-embed-text") -> dict:
    """
    Ollama 임베딩 모델 정보 반환.
    Output : {"model": str, "dimension": int}
    """

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    텍스트 목록을 벡터로 변환 (Ollama REST API 직접 호출, LangChain 사용 금지).
    Input : 텍스트 리스트
    Process: POST {OLLAMA_BASE_URL}/api/embeddings, 10개씩 배치 처리
    Output : [[float, ...], ...]
    """

def embed_single(text: str) -> list[float]:
    """단일 텍스트 임베딩. 검색 쿼리용."""
```

### `src/store.py`

```python
def get_client(persist_dir: str = "./outputs/chroma_db") -> chromadb.Client:
    """ChromaDB 영속 클라이언트 반환 (chromadb.PersistentClient)."""

def create_collection(client: chromadb.Client, name: str = "rag_docs") -> chromadb.Collection:
    """get_or_create_collection + cosine 거리 메트릭."""

def add_documents(
    collection: chromadb.Collection,
    chunks: list[dict],
    embeddings: list[list[float]]
) -> int:
    """청크 + 임베딩 + 메타데이터 저장. 저장 문서 수 반환."""

def search(
    collection: chromadb.Collection,
    query_embedding: list[float],
    k: int = 3,
    filter_dept: str | None = None
) -> list[dict]:
    """
    유사도 검색.
    filter_dept: 부서 필터 (metadata.department 기준)
    Output : [{"text": str, "metadata": dict, "distance": float}]
    """

def get_collection_stats(collection: chromadb.Collection) -> dict:
    """컬렉션 통계 (총 문서 수, 부서별 분포) 반환."""
```

### `src/main.py`

```python
def run_pipeline(
    pdf_paths: list[str],
    use_vision: bool = False
) -> None:
    """
    전체 파이프라인 실행.
    use_vision=False (기본): 규칙 기반 파싱 → fixed_size 청킹
    use_vision=True        : Vision LLM → Markdown → markdown_chunk 청킹

    단계:
    [1/5] 샘플 PDF 확인 (없으면 create_sample_pdfs.py 실행 안내)
    [2/5] PDF 파싱 (규칙 기반 또는 Vision LLM)
    [3/5] 청킹
    [4/5] 임베딩 (nomic-embed-text)
    [5/5] ChromaDB 저장

    실행 후 테스트 검색 3회:
    - "연차 신청은 어떻게 하나요?"       → HR 문서에서 답변
    - "보안 USB 정책이 뭐야?"           → HR 문서에서 답변
    - "2024년 마케팅팀 매출 현황은?"    → FIN 문서에서 답변
    """

def main() -> None:
    """
    진입점.
    python src/main.py             # 규칙 기반 파싱
    python src/main.py --vision    # Vision LLM 파싱 (LLM_MODEL_NAME 필요)
    """
```

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt

# 0단계: 샘플 PDF 생성 (최초 1회)
python data/create_sample_pdfs.py
# → data/HR_취업규칙_v1.0.pdf, data/FIN_매출현황_v1.0.pdf 생성

# Ollama 모델 준비
ollama pull nomic-embed-text    # 임베딩 모델
ollama pull llava:7b            # Vision 모드 사용 시 (선택)

# 1단계: 규칙 기반 파이프라인 (빠름, Ollama LLM 불필요)
python src/main.py

# 2단계: Vision LLM 파이프라인 (복합 레이아웃 처리, LLM 필요)
python src/main.py --vision
```

**기대 출력 (규칙 기반)**:
```
[1/5] PDF 확인... ✓ HR_취업규칙_v1.0.pdf, FIN_매출현황_v1.0.pdf
[2/5] 규칙 기반 파싱 중... ✓ (5페이지 추출)
[3/5] 청킹 중... ✓ (총 24개 청크)
[4/5] 임베딩 중... ✓ (24개 벡터, 차원: 768)
[5/5] ChromaDB 저장 중... ✓ (24개 문서 → outputs/chroma_db/)

=== 검색 테스트 ===
Q: "연차 신청은 어떻게 하나요?"
결과 1 (거리 0.12): "연차는 사용 전월 말일까지..." [HR_취업규칙_v1.0.pdf, p.1]
```

## 5. 의존성

```
# PDF 처리
pymupdf>=1.24.0          # pdfplumber, Vision 모드 이미지 캡처
pdfplumber>=0.11.0       # 규칙 기반 파싱 (표 추출에 강함)
reportlab>=4.0.0         # 샘플 PDF 생성 (create_sample_pdfs.py)
Pillow>=10.0.0           # PDF→이미지 변환 보조

# 벡터 DB
chromadb>=0.5.0

# 임베딩 (Ollama REST 직접 호출)
requests>=2.31.0

# 유틸
python-dotenv>=1.0.0
```

## 6. .env.example

```
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# Vision LLM 모델명 (Vision 모드 사용 시: --vision 플래그)
# Ollama 예시: llava:7b, llava:13b
# OpenAI 예시: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=llava:7b

# Ollama 설정 (PROVIDER가 ollama인 경우 필요)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 설정 (PROVIDER가 openai인 경우 필요)
# OPENAI_API_KEY=sk-proj-...

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# ChromaDB 설정
CHROMA_PERSIST_DIR=./outputs/chroma_db
COLLECTION_NAME=rag_docs
```

## 7. CH05 → CH06 연결

| CH05 산출물 | CH06 사용 위치 |
|------------|--------------|
| 네이밍 규칙 `{부서}_{문서명}_{버전}.pdf` | `parse_filename_metadata()` 자동 파싱 |
| 메타데이터 스키마 (`department`, `version`) | `add_documents()` ChromaDB 메타데이터 |
| 전처리 정규화 규칙 | `extractor.py` 헤더/푸터 제거 로직 |

## 8. CH07 연결

`outputs/chroma_db/`를 CH07 `data/chroma_db/`로 복사:
```bash
cp -r outputs/chroma_db ../CH07_RAG_QA엔진구현/data/chroma_db
```
