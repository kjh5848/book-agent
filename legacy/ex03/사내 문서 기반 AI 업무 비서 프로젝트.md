제공해주신 '사내 문서 기반 AI 업무 비서(RAG + MCP)' 프로젝트의 기획안과 목차를 AI가 문맥과 구조를 명확히 파악할 수 있도록 최적화된 마크다운(Markdown) 형식으로 정리해 드립니다.

---

# [프로젝트] 사내 문서 기반 AI 업무 비서 (RAG + MCP)

**작성일:** 2026-02-04 **목표:** 로컬 LLM을 활용하여 보안을 유지하면서, 회사의 정형 데이터(DB)와 비정형 데이터(문서)를 통합적으로 질의응답할 수 있는 시스템 구축

---

## 1. 아키텍처 개요 (System Architecture)

시스템은 사용자의 질문 유형에 따라 적절한 데이터 소스를 선택하는 **LangChain Agent (Router)** 구조를 가집니다.

### 데이터 처리 흐름 (Pipeline Strategy)

1.  **비정형 데이터 (RAG 파이프라인):**
    - **전처리:** PDF, Word, Excel 파일을 `pdf_strategy.py`, `docx_strategy.py`, `xlsx_strategy.py`를 통해 마크다운으로 변환.
    - **임베딩:** `ko-sroberta-multitask` 모델을 사용하여 Chroma 벡터 DB에 저장.
    - **검색:** 사용자 질문과 가장 유사한 문서 조각(Chunk)을 추출하여 LLM에 전달.
2.  **정형 데이터 (MCP 파이프라인):**
    - **MCP 서버:** `mcp/mcp_server.py`에서 FastMCP를 통해 데이터베이스 도구 제공.
    - **도구 목록:** 직원 정보(CRUD), 휴가 잔여량 조회/차감, 부서별 매출 집계 등.
    - **실행:** LLM이 질문을 분석하여 필요한 SQL 쿼리나 DB 조작 도구를 직접 호출.
3.  **통합 인제스트 (`ingest.py`):**
    - `data/raw` 폴더의 모든 파일을 자동 감지하여 일괄 변환 및 임베딩 수행.

---

## 2. 하이브리드 에이전트 도구 구축 (MCP)

본 프로젝트는 **FastMCP** 프레임워크를 사용하여 사내 DB와 LLM을 안전하게 연결합니다.

- **직원 관리:** 신규 등록, 정보 조회, 수정 및 퇴사 처리.
- **근태/휴가 관리:** 개인별 휴가 잔여 확인 및 휴가 사용 시 자동 차감 로직 포함.
- **매출 분석:** 특정 기간이나 부서별 매출 데이터를 DB에서 즉시 추출 및 통계 제공.

---

## 3. 프로젝트 구조 (Directory Structure)

```text
project/
├── app/                 # FastAPI 백엔드 및 UI
├── mcp/                 # MCP (Model Context Protocol) 서버
│   └── mcp_server.py    # FastMCP 기반 도구 정의 스크립트
├── data/
│   ├── raw/             # 원본 문서 (pdf, docx, xlsx 등)
│   ├── processed/       # 변환 완료된 MD 파일
│   └── embedding_db/    # Chroma 벡터 데이터베이스
├── scripts/
│   ├── converter/       # 파일 형식별 변환기 (pdf, docx, xlsx)
│   ├── embedding/       # 임베딩 전략기 (embed_strategy.py)
│   └── seed_data.py     # 초기 DB 데이터(직원, 매출) 삽입
├── ingest.py            # [통합] 데이터 감지/변환/임베딩 자동화
├── requirements.txt
└── ...
```

---

## 4. 운영 및 보안 체크리스트

- **보안:** 로컬 LLM(Ollama) 사용으로 데이터 외부 유출 차단, DB 접근 권한 분리.
- **확장성:** 새로운 데이터 소스(API, 다른 DB) 추가 시 MCP 도구를 통해 즉시 연동 가능.
- **최신성:** RAG를 통한 문서 정보와 MCP를 통한 정형 데이터의 실시간 동기화.

---

**이 문서에 대한 구체적인 Python 코드 구현 예시나 특정 파트(예: MCP 도구 추가 방법)의 상세 내용이 필요하시면 말씀해 주세요.**
