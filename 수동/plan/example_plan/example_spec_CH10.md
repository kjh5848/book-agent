# CH10 예제 코드 명세 — RAG 시스템 튜닝

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. CH09 완성 파이프라인을 기반으로 청크 튜닝, ReRanker, OCR, 평가 체계 구축.

## 2. 디렉토리 구조

```
CH10_RAG시스템튜닝/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py               ← 튜닝 실험 일괄 실행
│   ├── tuning/
│   │   ├── __init__.py
│   │   ├── chunker_tuning.py ← 청크 크기 / k값 실험
│   │   ├── reranker.py       ← CrossEncoder ReRanker + Hybrid Search
│   │   └── prompts.py        ← 시스템 프롬프트 변형 비교
│   ├── ocr_hybrid.py         ← LLaVA + EasyOCR 이미지 PDF 처리
│   └── evaluator.py          ← 테스트셋 기반 정확도 평가
├── data/
│   ├── testset.json          ← 평가용 30개 Q&A 쌍
│   ├── scanned_sample.pdf    ← OCR 실습용 스캔 PDF 샘플
│   └── chroma_db/            ← CH06 ChromaDB 복사본
└── outputs/
    ├── .gitkeep
    ├── eval_results/
    │   └── .gitkeep
    └── tuning_logs/
        └── .gitkeep
```

## 3. 파일별 함수 명세

### `src/tuning/chunker_tuning.py`

```python
@dataclass
class ChunkExperiment:
    chunk_size: int
    overlap: int
    k: int
    strategy: str   # "fixed" | "semantic"

def run_chunk_experiment(
    experiment: ChunkExperiment,
    test_questions: list[str],
    ground_truth_docs: list[str]
) -> dict:
    """
    청킹 설정 변경 후 검색 정확도 측정.
    Input : 실험 설정, 테스트 질문 목록, 정답 문서 목록
    Process:
      1. 해당 설정으로 ChromaDB 재구축
      2. 각 질문으로 검색 실행
      3. 반환된 문서와 정답 문서 비교
    Output : {
      "experiment": ChunkExperiment,
      "precision_at_k": float,    # 상위 k개 중 정답 포함 비율
      "avg_response_ms": float
    }
    """

EXPERIMENTS: list[ChunkExperiment] = [
    ChunkExperiment(chunk_size=200, overlap=20,  k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=3, strategy="fixed"),    # 기본값
    ChunkExperiment(chunk_size=800, overlap=100, k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=5, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=3, strategy="semantic"),
]
```

### `src/tuning/reranker.py`

```python
def rerank_with_cross_encoder(
    query: str,
    documents: list[str],
    top_k: int = 3
) -> list[dict]:
    """
    CrossEncoder로 1차 검색 결과 재순위화.
    Input : 쿼리, 1차 검색 문서 목록 (k=10), 최종 반환 수
    Process: sentence-transformers CrossEncoder 모델로 쌍별 점수 계산
    Output : [{"text": str, "score": float}] (점수 내림차순)
    모델: cross-encoder/ms-marco-MiniLM-L-6-v2
    """

def hybrid_search(
    query: str,
    collection: chromadb.Collection,
    k: int = 3,
    alpha: float = 0.5
) -> list[dict]:
    """
    벡터 유사도 + BM25 키워드 검색 결합.
    Input : 쿼리, 컬렉션, 반환 수, 가중치 (alpha: 벡터 비중, 1-alpha: BM25 비중)
    Process:
      1. 벡터 검색 (ChromaDB) → 점수 정규화
      2. BM25 검색 (rank_bm25) → 점수 정규화
      3. 가중 합산 후 상위 k개 반환
    Output : [{"text": str, "metadata": dict, "score": float}]
    """
```

### `src/tuning/prompts.py`

```python
PROMPT_VARIANTS: dict[str, str] = {
    "baseline": "당신은 AI 비서입니다. 주어진 문서를 참고하여 답하십시오.\n\n{context}\n\n질문: {question}",

    "evidence_first": (
        "당신은 사내 AI 비서입니다. 반드시 아래 문서의 내용만 근거로 답하십시오.\n"
        "문서에 없는 내용은 '제공된 문서에서 확인할 수 없습니다'라고 답하십시오.\n\n"
        "{context}\n\n질문: {question}"
    ),

    "admit_ignorance": (
        "당신은 신중한 AI 비서입니다.\n"
        "주어진 문서에 명확한 답이 있으면 답하고, 확실하지 않으면 '모르겠습니다'라고 하십시오.\n\n"
        "{context}\n\n질문: {question}"
    ),
}

def compare_prompts(
    question: str,
    context: str
) -> dict[str, str]:
    """세 프롬프트 변형으로 동일 질문 실행, 응답 비교 반환."""
```

### `src/ocr_hybrid.py`

```python
def extract_with_ocr(image_path: str) -> str:
    """
    EasyOCR로 이미지에서 텍스트 추출.
    Input : 이미지 파일 경로 (PNG/JPG)
    Output : 추출된 텍스트 문자열
    """

def describe_image_with_llava(image_path: str) -> str:
    """
    LLaVA로 이미지 내용 설명 생성.
    Input : 이미지 파일 경로
    Process: Ollama /api/generate (model=llava)
    Output : 이미지 설명 문자열 (한국어)
    전제조건: ollama pull llava
    """

def process_scanned_pdf(pdf_path: str) -> list[dict]:
    """
    스캔 PDF를 페이지별 이미지로 변환 후 OCR + LLaVA 처리.
    Input : 스캔 PDF 경로
    Process:
      1. PyMuPDF로 페이지 → 이미지 변환
      2. 페이지별 EasyOCR 텍스트 추출
      3. 이미지 포함 시 LLaVA 설명 추가
    Output : [{"page": int, "ocr_text": str, "image_desc": str | None}]
    """
```

### `src/evaluator.py`

```python
@dataclass
class TestCase:
    question: str
    expected_answer_keywords: list[str]   # 정답에 포함되어야 할 키워드
    expected_source_file: str             # 검색되어야 할 문서

@dataclass
class EvalResult:
    test_case: TestCase
    retrieved_docs: list[str]
    generated_answer: str
    retrieval_correct: bool    # 정답 문서가 검색됐는가
    answer_contains_keywords: bool  # 정답 키워드가 응답에 포함됐는가
    hallucination_detected: bool    # 문서에 없는 내용이 포함됐는가

def load_testset(path: str = "data/testset.json") -> list[TestCase]:
    """30개 테스트 케이스 로딩."""

def evaluate_single(
    test_case: TestCase,
    chain,
    retriever
) -> EvalResult:
    """단일 테스트 케이스 평가."""

def run_evaluation(testset: list[TestCase], chain, retriever) -> dict:
    """
    전체 테스트셋 평가 실행.
    Output : {
      "retrieval_accuracy": float,    # 정답 문서 검색 성공률
      "answer_accuracy": float,       # 키워드 포함 비율
      "hallucination_rate": float,    # 환각 발생 비율
      "total": int,
      "results": list[EvalResult]
    }
    """

def save_report(eval_result: dict, output_path: str) -> None:
    """평가 결과를 JSON + 콘솔 리포트로 저장."""
```

### `data/testset.json` 구조

```json
[
  {
    "question": "연차 신청은 며칠 전에 해야 합니까?",
    "expected_answer_keywords": ["전월 말일", "팀장"],
    "expected_source_file": "hr_policy.pdf"
  },
  ...
]
```
총 30개: 정형 10개 + 비정형 15개 + 복합 5개

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt
ollama pull llava   # OCR 섹션용 (선택)

# 청크 튜닝 실험
python -c "from src.tuning.chunker_tuning import *; run_all_experiments()"

# 전체 평가 실행
python src/main.py --mode eval

# OCR 데모
python src/main.py --mode ocr --input data/scanned_sample.pdf

# 기대 출력 (평가):
# === RAG 평가 결과 (30개 테스트 케이스) ===
# Retrieval Accuracy : 86.7% (26/30)
# Answer Accuracy    : 80.0% (24/30)
# Hallucination Rate :  6.7% ( 2/30)
# 결과 저장: outputs/eval_results/eval_2026-02-23.json
```

## 5. 의존성

```
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
sentence-transformers>=3.0.0   # CrossEncoder ReRanker
rank-bm25>=0.2.2               # Hybrid Search BM25
easyocr>=1.7.0                 # OCR
pymupdf>=1.24.0                # 스캔 PDF → 이미지 변환
python-dotenv>=1.0.0
```

## 6. .env.example

```
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# LLM 모델명 설정
# Ollama 예시: deepseek-r1:1.5b, deepseek-r1:8b, llama3
# OpenAI 예시: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 설정 (PROVIDER가 ollama인 경우 필요)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 설정 (PROVIDER가 openai인 경우 필요)
# OPENAI_API_KEY=sk-proj-...

# Vision LLM (OCR/이미지 처리용)
# Ollama: llava:7b, llava:13b  /  OpenAI: gpt-4o
VISION_MODEL_NAME=llava:7b

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# ChromaDB 설정
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs

# 리랭커 및 평가
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
TESTSET_PATH=./data/testset.json
```
