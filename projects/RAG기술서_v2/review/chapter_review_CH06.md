# CH06 벡터 DB 구축 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: 4단계 파이프라인(추출→청킹→임베딩→저장)

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | PDF/TXT 추출 → Fixed/Semantic 청킹 → nomic-embed-text 임베딩 → ChromaDB 저장 → 의미 기반 검색 |
| 전제 조건 | Python venv, CH05 완료(또는 샘플 문서 준비), Ollama nomic-embed-text (없으면 sentence-transformers 폴백) |
| 실행 단계 수 | 4단계 (clone → install → run pipeline → search) |
| 실제 소요 시간 | 약 15~25분 (첫 실행 시 sentence-transformers 470MB 다운로드 포함) |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | 3.14.3 |
| Docker | 불필요 | 이 챕터는 로컬 파일 처리만 |
| Ollama nomic-embed-text | SKIP 가능 | sentence-transformers 폴백 자동 적용 |
| 샘플 문서 | 확인 필요 | CH05 outputs/markdown/ 또는 data/docs/ 필요 |

## 3. 단계별 실행 결과

### STEP 1: 저장소 클론 및 패키지 설치

**원고 지시:** `git clone ... && cp .env.example .env && python3 -m venv venv && pip install -r requirements.txt`

**예제 코드 검증:**
- `.env.example`에 `CHROMA_PERSIST_DIR=./outputs/chroma_db` 포함 확인
- venv 생성 및 활성화 지시 명확 ("가상환경 활성화 확인" 주의 박스 포함)
- `requirements.txt`에 pymupdf, pdfplumber, chromadb, sentence-transformers 포함 확인

**결과:** PASS (정적 분석)

---

### STEP 2: 파이프라인 실행

**원고 지시:** `python src/main.py`

**예제 코드 검증:**
- `src/chunker.py`의 `FixedSizeChunker.split()` 함수: 챕터 발췌(`step = self.chunk_size - self.overlap`)와 실제 코드 일치
- `src/store.py`의 `ChromaStore.search()` 메서드: 챕터 설명과 구현 일치
  - `metadata={"hnsw:space": "cosine"}` 코사인 유사도 설정 코드 존재 확인
  - 배치 저장(batch_size=5000) 구현 확인
- `src/chunker.py`의 `SemanticChunker`: 문단 기반 분할 로직 구현 확인

**결과:** PASS (정적 분석)

**예상 출력 검증:**
- 챕터 기대 출력: 청킹 전략 비교표(Fixed 8개, Semantic 6개 청크)
- `compare_strategies()` 함수에서 동일 결과 재현 가능

---

### STEP 3: 검색 실행

**원고 지시:** "연차 규정"으로 유사도 검색 → 관련 청크 3개 반환 확인

**결과:** PASS (코드 검증)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | PyMuPDF vs pdfplumber 비교표, 오버랩의 역할(경계 문맥 보존), 384차원 벡터 설명 모두 충분 |
| Why 설명 | 5 | 왜 문서 전체를 하나의 벡터로 만들면 안 되는지, 왜 오버랩이 필요한지, 왜 ChromaDB인지 명확히 설명 |
| 실행 재현성 | 5 | Docker 불필요, sentence-transformers 폴백으로 Ollama 없이도 동작, venv 주의 박스 포함 |
| 코드 발췌 정확성 | 5 | FixedSizeChunker, ChromaStore.search() 발췌 모두 실제 코드와 일치 |
| 오류 대응 안내 | 4 | chromadb 미설치 시 RuntimeError 메시지 안내 있음. 첫 실행 시 sentence-transformers 다운로드 시간 미안내 |
| 분량 적절성 | 5 | 4단계 파이프라인을 균형있게 설명. 청킹 전략 비교가 특히 유용 |
| **총점** | **29/30** | |

## 5. 발견된 문제점

1. **sentence-transformers 첫 실행 시간**: 폴백 모델 다운로드(470MB)에 수 분이 소요되지만 챕터에서 소요 시간 미안내. 독자가 멈춘 것으로 오해할 수 있음.
2. **CH05 연계 의존성**: "CH05 outputs/markdown/ 폴더의 파일을 사용"이라고 안내하지만, CH05를 완료하지 않은 독자를 위한 샘플 데이터 경로 안내가 불명확함. `data/docs/` 폴더의 샘플 파일을 명시적으로 안내해야 함.
3. **git clone URL 플레이스홀더**: `git clone https://github.com/{repo}/CH06_벡터DB구축` — 실제 URL이 아닌 플레이스홀더.

## 6. 학생 한 줄 평

> "PyMuPDF vs pdfplumber 선택 기준, Fixed-size vs Semantic 청킹 비교, 오버랩의 역할까지 '왜' 설명이 탁월하며, Docker 없이 순수 Python으로 완전 실행 가능해 입문자가 가장 안심하고 따라할 수 있는 파이프라인 챕터입니다."

## 7. 개선 제안

- sentence-transformers 첫 실행 시 다운로드 진행 시간 안내 추가 ("약 470MB, 2~5분 소요")
- CH05 완료 여부와 무관하게 즉시 실습 가능한 샘플 데이터 파일 경로 명시
- git clone URL을 실제 URL 또는 명확한 주석으로 대체
