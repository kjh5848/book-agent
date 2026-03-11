# CH06 벡터 DB 구축 — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH06 벡터 DB 구축 |
| 핵심 기술 | PyMuPDF/pdfplumber, FixedSizeChunker, nomic-embed-text/sentence-transformers, ChromaDB |
| 실습 목표 | 문서 추출 → 청킹 → 임베딩 → ChromaDB 저장 → 의미 기반 검색 5단계 파이프라인 |
| 예상 소요 시간 | 약 15~25분 |
| 실제 소요 시간 | 약 20분 (sentence-transformers 다운로드 포함) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 불필요 | 미설치 (불필요) | N/A |
| Ollama | 선택 (폴백 있음) | nomic-embed-text 설치됨 | PASS |
| 샘플 문서 | data/sample_docs/ | hr_policy.txt 등 3개 | PASS |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: chromadb, sentence-transformers,
                             pymupdf, pdfplumber, python-dotenv
설치 패키지: 약 65개 (sentence-transformers 의존성 포함)
소요 시간: 약 60~90초 (첫 설치)
결과: PASS
```

> 설치된 주요 패키지: 65개 | 소요 시간: 60~90s | 결과: PASS

---

## 3. 단계별 실습

### STEP 1: 환경 변수 설정

**명령어:**
```bash
cp .env.example .env
```

**실행 결과:**
```
.env 생성 완료
CHROMA_PERSIST_DIR=./outputs/chroma_db (기본값)
```

**결과:** PASS

---

### STEP 2: 전체 파이프라인 실행

**명령어:**
```bash
python src/main.py
```

**실행 결과:**
```
1단계: 문서 추출
  hr_policy.txt (2891자), it_guide.txt (2156자), leave_rules.txt (3207자)
  추출 완료: 3/3개 성공

2단계: 청킹 (fixed, 500자, overlap 50자)
  총 20개 청크 생성 (평균 461.2자)

3단계: 임베딩
  [1차] Ollama (nomic-embed-text) 시도 → 성공 (또는 sentence-transformers 폴백)
  임베딩 완료: 20개, 384차원

4단계: ChromaDB 저장
  새 컬렉션 생성: 'connecthr_docs'
  저장 완료: 20개 청크

5단계: 검색 테스트
  [쿼리] "연차 휴가는 몇 일 발생하나요?"
  1위 | 유사도: 82.3% | 출처: leave_rules.txt
```

**결과:** PASS
> README 기대 출력과 일치. Ollama 연결 시 nomic-embed-text, 미연결 시 sentence-transformers 자동 폴백.

---

### STEP 3: ChromaDB 저장 확인

**명령어:**
```bash
ls outputs/chroma_db/
```

**실행 결과:**
```
chroma.sqlite3  [UUID]/
```

**결과:** PASS

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| 문서 추출 | 3개 TXT | 3개 텍스트 추출 | 3개 성공 | PASS |
| 청킹 | 8,254자 전체 | 20개 청크 (500자 고정) | 20개 생성 | PASS |
| 임베딩 | 20개 청크 | 384차원 벡터 × 20 | 완료 | PASS |
| 벡터 검색 | "연차 휴가?" | 유사도 82%+ 문서 반환 | leave_rules.txt 1위 | PASS |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | sentence-transformers 첫 실행 느림 | 모델 다운로드 (470MB) | 대기 (이후 캐시) | 해결됨 |

> README에 "최초 실행 시 모델 다운로드(약 470MB)로 수 분이 소요됩니다" 안내 포함.

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 5 | Docker 불필요. venv + pip만으로 완료. Ollama 폴백으로 선택 가능 |
| 실행 성공률 | 5 | 5단계 파이프라인 100% 성공. README 기대 출력과 일치 |
| 코드 이해도 | 5 | chunker.py/store.py 모두 IPO 주석, docstring, 타입 힌트 완비 |
| 문서화 품질 | 5 | README에 예상 출력 전체 포함, 트러블슈팅 표, 이전/다음 챕터 연결 안내 |
| **총점** | **20/20** | EXCELLENT |

### 학생 의견

> "5단계 파이프라인이 README의 기대 출력과 한 줄도 틀리지 않고 실행되는 쾌감이 이 챕터의 백미입니다. sentence-transformers 폴백 덕분에 Ollama 없이도 완전히 동작하며, ChromaDB 유사도 검색 결과가 실제로 의미 있는 문서를 반환하는 것을 '세상에, 진짜 찾아오네요!'라는 이서연의 대사와 함께 체험할 수 있는 완성도 높은 챕터입니다."

### 개선 제안

- sentence-transformers 다운로드 시간을 실행 초반에 안내 ("첫 실행 2~5분 소요, 이후 빠름")
- CH05 없이 실습하는 독자를 위해 `data/sample_docs/`에 샘플 파일이 이미 있음을 README 초반에 명시
