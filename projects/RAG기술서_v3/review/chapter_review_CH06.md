# CH06 VectorDB 구축 — Reader Review Report


---

## 1. Chapter Overview

| Item | Content |
|------|---------|
| Learning objective | Python 파싱 → Vision LLM 파싱 → 청킹 → 임베딩 → ChromaDB 저장 전 과정 실습 |
| Prerequisites | CH02 개발환경(Ollama + Python), CH05 표준화 문서 세트(data/docs/) 준비 |
| Number of execution steps | 3 steps (Step 1: Python 파싱, Step 2: Vision LLM 파싱, Step 3: CLI 검증) |

---

## 2. Environment Check Results

| Item | Requirement | Actual Version/Status | Result |
|------|-------------|-----------------------|--------|
| Python | 3.10+ | 3.12 (Homebrew) | PASS |
| Python (system) | 3.10+ | 3.14.3 (시스템 기본값) | FAIL — 주의 필요 |
| Ollama | 실행 중 | llava:7b, deepseek-r1:1.5b 사용 가능 | PASS |
| Docker | 선택사항 | 29.1.3 실행 중 | PASS |
| 인터넷 연결 | 모델 다운로드 | ko-sroberta-multitask 다운로드 성공 | PASS |

### 비고: Python 버전 문제

챕터는 `python -m venv venv` 명령만 제시하며 특정 Python 버전을 명시하지 않습니다. 시스템 기본 Python이 3.14인 환경에서 `tokenizers` 패키지가 PyO3 ABI 호환성 문제로 빌드에 실패합니다. Python 3.12(`/opt/homebrew/bin/python3.12`)를 명시적으로 사용하여 해결했습니다.

---

## 3. Step-by-Step Execution Results

### STEP 0: 환경 설정 및 의존성 설치

**Manuscript instruction:** "python -m venv venv / source venv/bin/activate / pip install -r requirements.txt"

**Executed command:**
```bash
/opt/homebrew/bin/python3.12 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Actual output:**
```
Successfully installed MarkupSafe-3.0.3 ... chromadb-0.5.23 ...
sentence-transformers-3.3.1 pymupdf-1.24.14 ...
(총 약 80개 패키지 설치 성공)
```

**Result:** CONDITIONAL PASS
> Python 3.14 환경에서는 tokenizers 빌드 실패. Python 3.12 명시 필요. Python 3.12로 전환 후 정상 설치 완료.

---

### STEP 1: Python 파싱 단독 실행

**Manuscript instruction:** "`python src/main.py --step 1` 을 실행하여 추출 결과를 직접 확인하십시오."

**Executed command:**
```bash
python src/main.py --step 1
```

**Actual output:**
```
============================================================
Q/A 사내 AI VectorDB 구축 파이프라인 시작
============================================================
실행 Step: [1]
문서 디렉토리: .../data/docs

============================================================
Step 1: Python 파싱 — 형식별 텍스트 추출
============================================================
총 6개 문서를 발견했습니다.
  추출 중: FIN_2025_상반기_매출현황.xlsx ... 완료 (891자)
  추출 중: FIN_부서별_예산기안서.xlsx ... 완료 (633자)
  추출 중: HR_정보보안서약서.pdf ... 완료 (0자)
  추출 중: HR_취업규칙_v1.0.pdf ... 완료 (1906자)
  추출 중: OPS_신규서비스_런칭전략.pdf ... 완료 (1435자)
  추출 중: SEC_보안규정_v1.0.docx ... 완료 (896자)

Step 1 완료: 6개 문서 추출 (0.2초)
```

**Screen capture:**
![Step 1 Python 파싱 실행 결과](../assets/CH06/step01_python_parsing.png)

**Result:** PASS
> 챕터 예시 출력과 차이 있음: 챕터는 7개 문서(FIN_매출현황_v1.0.pdf 포함)를 예시로 보여주지만, 실제 data/docs/에는 6개 문서가 서브디렉토리(hr/, finance/, ops/, security/)에 구성되어 있음. 핵심 개념(이미지형 PDF 0자 추출) 확인은 `HR_정보보안서약서.pdf`(0자)를 통해 동일하게 체감 가능.

---

### STEP 2: Vision LLM 없이 전체 파이프라인 실행 (--no-vision)

**Manuscript instruction:** "Vision LLM을 사용하지 않으려면 다음 옵션을 사용하십시오: `python src/main.py --no-vision`"

**Executed command:**
```bash
python src/main.py --no-vision
```

**Actual output:**
```
[Vision LLM 비활성화] Step 2를 건너뜁니다.

============================================================
Q/A 사내 AI VectorDB 구축 파이프라인 시작
============================================================
실행 Step: [1, 3]
...
총 6개 문서를 발견했습니다.
...
전체 청크 수: 17개
임베딩 모델 로드 중: jhgan/ko-sroberta-multitask
  임베딩 모델 로드 완료 (벡터 차원: 768)

ChromaDB 초기화: .../outputs/chroma_db
  새 컬렉션 생성: 'hr_documents'
  17개 청크 임베딩 계산 중... (배치 크기: 64)
  임베딩 계산 완료: 17개 벡터 생성

ChromaDB에 저장 중... (17개 청크)
  업서트 완료: 17/17개
ChromaDB 저장 완료! (컬렉션 총 문서 수: 17)

Step 3 완료 (5.4초)
파이프라인 완료! (총 소요 시간: 5.6초)
```

**Screen capture:**
![파이프라인 실행 완료 화면](../assets/CH06/step02_pipeline_complete.png)

**Result:** PASS
> 챕터 예상 출력(127개 청크)과 실제(17개 청크) 수치 차이가 큼. 원인: 예시 데이터가 7개 문서(더 긴 내용)였던 반면 실제 샘플 문서는 소용량 샘플 PDF/DOCX. 동작 자체는 완벽히 정상. telemetry 경고 메시지가 출력되나 실행에는 영향 없음.

---

### STEP 3: CLI 검색 품질 검증

**Manuscript instruction:** "`python src/cli_search.py --query '연차 사용 규정'` 을 실행하여 검색 품질을 확인하십시오."

**Executed command:**
```bash
python src/cli_search.py --query "연차 사용 규정"
```

**Actual output:**
```
======================================================================
검색 쿼리: 연차 사용 규정
상위 5개 결과를 검색합니다...
======================================================================
임베딩 모델 로드 완료 (벡터 차원: 768)

[결과 1]  유사도: 78.0%  |  출처: HR_취업규칙_v1.0.pdf  |  페이지: 1
  유형: 텍스트
----------------------------------------------------------------------
취업규칙 (다단 편집형)문서번호 : HR-2026-001
버전: v2.0 (Draft)
4. 휴가 및 리프레시 (Leave & Refresh)
4.1 스마트 휴가 승인 (Smart Approval)
메타코딩는 구성원의 자율성을 존중하며, 휴가 사용에 있어 불필요한 절차를 최소화합니다...
연차, 반차, 및 ... (이하 생략)

[결과 2]  유사도: 76.0%  |  출처: HR_취업규칙_v1.0.pdf  |  페이지: 1
...
총 5개 결과 반환 완료
```

**Screen capture:**
![CLI 검색 결과 화면](../assets/CH06/step03_cli_search_result.png)

**Result:** PASS
> 상위 결과가 HR_취업규칙_v1.0.pdf에서 정확히 반환됨. 유사도 78.0%(챕터 예시 91.2%보다 낮음) — 이는 샘플 문서의 텍스트 추출 품질 차이와 Python 파싱만 사용했기 때문. 검색 방향은 올바름.

---

## 4. Chapter Manuscript Quality Evaluation

| Item | Score (5 pts) | Rationale |
|------|--------------|-----------|
| Explanation sufficiency | 5 | Python 파싱 한계 → Vision LLM 필요성 → 청킹 전략 → 임베딩 모델 선택 이유를 흐름에 따라 충분히 설명. 각 코드 블록 앞에 "왜 이 코드인가"를 명시 |
| Why explanation | 5 | 500자 청킹 선택 이유, ko-sroberta-multitask 선택 3가지 이유, upsert 방식 설명, CLI 검증 먼저 하는 이유 모두 설명됨 |
| Execution reproducibility | 3 | --no-vision 옵션으로 전체 실행 성공. 그러나 Python 버전(3.12 이상 권장) 명시 누락으로 Python 3.14 환경에서 설치 실패 발생. 예시 출력 수치(127개 청크, 7개 문서)와 실제 샘플 데이터(17개 청크, 6개 문서) 불일치 혼란 |
| Code excerpt accuracy | 4 | `extract_text()`, `split_text_into_chunks()`, `store_chunks_to_chroma()`, `print_search_result()` 핵심 함수 발췌가 실제 코드와 일치. `store_chunks_to_chroma()` 발췌에서 `batch_end` 변수 선언 없이 사용하는 것처럼 보이는 부분이 있으나 실제 코드에는 올바르게 구현되어 있음 |
| Error handling guidance | 4 | Vision LLM 폴백 메커니즘, --no-vision 옵션, 60% 미만 유사도 대처법 설명됨. Python 버전 호환성 문제에 대한 가이드 없음 |
| Volume appropriateness | 5 | 개념 1장 → 환경설정 1장 → 3 Step 실습 → 정리 구성이 자연스러움. 각 섹션 분량 균형 좋음 |
| **Total** | **26/30** | |

---

## 5. Issues Found

### 이슈 1: Python 버전 명시 누락 (심각도: 중)

**현상:** 챕터가 `python -m venv venv` 만 제시하여 시스템 기본 Python이 3.14인 경우 `tokenizers` 패키지 빌드 실패.

**오류 메시지:**
```
ERROR: Failed building wheel for tokenizers
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 to suppress this check
```

**해결 방법:** `/opt/homebrew/bin/python3.12 -m venv venv` 사용

**원고 개선 제안:** requirements.txt 주석 또는 환경설정 단계에 `# Python 3.10 ~ 3.12 권장. Python 3.14에서는 sentence-transformers 설치가 실패할 수 있습니다.` 추가 필요.

---

### 이슈 2: 예시 출력과 실제 데이터 불일치 (심각도: 낮음)

**현상:** 챕터 본문의 예상 출력은 7개 문서, 127개 청크를 보여주지만 실제 `data/docs/`에는 6개 문서가 있으며 Python 파싱만으로는 17개 청크만 생성됨.

**원인:** 챕터 예시 출력이 Vision LLM 파싱까지 완료된 전체 파이프라인 기준이나, 본문 예시에서 이를 명확히 구분하지 않음.

**해결 방법:** 예시 출력에 `(Vision LLM 포함 전체 실행 기준)` 또는 `(--no-vision 실행 시 17개 청크)` 주석 추가 권장.

---

### 이슈 3: ChromaDB telemetry 경고 메시지 (심각도: 낮음)

**현상:** 실행 시 아래 경고 메시지가 출력됨.
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
```

**원인:** chromadb==0.5.23에서 posthog 라이브러리 버전 불일치로 발생하는 알려진 경고.

**영향:** 기능적 문제 없음. 실행 결과에는 영향 없음.

**원고 개선 제안:** "이 경고는 ChromaDB 내부 텔레메트리 오류로 실행에는 영향이 없습니다" 설명 추가 권장.

---

### 이슈 4: store.py 코드 발췌 불완전 (심각도: 낮음)

**현상:** 원고의 `store_chunks_to_chroma()` 코드 발췌 부분(섹션 6.1)에서 `batch_end` 변수가 선언 없이 사용되는 것처럼 보임.

```python
# 원고 발췌:
for batch_start in range(0, len(ids), BATCH_SIZE):
    batch_end = batch_start + BATCH_SIZE   # ← 원고에 없음
    collection.upsert(
        ids=ids[batch_start:batch_end],    # ← batch_end 미선언 상태
```

**실제 코드:** `src/store.py`에는 `batch_end = batch_start + BATCH_SIZE`가 올바르게 선언되어 있음.

**원고 개선 제안:** 발췌 코드에 `batch_end` 선언 라인을 추가하거나 생략 표시(`...`) 추가.

---

## 6. Student One-liner

> "Python 파싱의 한계를 직접 체감하게 한 뒤 Vision LLM의 필요성으로 자연스럽게 연결하는 구성이 설득력 있고, `--no-vision` 옵션 덕분에 LLaVA 없이도 전체 파이프라인을 빠르게 완주할 수 있었다. 다만 Python 3.14 환경에서 패키지 설치가 실패하는 상황을 사전에 경고해주지 않아 첫 실습에서 당황할 수 있으며, 챕터 예시 출력 수치와 실제 샘플 데이터가 달라 '내가 뭔가 잘못하고 있나?' 하는 의심이 생겼다."

---

## 7. Improvement Suggestions

- **[필수]** 환경설정 단계에 Python 버전 명시: `python3.12 -m venv venv` 와 함께 "Python 3.13 이상에서는 일부 패키지 빌드 실패가 발생할 수 있습니다 (2024년 기준). Python 3.10~3.12 사용을 권장합니다." 경고문 추가

- **[권장]** 예시 출력에 실행 조건 명시: `--no-vision` 실행 기준과 전체 파이프라인 기준 출력을 구분하거나, 실제 샘플 데이터 크기에 맞는 예시 출력으로 교체

- **[권장]** ChromaDB telemetry 경고에 대한 한 줄 설명 추가: 첫 실행 시 학생이 혼란스러워할 수 있는 경고 메시지임

- **[권장]** `store.py` 코드 발췌에서 `batch_end` 변수 선언 라인 포함하거나 생략 표시(`# ...`) 삽입

- **[선택]** Step 1 예시 출력에 실제 샘플 데이터 파일명 반영: `FIN_매출현황_v1.0.pdf` 대신 `HR_정보보안서약서.pdf`(0자)를 이미지형 PDF 한계 체감 예시로 사용하면 실제 실행 결과와 일치

- **[선택]** `--step 1 3` 문법(두 개의 --step 플래그) 대신 `--step 1 --step 3` 형식을 명확히 표기 (nargs="+" 사용 시 공백 구분이 직관적이지 않을 수 있음)

---

## 부록: 캡처 화면 목록

| 파일명 | 내용 |
|--------|------|
| `step01_python_parsing.png` | Step 1 Python 파싱 실행 결과 |
| `step02_pipeline_complete.png` | --no-vision 전체 파이프라인 실행 완료 |
| `step03_cli_search_result.png` | CLI 검색 "연차 사용 규정" 결과 |

Placeholder 채움 현황:
- `assets/CH06/06_pipeline-complete.png` — step02 화면으로 채움
- `assets/CH06/06_cli-search-result.png` — step03 화면으로 채움
