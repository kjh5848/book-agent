# CH02: 사내 지식 검색 엔진 구축 (기술 설계서)

## 1. 개요 및 요구사항
- **목표**: 파편화된 사내 문서(PDF 등)를 수집하여 텍스트와 **표(Table)** 데이터를 정교하게 파싱하고, 이를 LangChain과 ChromaDB를 이용해 벡터 데이터베이스로 구축(RAG 베이스)합니다.
- **주요 기능**:
  - 기본 텍스트 전처리(Chunking)
  - [고도화] PDF 내 레이아웃 기반 표(Table) 추출 및 Markdown 변환
  - 텍스트 임베딩 후 로컬 ChromaDB에 영구 저장 (Vector DB 구축)
  - 저장된 문서를 바탕으로 출처(출판 정보)를 표기하는 기초 Q&A 봇 구동

## 2. 파일 구성도
```text
anti_v2_book/examples/ch02/
├── requirements.txt      # PDF 파싱(PyMuPDF) 및 LangChain, Chroma 패키지
├── data/                 # 실습용 가짜 사내 규정 PDF 폴더 (에이전트 생성)
├── 01_text_parsing.py    # 기초 텍스트 파싱 및 Chunking 실습
├── 02_table_parsing.py   # [고도화] 표(Table) 파싱 및 Markdown 변환 실습
├── 03_vector_db.py       # 임베딩 및 ChromaDB 적재 (create_vector_db)
├── 04_rag_chatbot.py     # 로컬 QA 봇 1차 스크립트 (rag_pipeline)
├── README.md             # 초보자용 실행 가이드라인
└── tech_plan.md          # (본 문서)
```

## 3. 코드 아키텍처 및 검증 시나리오
- **가짜 데이터(PDF) 생성**: 코드 구동 전 `anti_v2_book/examples/ch02/data` 내에 텍스트와 표가 혼합된 "가상의 휴가 규정.pdf"를 생성하는 셋업 스크립트 작성 (실습 편의성 제공).
- **02_table_parsing.py (고도화 포인트 핵심)**: 단순히 텍스트를 줄글로 빼내는 PyMuPDF의 `get_text()`의 한계를 지적하고, x,y 좌표 기반으로 표를 인식하여 마크다운 표 구조(`| Header |...`)로 예쁘게 정제해내는 과정을 IPO 패턴으로 시연합니다.
- **04_rag_chatbot.py**: 저장된 VectorDB에서 쿼리를 통해 가장 유사한 K개의 문서를 검색(Retrieval)하고, 이를 LLM에 Prompt로 주입해 출처와 함께 정답을 받아옵니다.
- **검증**: 가상환경에서 `requirements.txt` 설치 확인 후, 01~04번 스크립트를 순차적으로 실행하여 최종적으로 로컬 챗봇(04)이 가상 규정에 기반한 정확한 답변을 도출하는지 터미널에서 캡쳐합니다.
