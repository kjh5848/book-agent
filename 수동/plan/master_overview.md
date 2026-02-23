# 마스터 오버뷰 — plan.md — AI 업무 비서 구축: RAG + MCP 실전 가이드

> 자동 생성: 2026-02-23
> 소스: plan.md + chapter_plan/ + example_plan/

---

## 1. 프로젝트 개요


**총 분량**: 100p

### 기술 스택

| 서비스 | 유형 | 비용 | 대체 가능 |
|--------|------|------|----------|
| Ollama | 로컬 LLM 런타임 | 무료 | vLLM, llama.cpp |
| DeepSeek R1 | LLM 모델 | 무료 (오픈 웨이트) | Llama 3, Mistral |
| LLaVA | 이미지 LLM | 무료 (오픈 웨이트) | - |
| ChromaDB | 벡터 DB | 무료 (오픈소스) | FAISS, Milvus |
| PostgreSQL | 관계형 DB | 무료 (오픈소스) | SQLite(축소판) |
| EasyOCR | OCR 엔진 | 무료 (오픈소스) | Tesseract |
| OS | 지원 수준 | 특이사항 |
|----|----------|---------|
| macOS (Apple Silicon) | 1차 지원 | Ollama 네이티브 지원, Metal 가속 |
| macOS (Intel) | 1차 지원 | CPU 모드 |


## 2. 챕터 개요 테이블

| CH | 제목 | 유형 | 주요 파일 | 핵심 개념 |
|-----|------|------|---------|---------|
| 01 | 이 책의 목표와 최종 완성본 미리보기 | AI코드 |  | RAG, MCP, 환각 |
| 02 | 개발 환경 구축 | 인프라 | `README.md`, `requirements.txt`, `01_schema_and_data.sql` | Ollama, venv, Docker Compose |
| 03 | DeepSeek-R1으로 체험하는 LLM의 한계와 RAG의 필요성 | 인프라 | `README.md`, `requirements.txt`, `__init__.py` | 환각, 학습 데이터 컷오프, Context Injection |
| 04 | 베이스 시스템 확보 | 인프라 | `README.md`, `01_schema_and_data.sql`, `__init__.py` | MCP, CRUD, ER 다이어그램 |
| 05 | 사내 문서 표준화 | 인프라 | `README.md`, `metadata_schema.json`, `hr_policy_raw.txt` | 전처리, 정규화, 메타데이터 |
| 06 | 벡터 DB 구축 | AI코드 | `README.md`, `requirements.txt`, `__init__.py` | 청킹, 임베딩, 컬렉션 |
| 07 | RAG Q&A 엔진 구현 | AI코드 | `README.md`, `requirements.txt`, `__init__.py` | LCEL, Retriever, Source Citation |
| 08 | 통합 에이전트 설계 (MCP + RAG) | AI코드 | `README.md`, `requirements.txt`, `__init__.py` | 질문 라우팅, 정형 데이터, 비정형 데이터 |
| 09 | LangChain 최종 연결 | AI코드 | `README.md`, `requirements.txt`, `__init__.py` | LangChain Tool, LCEL, Retry |
| 10 | RAG 시스템 튜닝 | AI코드 | `README.md`, `requirements.txt`, `__init__.py` | ReRanker, Hybrid Search, Parent Document Retriever |


## 3. 챕터별 상세

### CH01 — 이 책의 목표와 최종 완성본 미리보기

**섹션 구조**
1. 이 책이 만드는 것: Fine-tuning이 아닌 RAG 파이프라인, 로컬 LLM 전용 접근 방식. 최종 완성본 스크린샷/시나리오로 "이런 걸 만든다"를 먼저 보여줌
2. 시나리오로 보는 AI 업무 비서: 구체적인 사용자 시나리오 (김철수의 연차 잔여일 + 연차 규정 문서 복합 질의) — 질문이 어떻게 라우팅되어 DB와 문서를 동시에 검색하고 답변이 합성되는지 단계별로 추적
3. 전체 아키텍처 한 장 요약: Mermaid 다이어그램으로 전체 시스템 구성도, 각 구성 요소의 역할을 한 줄씩 설명
4. 사용 기술 스택 상세: 각 기술의 선택 이유와 버전을 표로 정리
5. 이 책을 마치면 할 수 있는 것: 독자가 달성할 역량 목록
6. 정리하며: 2장(개발 환경 구축) 예고 — "이 시스템을 직접 만들기 위해, 먼저 도구를 준비합니다"

**→ 다음 챕터**: 전체 아키텍처 구조, 기술 스택 개요 → "이 시스템을 직접 구축하기 위해, 2장에서 개발 환경을 세팅합니다"

### CH02 — 개발 환경 구축

**섹션 구조**
1. Ollama 설치 및 DeepSeek R1 모델 다운로드: OS별 설치 방법, 모델 다운로드, 동작 확인
2. PostgreSQL 설치 및 초기 설정: Docker Compose로 PostgreSQL 구동, 초기 접속 확인
3. Python 3.11 가상환경 및 패키지 설치: venv 생성, requirements.txt 기반 패키지 설치
4. 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계: .env.example 작성, python-dotenv 활용, Provider 전환 구조
5. 정리하며: 전체 환경 체크리스트 + 3장 예고

**예제 파일**: `README.md` · `requirements.txt` · `01_schema_and_data.sql` · `__init__.py` · `config.py` · `verify_env.py` · `test_config.py`
**실행**: `python src/verify_env.py`
**→ 다음 챕터**: 완성된 개발 환경, .env 구성, Docker Compose 기반 인프라 구동 방법

### CH03 — DeepSeek-R1으로 체험하는 LLM의 한계와 RAG의 필요성

**섹션 구조**
1. [실패] LLM 단독 질의의 한계: DeepSeek R1에 사내 정보를 질문하여 환각을 직접 체감
2. 왜 LLM은 환각을 일으키는가: 학습 데이터 컷오프, 사내 비공개 정보 부재, 확신 있는 거짓말의 원리 설명
3. [임시 해결] Context Injection 맛보기: 문서를 프롬프트에 직접 붙여넣어 응답 개선 체험 — 그러나 토큰 한계와 확장 불가능성을 체감
4. 해결책 미리보기 — RAG란 무엇인가: RAG 개념과 전체 아키텍처 소개 (구현은 6장에서)
5. 정리하며: 문제와 해결 방향 정리 + 4장 베이스 시스템 예고

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `01_llm_only.py` · `02_context_injection.py` · `sample_hr_policy.txt`
**실행**: `python src/01_llm_only.py`
**→ 다음 챕터**: LLM 한계의 이해, RAG가 필요한 이유 (동기 부여)

### CH04 — 베이스 시스템 확보

**섹션 구조**
1. 사내 시스템 git clone으로 확보: rag-infra 레포 클론, docker-compose up으로 전체 인프라 구동
2. 데이터베이스 스키마 분석: 직원, 휴가, 매출 테이블 구조 파악, ER 다이어그램
3. CRUD API 구조 이해: FastAPI 엔드포인트 목록, 요청/응답 형식 확인
4. MCP 개념 소개: Model Context Protocol의 정의, LLM이 외부 도구를 호출하는 원리
5. 정리하며: 확보한 인프라 요약 + 5장 예고

**예제 파일**: `README.md` · `01_schema_and_data.sql` · `__init__.py` · `main.py` · `database.py` · `models.py` · `schemas.py` · `__init__.py`
**실행**: `docker-compose up -d`
**→ 다음 챕터**: 사내 DB 스키마, CRUD API 구조, MCP 개념 기초

### CH05 — 사내 문서 표준화

**섹션 구조**
1. RAG 검색 품질을 결정하는 문서 기준: "쓰레기가 들어가면 쓰레기가 나온다" — 문서 품질이 RAG 성능을 좌우하는 원리
2. PDF, Word, Markdown 수집 전략: 사내에 흩어진 문서 유형별 수집 방법과 우선순위
3. 문서 전처리 및 정규화 가이드라인: 헤더/푸터 제거, 인코딩 통일, 불필요 공백 정리, 표/이미지 처리 방침
4. 문서 버전 관리 및 메타데이터 설계: 문서 ID, 출처, 작성일, 부서 등 메타데이터 스키마 설계
5. 정리하며: 표준화 완료 체크리스트 + 6장 예고

**예제 파일**: `README.md` · `metadata_schema.json` · `hr_policy_raw.txt` · `hr_policy_clean.txt` · `collection_strategy.md` · `preprocessing_rules.md`
**→ 다음 챕터**: 문서 표준화 기준, 메타데이터 스키마, 전처리 파이프라인 설계

### CH06 — 벡터 DB 구축

**섹션 구조**
1. 텍스트 추출: PyMuPDF와 pdfplumber를 사용하여 PDF에서 텍스트를 추출. 두 라이브러리의 차이점과 선택 기준
2. 청킹 전략: Fixed-size vs Semantic 청킹 비교. 청크 크기, 오버랩 설정. 실습으로 두 전략의 결과 비교
3. 임베딩 모델 선택 및 적용: Ollama 임베딩 모델 활용. 임베딩 차원과 성능 트레이드오프
4. ChromaDB에 저장 및 컬렉션 관리: 컬렉션 생성, 문서+메타데이터 저장, 영속 모드 설정, 유사도 검색 테스트
5. 정리하며: 구축된 벡터 DB 확인 + 7장 예고

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `main.py` · `extractor.py` · `chunker.py` · `embedder.py` · `store.py`
**실행**: `python src/main.py`
**→ 다음 챕터**: ChromaDB에 저장된 벡터 데이터, 컬렉션 구조, 유사도 검색 API

### CH07 — RAG Q&A 엔진 구현

**섹션 구조**
1. LangChain RAG 파이프라인 설계: LCEL 기반 RAG Chain 구조. Retriever -> Prompt -> LLM -> Output Parser
2. 유사도 검색 및 컨텍스트 구성: ChromaDB Retriever 설정, k값 조정, 검색 결과를 프롬프트 컨텍스트로 조합
3. 출처 표시 시스템: 응답에 참조 문서의 출처(파일명, 페이지)를 자동 첨부하는 구현
4. 대화 히스토리와 멀티턴 Q&A: ChatMessageHistory를 활용하여 이전 대화 맥락을 유지하는 멀티턴 RAG 구현. 단발 Q&A에서 대화형 비서로 확장
5. 기본 채팅 인터페이스 연결: 터미널 기반 대화형 Q&A 루프 구현 (멀티턴 적용)
6. 정리하며: RAG Q&A 엔진 완성 확인 + 8장 예고

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `main.py` · `rag_chain.py` · `retriever.py` · `citation.py` · `memory.py`
**실행**: `python src/main.py`
**→ 다음 챕터**: RAG Chain, Retriever, 출처 표시, 멀티턴 대화 시스템 (CH08에서 통합 에이전트에 결합)

### CH08 — 통합 에이전트 설계 (MCP + RAG)

**섹션 구조**
1. 정형/비정형 분리 원칙: 어떤 질문이 DB 조회(정형)이고 어떤 질문이 문서 검색(비정형)인지 분류 기준 수립
2. 질문 라우팅 전략: 규칙 기반 라우팅에서 LLM 판단 기반 라우팅으로 진화. 라우터 프롬프트 설계
3. 통합 응답 전략: DB 조회 결과 + 문서 검색 결과를 LLM이 합성하여 단일 응답 생성
4. 대표 질문 시나리오 10개 실습: 정형, 비정형, 복합 질문별 실행 결과 확인 및 분석
5. 정리하며: 에이전트 설계 패턴 요약 + 9장 예고

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `main.py` · `router.py` · `mcp_client.py` · `rag_client.py` · `agent.py`
**실행**: `python src/main.py`
**→ 다음 챕터**: 라우터 설계 패턴, 통합 응답 전략, 시나리오 기반 검증 방법

### CH09 — LangChain 최종 연결

**섹션 구조**
1. Router / Agent / RAG Chain / MCP Tool 구성: 8장에서 설계한 아키텍처를 LangChain LCEL로 통합 구현
2. MCP Tool 설계: get_leave_balance, get_sales_sum 등 사내 DB 조회 Tool을 LangChain Tool 규격으로 구현
3. 운영 설정: Timeout, Retry, 로깅(logging), 캐싱(LangChain Cache) 구성
4. 비용 관리 및 토큰 모니터링: 토큰 사용량 추적, 로컬 LLM에서의 리소스 모니터링
5. 정리하며: 전체 파이프라인 완성 확인 + 10장 예고

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `main.py` · `mcp_tools.py` · `rag_tool.py` · `agent.py` · `config.py`
**실행**: `python src/main.py`
**→ 다음 챕터**: 완성된 통합 파이프라인 (CH10에서 튜닝 대상)

### CH10 — RAG 시스템 튜닝

**섹션 구조**
1. 증상별 튜닝 가이드: 환각, 근거 부족, 엉뚱한 문서 반환 등 증상별 원인 진단 및 해결법 매트릭스
2. Chunk/Retriever 튜닝: Semantic Chunk, k값 조정, Metadata Filtering 적용
3. 고급 기술: ReRanker, Hybrid Search(키워드+벡터), Parent Document Retriever 소개 및 적용
4. 프롬프트 튜닝: 근거 우선 응답, "모르면 모른다" 전략, 시스템 프롬프트 최적화
5. PDF 이미지 처리: LLaVA + EasyOCR 하이브리드로 이미지 포함 PDF 처리
6. 평가 체계 구축: 테스트셋 30개 설계, Retrieval 정확도, Hallucination Rate 측정
7. 정리하며: 전체 프로젝트 회고 + 향후 확장 방향 제시

**예제 파일**: `README.md` · `requirements.txt` · `__init__.py` · `main.py` · `__init__.py` · `chunker_tuning.py` · `reranker.py` · `prompts.py`
**실행**: `python src/main.py --mode eval`
**→ 다음 챕터**: 없음 (최종 챕터). 에필로그에서 향후 확장 방향(Graph RAG, 멀티에이전트 등) 간략 언급


## 4. 챕터 의존성 그래프

```mermaid
flowchart LR
    CH01["1장 이 책의 목표와 최종 "] --> CH02["2장 개발 환경 구축"]
    CH02["2장 개발 환경 구축"] --> CH03["3장 DeepSeek-R1으"]
    CH03["3장 DeepSeek-R1으"] --> CH04["4장 베이스 시스템 확보"]
    CH04["4장 베이스 시스템 확보"] --> CH05["5장 사내 문서 표준화"]
    CH05["5장 사내 문서 표준화"] --> CH06["6장 벡터 DB 구축"]
    CH06["6장 벡터 DB 구축"] --> CH07["7장 RAG Q&A 엔진 구"]
    CH07["7장 RAG Q&A 엔진 구"] --> CH08["8장 통합 에이전트 설계 ("]
    CH08["8장 통합 에이전트 설계 ("] --> CH09["9장 LangChain 최종"]
    CH09["9장 LangChain 최종"] --> CH10["10장 RAG 시스템 튜닝"]
```


## 5. 빠른 실행 가이드

**CH02 개발 환경 구축**
```bash
# 예제 위치: examples/CH02_*/
cp .env.example .env && pip install -r requirements.txt
python src/verify_env.py
```
주요 의존성: langchain · langchain-community · langchain-ollama · chromadb

**CH03 DeepSeek-R1으로 체험하는 LLM의 한계와 RAG의 필요성**
```bash
# 예제 위치: examples/CH03_*/
cp .env.example .env && pip install -r requirements.txt
python src/01_llm_only.py
```
주요 의존성: requests · python-dotenv

**CH04 베이스 시스템 확보**
```bash
# 예제 위치: examples/CH04_*/
cp .env.example .env && pip install -r requirements.txt
docker-compose up -d
```
주요 의존성: fastapi · sqlalchemy · psycopg2-binary · pydantic

**CH06 벡터 DB 구축**
```bash
# 예제 위치: examples/CH06_*/
cp .env.example .env && pip install -r requirements.txt
python src/main.py
```
주요 의존성: requests

**CH07 RAG Q&A 엔진 구현**
```bash
# 예제 위치: examples/CH07_*/
cp .env.example .env && pip install -r requirements.txt
python src/main.py
```
주요 의존성: langchain · langchain-community · langchain-ollama · chromadb

**CH08 통합 에이전트 설계 (MCP + RAG)**
```bash
# 예제 위치: examples/CH08_*/
cp .env.example .env && pip install -r requirements.txt
python src/main.py
```
주요 의존성: requests

**CH09 LangChain 최종 연결**
```bash
# 예제 위치: examples/CH09_*/
cp .env.example .env && pip install -r requirements.txt
python src/main.py
```
주요 의존성: langchain · langchain-community · langchain-ollama · chromadb

**CH10 RAG 시스템 튜닝**
```bash
# 예제 위치: examples/CH10_*/
cp .env.example .env && pip install -r requirements.txt
python src/main.py --mode eval
```
주요 의존성: sentence-transformers · rank-bm25 · easyocr · pymupdf
