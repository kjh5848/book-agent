# CH05 사내 문서 수집 전략과 문서 표준 만들기 — Reader Review Report


---

## 1. Chapter Overview

| Item | Content |
|------|---------|
| Learning objective | 사내 문서 수집 표준 규칙(파일명, 폴더 구조, 메타데이터)을 정립하고 `validator.py`로 6개 문서를 검증하여 `outputs/metadata.json`을 생성한다 |
| Prerequisites | CH02 개발 환경 설정 완료, CH04 FastAPI+PostgreSQL 사내 시스템 구축 완료 |
| Number of execution steps | 4단계 (환경 확인 → 의존성 설치 → validator.py 실행 → metadata.json 확인) |

---

## 2. Environment Check Results

| Item | Requirement | Actual Version/Status | Result |
|------|-------------|-----------------------|--------|
| Python | 3.10+ | 3.14.3 | PASS |
| Docker | 불필요 (CH05는 외부 서비스 없음) | 해당 없음 | SKIP |
| Ollama | 불필요 (CH05는 외부 서비스 없음) | 해당 없음 | SKIP |
| data/docs/ 문서 파일 | 6개 파일 (hr/2, security/1, ops/1, finance/2) | 6개 확인 | PASS |
| requirements.txt | pypdf==4.3.1, python-docx==1.1.2, openpyxl==3.1.5 | 정상 존재 | PASS |

---

## 3. Step-by-Step Execution Results

### STEP 1: 폴더 구조 확인 및 파일 존재 검증

**Manuscript instruction:** "실제 PDF, DOCX, XLSX 파일이 이미 `data/docs/` 폴더에 포함되어 있습니다. 별도로 문서를 준비할 필요가 없습니다."

**Executed command:**
```bash
find data/docs/ -type f
```

**Actual output:**
```
data/docs/security/SEC_보안규정_v1.0.docx
data/docs/hr/HR_정보보안서약서.pdf
data/docs/hr/HR_취업규칙_v1.0.pdf
data/docs/ops/OPS_신규서비스_런칭전략.pdf
data/docs/finance/FIN_부서별_예산기안서.xlsx
data/docs/finance/FIN_2025_상반기_매출현황.xlsx
```

**Result:** PASS

> 챕터에 명시된 폴더 구조 그대로 6개 문서가 존재합니다. 주의사항의 "legacy/ex01-1/data/docs/ 파일 복사" 작업이 이미 완료된 상태였습니다.

---

### STEP 2: 가상환경 생성 및 의존성 설치

**Manuscript instruction:** "의존성을 설치합니다."

**Executed command:**
```bash
python3 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
```

**Actual output:**
```
Successfully installed et-xmlfile-2.0.0 lxml-6.0.2 openpyxl-3.1.5 pypdf-4.3.1 python-docx-1.1.2 typing-extensions-4.15.0
```

**Result:** PASS

> 3개 패키지(pypdf, python-docx, openpyxl) 외에 의존성인 lxml, et-xmlfile, typing-extensions도 함께 설치되었습니다. `requirements.txt` 상단 3줄만 기재되어 있으나 설치는 정상적으로 완료됩니다.

---

### STEP 3: validator.py 실행

**Manuscript instruction:** "다음 명령으로 검증을 실행합니다."

**Executed command:**
```bash
python src/validator.py
```

**Actual output:**
```
============================================================
   CH05 문서 수집 표준화 검증 도구
============================================================
문서 폴더: .../data/docs
출력 경로: .../outputs/metadata.json

총 6개 문서 검증 시작...

------------------------------------------------------------
[WARN] FIN_2025_상반기_매출현황.xlsx
       부서: 재무 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: FIN_2025_상반기_매출현황_v1.0.xlsx)

[WARN] FIN_부서별_예산기안서.xlsx
       부서: 재무 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: FIN_부서별_예산기안서_v1.0.xlsx)

[WARN] HR_정보보안서약서.pdf
       부서: 인사 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: HR_정보보안서약서_v1.0.pdf)

[PASS] HR_취업규칙_v1.0.pdf
       부서: 인사 | 버전: 1.0
       메시지: 파일명 규칙 준수

[WARN] OPS_신규서비스_런칭전략.pdf
       부서: 운영 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: OPS_신규서비스_런칭전략_v1.0.pdf)

[PASS] SEC_보안규정_v1.0.docx
       부서: 보안 | 버전: 1.0
       메시지: 파일명 규칙 준수

메타데이터 저장 완료: .../outputs/metadata.json

============================================================
            문서 검증 결과 요약
============================================================
  전체 문서:  6개
  PASS:       2개  (33.3%)
  WARN:       4개  (66.7%)
  FAIL:       0개  (0.0%)
------------------------------------------------------------

조치가 필요한 항목:
  [WARN] FIN_2025_상반기_매출현황.xlsx
         → 버전 정보 누락 (권장 형식: FIN_2025_상반기_매출현황_v1.0.xlsx)
  [WARN] FIN_부서별_예산기안서.xlsx
         → 버전 정보 누락 (권장 형식: FIN_부서별_예산기안서_v1.0.xlsx)
  [WARN] HR_정보보안서약서.pdf
         → 버전 정보 누락 (권장 형식: HR_정보보안서약서_v1.0.pdf)
  [WARN] OPS_신규서비스_런칭전략.pdf
         → 버전 정보 누락 (권장 형식: OPS_신규서비스_런칭전략_v1.0.pdf)
============================================================

최종 판정: WARN (4개 문서에 경고가 있습니다. 표준 규칙 적용을 권장합니다.)
```

**Screen capture:**
![validator.py 실행 결과](../assets/CH05/step01_validator_run.png)

**Result:** PASS

> 챕터의 예상 출력과 비교했을 때 구조가 정확히 일치합니다. 챕터 예상 출력에는 PASS 문서가 2개(HR_취업규칙, SEC_보안규정)로 표시되어 있으며 실제 실행 결과도 동일합니다. 조치 필요 항목 상세 목록이 실제 출력에 추가로 나타나는데, 이 부분은 챕터에서 예상 출력에 생략되어 있습니다.

---

### STEP 4: metadata.json 확인

**Manuscript instruction:** "실행 후 생성된 `outputs/metadata.json`을 열어보면 다음과 같은 구조입니다."

**Executed command:**
```bash
cat outputs/metadata.json
```

**Actual output (일부):**
```json
{
  "generated_at": "2026-02-27 11:12:14",
  "total_documents": 6,
  "documents": [
    {
      "doc_id": "HR_취업규칙_1.0",
      "filename": "HR_취업규칙_v1.0.pdf",
      "title": "취업규칙",
      "department": "인사",
      "department_code": "HR",
      "version": "1.0",
      "date": "2026-02-27",
      "format": "PDF",
      "file_size_bytes": 908545,
      "relative_path": "...(절대 경로)...",
      "validation_status": "PASS",
      "validation_message": "파일명 규칙 준수"
    },
    ...
  ]
}
```

**Result:** PASS

> 챕터 예상 JSON과 구조가 일치합니다. 실제 코드에는 챕터 예상 출력에 없는 `department_code`, `file_size_bytes`, `relative_path` 필드가 추가로 포함되어 있습니다. 이는 실제 코드가 챕터 예상 출력보다 더 풍부한 정보를 제공하는 긍정적 차이입니다.

---

## 4. Chapter Manuscript Quality Evaluation

| Item | Score (5 pts) | Rationale |
|------|--------------|-----------|
| Explanation sufficiency | 5 | "Garbage In, Garbage Out" 원칙 도입 → 문서 표준 필요성 → 실습 순서가 자연스럽게 연결됩니다. 학생이 왜 이 작업을 해야 하는지 명확히 이해하고 시작할 수 있습니다. |
| Why explanation | 5 | 파일명 규칙 3가지 이유(버전 관리, 부서 분류, 출처 추적), 메타데이터 설계 이유(CH10 Self-Query Retriever 연결), 폴더 구조 이유 등 모든 설계 결정에 이유 설명이 붙어 있습니다. |
| Execution reproducibility | 4 | `python src/validator.py` 실행 결과가 챕터 예상 출력과 거의 정확히 일치합니다. 다만 챕터 예상 출력에는 "조치가 필요한 항목:" 하단 상세 목록이 생략되어 있어 실제 출력과 약간 차이가 납니다. |
| Code excerpt accuracy | 4 | 챕터 본문의 코드 조각(validate_filename, extract_metadata, main)이 실제 `src/validator.py`와 내용이 일치합니다. 다만 챕터에서는 `...` 생략 표현으로 부분 발췌하므로, 전체 코드를 보려면 GitHub 참조가 필요합니다. |
| Error handling guidance | 4 | FAIL/WARN 판정 의미와 대처 방법이 안내박스로 제공됩니다. 그러나 `pip install` 중 버전 충돌이나 Python 3.14 호환성 이슈에 대한 사전 안내는 없습니다. |
| Volume appropriateness | 5 | 개념 설명(3섹션) + 실습(1섹션)의 비율이 적절합니다. 개념 파트가 길지만 각 소제목이 명확하여 스킵하기 쉽습니다. 실습 파트는 4단계로 간결하게 구성되어 있습니다. |
| **Total** | **27/30** | |

---

## 5. Issues Found

### 5-1. 챕터 예상 출력과 실제 출력의 소폭 차이

**위치:** 섹션 4.3 `validator.py` 실행 예상 출력

**내용:** 챕터 예상 출력에는 3개 문서(FIN_매출현황, HR_취업규칙, SEC_보안규정)만 표시되지만, 실제 출력은 6개 문서 전체(FIN_매출현황, FIN_예산기안서, HR_정보보안서약서, HR_취업규칙, OPS_런칭전략, SEC_보안규정)가 알파벳 정렬 순으로 출력됩니다. 또한 요약 하단에 "조치가 필요한 항목:" 상세 목록이 추가로 표시됩니다.

**영향:** 낮음. 학생이 일부 출력이 다르다고 혼란을 느낄 수 있으나, 최종 판정(WARN)은 동일합니다.

**제안:** 예상 출력을 6개 문서 전체로 업데이트하거나, "(...중략...)"으로 생략 표시를 명시합니다.

---

### 5-2. metadata.json의 `relative_path` 필드가 절대 경로를 담음

**위치:** `src/validator.py` 154번째 줄 (`"relative_path": str(file_path)`)

**내용:** 필드명은 `relative_path`이지만 실제 값은 시스템 전체 절대 경로(`/Users/nomadlab/...`)입니다. CH06에서 이 경로를 사용하는 코드가 절대 경로를 기대한다면 문제가 없지만, 다른 환경으로 이동하거나 폴더 구조가 달라지면 CH06 파이프라인이 깨질 수 있습니다.

**제안:** 필드명을 `absolute_path`로 변경하거나, `docs_dir`를 기준으로 한 실제 상대 경로를 저장합니다.

---

### 5-3. requirements.txt에 간접 의존성이 명시되지 않음

**위치:** `requirements.txt`

**내용:** 직접 의존성 3개(pypdf, python-docx, openpyxl)만 명시되어 있고, python-docx가 필요로 하는 lxml은 명시되지 않습니다. Python 3.14 환경에서는 lxml의 바이너리 빌드가 없을 경우 설치 실패할 수 있습니다.

**실제 영향:** Python 3.14.3 + macOS 환경에서는 lxml 6.0.2 universal2 wheel이 제공되어 정상 설치되었습니다. 단 Linux x86_64 Python 3.14 환경에서는 빌드 실패 가능성이 있습니다.

**제안:** 챕터에 "Python 3.12 이하 권장" 또는 "lxml 빌드 실패 시 해결 방법" 안내를 추가합니다.

---

### 5-4. 챕터 문서 표에서 파일 수 불일치

**위치:** 섹션 1.2 교재용 문서 세트 표

**내용:** 표에 6개 문서가 나열되어 있으나, 섹션 4.2 폴더 구조 예시에서도 6개 파일이 표시됩니다. 그런데 챕터 제목 표의 4번째 행과 5번째 행이 모두 FIN(재무) 부서인데, 이 중 하나(`FIN_매출현황`)는 버전이 없어 WARN 처리됩니다. 표 자체에서 이 사실을 미리 언급해 주면 독자가 WARN을 보고 놀라지 않습니다.

**제안:** 섹션 1.2 표에 "버전 없음" 또는 "WARN 예정" 비고를 추가합니다.

---

## 6. Student One-liner

> "Garbage In, Garbage Out" 원칙에서 시작해 파일명 표준 규칙 → 폴더 구조 → 메타데이터 설계까지 RAG 품질의 뿌리를 논리적으로 쌓아 올리는 챕터로, `validator.py` 한 번 실행으로 6개 문서의 규칙 준수 여부를 즉시 확인할 수 있어 개념이 코드로 바로 연결된다는 점이 인상적이었습니다. 예상 출력과 실제 출력 사이의 소폭 차이가 처음에는 혼란스러웠지만, 실행 결과 자체는 완전히 정상이며 CH06 진입 조건(FAIL 0개)도 충족됩니다.

---

## 7. Improvement Suggestions

- 섹션 4.3 예상 출력을 6개 문서 전체 출력으로 업데이트하거나 `(...중략...)` 표기를 명시하여 실제 출력과의 불일치로 인한 학생 혼란을 방지합니다.
- `validator.py`의 `relative_path` 필드명을 `absolute_path`로 수정하거나, 실제로 상대 경로(`docs_dir` 기준)를 계산하여 저장하도록 수정합니다.
- 섹션 1.2 문서 목록 표에 버전 유무 컬럼 또는 "예상 판정" 컬럼을 추가하여 독자가 WARN 결과를 사전에 예측할 수 있도록 합니다.
- Python 버전 요구사항을 챕터 시작 부분에 명시합니다 (예: "Python 3.10–3.12 권장"). Python 3.14에서도 동작하지만 일부 환경에서 lxml 빌드 이슈가 발생할 수 있습니다.
- 챕터 예상 출력에서 생략된 "조치가 필요한 항목:" 하단 상세 목록 부분을 포함하여 예상 출력의 완성도를 높입니다.
