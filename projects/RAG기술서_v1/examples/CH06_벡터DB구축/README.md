# CH06 벡터 DB 구축

> 파이썬으로 배우는 RAG 시스템 - 6장 실습 코드

## 목적 및 학습 목표

- PDF에서 텍스트를 추출하는 두 가지 방식(pdfplumber, PyMuPDF)을 직접 비교합니다.
- Vision LLM(llava 또는 gpt-4o)을 이용한 PDF 파싱 방식을 체험합니다.
- Fixed-size 청킹과 Markdown 헤더 청킹 두 전략의 차이를 이해합니다.
- Ollama REST API를 직접 호출하여 텍스트를 임베딩 벡터로 변환하는 원리를 익힙니다.
- ChromaDB PersistentClient로 벡터를 디스크에 영속 저장하고 부서 필터 검색을 수행합니다.

## 실행 환경

- Python 3.11+
- Ollama (로컬 임베딩 서버 + Vision LLM)
  - 임베딩 모델: `nomic-embed-text`
  - Vision 모델: `llava:7b` (--vision 플래그 사용 시)
- ChromaDB 0.5+

## 파일 구조

```
CH06_벡터DB구축/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   └── docs/                       <- 실습용 PDF 파일
│       ├── HR_취업규칙_v1.0.pdf
│       └── FIN_매출현황_v1.0.pdf
├── src/
│   ├── __init__.py
│   ├── main.py                     <- 파이프라인 진입점
│   ├── extractor.py                <- pdfplumber/PyMuPDF 텍스트 추출
│   ├── vision_extractor.py         <- Vision LLM PDF -> Markdown 변환
│   ├── chunker.py                  <- Fixed-size / Markdown 헤더 청킹
│   ├── embedder.py                 <- Ollama REST API 임베딩
│   └── store.py                    <- ChromaDB 저장 및 검색
└── outputs/
    ├── markdown/                   <- Vision LLM 결과 Markdown 파일
    └── chroma_db/                  <- ChromaDB 영속 저장 폴더
```

## CH05와의 연결

이 챕터의 샘플 PDF 파일명은 CH05에서 배운 **네이밍 규칙**을 따릅니다.

```
{부서}_{문서명}_{버전}.pdf
HR_취업규칙_v1.0.pdf   -> 부서: HR, 문서명: 취업규칙, 버전: v1.0
FIN_매출현황_v1.0.pdf  -> 부서: FIN, 문서명: 매출현황, 버전: v1.0
```

`extractor.py`의 `parse_filename_metadata()` 함수는 이 네이밍 규칙을 파싱하여
부서 코드를 ChromaDB 메타데이터로 저장합니다. 덕분에 `search(filter_dept="HR")`처럼
부서별 필터 검색이 가능합니다.

## 사전 준비 — Ollama 서버 구동 (최초 1회)

실습 전 Ollama를 설치하고 필요한 모델을 다운로드합니다.

**macOS / Linux**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
ollama serve
```

**Vision LLM 사용 시 추가 모델 설치**

```bash
ollama pull llava:7b
```

**Windows**

Ollama 공식 사이트(https://ollama.com)에서 Windows 설치 파일을 내려받아 설치합니다.
설치 후 터미널에서 아래 명령을 실행합니다.

```bash
ollama pull nomic-embed-text
ollama serve
```

> Ollama 서버는 실습 내내 실행 상태를 유지해야 합니다. 서버가 종료되면 임베딩 API 호출이 실패합니다.

## 설치 및 실행

이 챕터의 예제 코드를 클론합니다.

```bash
git clone https://github.com/{repo}/CH06_벡터DB구축
```

CH06_벡터DB구축 폴더로 이동합니다.

환경 변수를 설정합니다.

```bash
cp .env.example .env
```

`.env` 파일의 주요 환경변수와 기본값입니다. 별도 수정 없이 실습이 가능합니다.

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `EMBED_MODEL` | `nomic-embed-text` | Ollama 임베딩 모델 |
| `CHROMA_PERSIST_DIR` | `./outputs/chroma_db` | ChromaDB 저장 경로 |
| `COLLECTION_NAME` | `rag_docs` | ChromaDB 컬렉션 이름 |
| `LLM_MODEL_NAME` | `llava:7b` | Vision LLM 모델 (--vision 사용 시) |
| `CHAT_MODEL` | `deepseek-r1:1.5b` | 터미널 쿼리 LLM (scripts/query.py 사용 시) |

### 사양별 모델 선택 가이드

실습 환경의 RAM 용량에 따라 모델을 선택하십시오.

| RAM | Vision 모델 (`LLM_MODEL_NAME`) | 쿼리 LLM (`CHAT_MODEL`) | 임베딩 (`EMBED_MODEL`) |
|-----|-------------------------------|------------------------|----------------------|
| 8GB 이하 | `moondream` | `deepseek-r1:1.5b` | `nomic-embed-text` |
| 16GB | `llava:7b` | `deepseek-r1:1.5b` | `nomic-embed-text` |
| 32GB+ | `llava:13b` | `qwen2.5:7b` | `nomic-embed-text` |

> **권장**: RAM 8GB 이하 환경에서는 `--file` 옵션으로 한 파일씩 테스트한 뒤 전체 인제스트를 진행하십시오.
>
> ```bash
> ollama pull moondream
> ollama pull deepseek-r1:1.5b
> ```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 실행 순서

### 사전 점검 — Ollama 서버 응답 확인

파이프라인 실행 전 Ollama 서버가 정상 동작하는지 확인합니다.

```bash
curl http://localhost:11434/
```

`Ollama is running` 메시지가 출력되면 정상입니다.

### 1단계: 규칙 기반 파이프라인 실행

```bash
python src/main.py
```

pdfplumber로 텍스트를 추출하고 Fixed-size 청킹을 적용합니다.

### 2단계: Vision LLM 파이프라인 실행 (--vision 플래그)

```bash
python src/main.py --vision
```

PDF 페이지를 이미지로 변환한 뒤 Vision LLM(llava:7b)이 Markdown으로 파싱합니다.
Markdown 헤더 청킹이 적용되며, 결과가 `outputs/markdown/` 에 저장됩니다.

**--vision 플래그 동작 방식:**

| 단계 | 기본 모드 | --vision 모드 |
|------|-----------|---------------|
| 파싱 | pdfplumber (텍스트 직접 추출) | PDF -> PNG -> Vision LLM |
| 청킹 | fixed_size_chunk (500자, overlap 50) | markdown_chunk (## 헤더 기준) |
| 출력 | 없음 | outputs/markdown/*.md 파일 저장 |

> **OpenAI gpt-4o 사용 시**: .env에서 `LLM_PROVIDER=openai`, `LLM_MODEL_NAME=gpt-4o`,
> `OPENAI_API_KEY=sk-proj-...` 를 설정한 뒤 `pip install openai` 를 실행하십시오.

### 3단계: 터미널 RAG 쿼리 실행 (scripts/query.py)

1단계 또는 2단계 실행 후, 아래 명령으로 ChromaDB를 검색하고 LLM 답변을 받을 수 있습니다.

```bash
# 기본 질의
python scripts/query.py "연차 신청은 어떻게 하나요?"

# 부서 필터 적용
python scripts/query.py "보안 USB 분실하면 어떻게 해야 해?" --dept HR

# 검색 결과 수 조정
python scripts/query.py "교육비 지원 한도가 얼마야?" --top-k 5

# LLM 없이 검색 결과만 출력 (빠른 확인용)
python scripts/query.py "연차 신청" --no-llm
```

**쿼리 옵션:**

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--dept` | 없음 (전체 검색) | 부서 코드 필터 (예: HR, FIN) |
| `--top-k` | 3 | 반환할 검색 결과 수 |
| `--no-llm` | 비활성 | 검색 결과만 출력, LLM 생략 |

> **참고**: 쿼리 LLM은 `.env`의 `CHAT_MODEL` 변수로 지정합니다(기본값: `deepseek-r1:1.5b`).
> 처음 실행 시 모델 로딩으로 수십 초가 소요될 수 있습니다.

## 예상 결과 — 규칙 기반 모드

<!-- [캡처 사진 삽입 위치: 터미널 성공 실행 전체 화면 — 5단계 파이프라인 출력] -->

```
=================================================================
  CH06 벡터 DB 구축 파이프라인
  파싱 모드: 규칙 기반 (pdfplumber)
=================================================================

[1/5] PDF 파일 확인 중...
  확인: HR_취업규칙_v1.0.pdf [부서=HR, 문서명=취업규칙, 버전=v1.0]
  확인: FIN_매출현황_v1.0.pdf [부서=FIN, 문서명=매출현황, 버전=v1.0]
  총 2개 PDF 파일 확인 완료.

[2/5] PDF 파싱 중... (모드: 규칙 기반 (pdfplumber))
  완료: HR_취업규칙_v1.0.pdf -> 3페이지 추출 (표 포함 페이지: 1개)
  완료: FIN_매출현황_v1.0.pdf -> 2페이지 추출 (표 포함 페이지: 2개)
  파싱 완료: 총 5개 페이지/섹션

[3/5] 텍스트 청킹 중...
  Fixed-size 청킹 완료: 12개 청크 생성

[청킹 전략 비교]
=================================================================
  항목                      Fixed-size      Markdown 헤더
  -------------------------------------------------
  청크 수                           12             18
  평균 길이 (문자)               478.3          284.5
  섹션 제목 보존                     X              O
=================================================================
비교 완료.

[4/5] 임베딩 변환 중...
  모델: nomic-embed-text, 예상 차원: 768
  임베딩 시작: 총 12개 텍스트, 배치 크기=10, 모델=nomic-embed-text
    진행: 10/12 (83.3%)
    진행: 12/12 (100.0%)
  임베딩 완료: 12개 벡터, 차원=768
  실제 차원: 768

[5/5] ChromaDB 저장 및 검색 테스트 중...
  ChromaDB 클라이언트 초기화 완료: 경로=.../outputs/chroma_db
  컬렉션 'rag_docs' 준비 완료 (현재 문서 수: 0)
  12개 청크 저장 완료. 컬렉션 총 문서 수: 12

  컬렉션 통계:
    총 문서 수: 12
    부서별 분포:
      FIN: 5개
      HR: 7개

  테스트 검색 (3회):
  ------------------------------------------------------------

  검색 1: '연차 신청은 어떻게 하나요?' [전체]
    [1] 거리=0.1734 | HR_취업규칙_v1.0.pdf | 부서=HR
         신입 사원은 입사 후 만 3년간 별도 연차 휴가가 발생하지 않습니다....
    [2] 거리=0.2481 | HR_취업규칙_v1.0.pdf | 부서=HR
         연차 휴가는 발생일로부터 1년 이내에 사용하여야 하며...
    [3] 거리=0.3201 | HR_취업규칙_v1.0.pdf | 부서=HR
         리프레시 데이는 사전 팀장 승인 후 사용 가능하며...

  검색 2: '보안 USB 분실하면 어떻게 해야 해?' [전체]
    [1] 거리=0.1892 | HR_취업규칙_v1.0.pdf | 부서=HR
         보안 USB는 개인 관리 책임 하에 있으며, 분실 시 즉시 IT 팀에 신고...
    [2] 거리=0.2345 | HR_취업규칙_v1.0.pdf | 부서=HR
         발급된 보안 USB에는 업무 목적 이외의 개인 파일을 저장하는 것을 금지...
    [3] 거리=0.3102 | HR_취업규칙_v1.0.pdf | 부서=HR
         IT 팀에서 발급한 암호화 보안 USB만 허용됩니다...

  검색 3: '교육비 지원 한도가 얼마야?' [전체]
    [1] 거리=0.1543 | HR_취업규칙_v1.0.pdf | 부서=HR
         업무 관련 교육 및 자격증 취득 비용을 연 200만 원 한도 내에서 지원...
    [2] 거리=0.2210 | HR_취업규칙_v1.0.pdf | 부서=HR
         지원 대상 교육은 HR 팀의 사전 승인을 받아야 합니다...
    [3] 거리=0.3087 | FIN_매출현황_v1.0.pdf | 부서=FIN
         2024년도 전체 매출은 전년 대비 23% 성장하였습니다...

=================================================================
  파이프라인 완료.
  저장 경로: .../outputs/chroma_db
=================================================================
```

> **주의**: 위 출력은 실제 실행 결과를 기반으로 한 예시입니다. 거리 값과 청크 수는 실제 PDF 내용에 따라 다를 수 있습니다.

## 전체 구조

```mermaid
graph LR
    A["data/docs/\nHR_취업규칙_v1.0.pdf\nFIN_매출현황_v1.0.pdf"] --> B["extractor.py\npdfplumber 추출\n표 -> Markdown 변환"]
    A --> C["vision_extractor.py\nPDF -> 이미지 변환\nVision LLM 파싱"]
    B --> D["chunker.py\nfixed_size_chunk"]
    C --> E["chunker.py\nmarkdown_chunk"]
    D --> F["embedder.py\nOllama REST API\nnomic-embed-text"]
    E --> F
    F --> G["store.py\nget_client + create_collection\nChromaDB PersistentClient"]
    G --> H["outputs/chroma_db\n영속 저장"]
    J["검색 쿼리\n+ 부서 필터"] --> F
    F --> K["store.search(filter_dept)"]
    G --> K
    K --> L["유사 문서 반환"]
```

## 자주 발생하는 오류

| 오류 증상 | 원인 | 해결 방법 |
|---------|------|---------|
| `data/docs/ 폴더에 PDF 파일이 없습니다.` | `data/docs/` 폴더 없거나 PDF 미존재 | PDF 파일을 `data/docs/` 폴더에 복사 |
| `Connection refused` / `ConnectionError` | Ollama 서버 미실행 | `ollama serve` 실행 후 재시도 |
| ChromaDB 재실행 시 문서 수 계속 증가 | 기존 DB에 중복 저장됨 | `outputs/chroma_db/` 폴더 삭제 후 재실행 |
| `pymupdf` 설치 오류 (Windows) | C++ 빌드 도구 누락 | `pip install pymupdf --only-binary :all:` |

## 모듈 설명

| 파일 | 역할 |
|------|------|
| `src/extractor.py` | pdfplumber/PyMuPDF로 PDF 텍스트를 추출합니다. 표를 Markdown으로 변환합니다 |
| `src/vision_extractor.py` | PDF 페이지를 이미지로 변환한 뒤 Vision LLM이 Markdown으로 파싱합니다 |
| `src/chunker.py` | Fixed-size 또는 Markdown 헤더 기준으로 텍스트를 청킹합니다 |
| `src/embedder.py` | Ollama REST API를 직접 호출하여 임베딩 벡터를 생성합니다 |
| `src/store.py` | get_client + create_collection으로 ChromaDB를 초기화하고 벡터를 저장하며 부서 필터 검색을 수행합니다 |
| `src/main.py` | 파이프라인 전체를 순서대로 실행하는 진입점입니다 |
