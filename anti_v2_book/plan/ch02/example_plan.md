# CH02. 사내 지식 검색 엔진 구축 — 예제 코드 플랜 (example_plan)

## 1. 개요 및 목표

- **목표**: 파편화된 사내 문서(PDF 등)를 수집하여 텍스트와 **표(Table)** 데이터를 정교하게 파싱하고, 이를 LangChain과 ChromaDB를 이용해 벡터 데이터베이스로 구축(RAG 베이스)합니다.
- **주요 기능**:
  - 기본 텍스트 전처리(Chunking)
  - [고도화] PDF 내 레이아웃 기반 표(Table) 추출 및 Markdown 변환
  - 텍스트 임베딩 후 로컬 ChromaDB에 영구 저장 (Vector DB 구축)
  - 저장된 문서를 바탕으로 출처를 표기하는 기초 Q&A 봇 구동

## 2. 파일 구성도

```text
anti_v2_book/examples/ch02/
├── requirements.txt      # PDF 파싱(PyMuPDF) 및 LangChain, ChromaDB 패키지
├── data/                 # 실습용 가상 사내 규정 PDF 폴더
├── 00_setup_pdf.py       # 가상 사내 규정 PDF 자동 생성 스크립트 (reportlab)
├── 01_text_parsing.py    # 기초 텍스트 파싱 및 한계점 체감용 실습
├── 02_table_parsing.py   # [고도화] 표(Table) 파싱 및 Markdown 변환 실습
├── 03_vector_db.py       # 임베딩 및 ChromaDB 적재 (Vector DB 구축)
└── 04_rag_chatbot.py     # 로컬 QA 봇 1차 스크립트 (RAG 파이프라인)
```

## 3. 코드 아키텍처 및 IPO 명세

| 파일 | Input | Process | Output |
|---|---|---|---|
| `00_setup_pdf.py` | 없음 | `reportlab`으로 텍스트+표 혼합 PDF 생성 | `data/dummy_rules.pdf` |
| `01_text_parsing.py` | `dummy_rules.pdf` | PyMuPDF `get_text()`로 단순 추출, 한계점 분석 | 터미널 출력 (표 구조 깨짐 확인용) |
| `02_table_parsing.py` | `dummy_rules.pdf` | 좌표 기반 `find_tables()` + Markdown 변환 | 터미널에 마크다운 표 출력 |
| `03_vector_db.py` | `dummy_rules.pdf` | 전체 텍스트+표 파싱 → Chunking → HuggingFace 임베딩 → Chroma 저장 | `chroma_db/` 로컬 저장소 |
| `04_rag_chatbot.py` | 사용자 질문 (터미널 입력) | VectorDB 검색 → 프롬프트 조합 → DeepSeek 추론 | 답변 + 출처 터미널 출력 |

## 4. 검증 시나리오 (Verification)

1. 가상환경 활성화 후 `pip install -r requirements.txt` 실행.
2. `python 00_setup_pdf.py` → `data/dummy_rules.pdf` 정상 생성 확인.
3. `python 01_text_parsing.py` → 표가 깨진 텍스트 덩어리 출력 확인 (한계점 체감).
4. `python 02_table_parsing.py` → 마크다운 표(`| 직급 | 휴가 | 지원금 |`) 정상 출력 확인.
5. `python 03_vector_db.py` → `chroma_db/` 디렉토리 정상 생성 확인.
6. `python 04_rag_chatbot.py` → "대리 직급 휴가 지원금은?" 질문에 규정 기반 정확한 답변 출력 확인.
7. 성공 화면 캡처 → `assets/CH02_result_rag_chatbot.png` 저장.
