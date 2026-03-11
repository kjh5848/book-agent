# 사내 문서 네이밍(Naming) 표준 규칙

RAG 시스템에 문서를 넣기 전, 파일 이름부터 정리해야 합니다.
`2025년본.pdf`, `최종수정(진짜최종).xlsx` 같은 파일이 그대로 들어가면 메타데이터가 꼬여 검색 품질이 박살납니다.

---

## 1. 네이밍 포맷

```
{부서}_{문서명}_{버전}.확장자
```

| 구성 요소 | 형식 | 예시 |
|----------|------|------|
| 부서 | 영문 약어 대문자 | `HR`, `FIN`, `SEC`, `OPS`, `DEV` |
| 문서명 | 한글 또는 영문, 공백 없이 | `취업규칙`, `예산기안서`, `보안규정` |
| 버전 | `v{major}.{minor}` | `v1.0`, `v2.1`, `v3.0` |
| 확장자 | 원본 형식 그대로 | `.pdf`, `.docx`, `.xlsx`, `.md` |

---

## 2. 올바른 사례 vs 잘못된 사례

| 잘못된 사례 ❌ | 올바른 사례 ✅ | 개선 이유 |
|-------------|-------------|---------|
| `2025년본.pdf` | `HR_취업규칙_v1.0.pdf` | 부서·문서명·버전 모두 불명확 |
| `최종수정(진짜최종).xlsx` | `FIN_부서별예산기안서_v3.2.xlsx` | 특수문자, 버전 추적 불가 |
| `보안규정.docx` | `SEC_보안규정_v1.0.docx` | 부서 정보 없음 |
| `신규서비스런칭전략.pdf` | `OPS_신규서비스런칭전략_v1.0.pdf` | 부서 정보 없음 |
| `HR규정(수정중).pdf` | `HR_취업규칙_v2.0.pdf` | 괄호/한글 상태 표시 금지 |
| `연차규정final.pdf` | `HR_연차규정_v1.1.pdf` | `final` 대신 버전 번호 사용 |

---

## 3. 폴더 구조 (부서별 분리)

파일명뿐 아니라 폴더도 부서별로 분리합니다. 폴더명 자체가 메타데이터입니다.

```
data/docs/
├── hr/               ← HR 부서 문서
│   ├── HR_취업규칙_v1.0.pdf
│   └── HR_연차규정_v2.1.pdf
├── finance/          ← Finance 부서 문서
│   ├── FIN_부서별예산기안서_v3.2.xlsx
│   └── FIN_2024상반기매출현황_v1.0.pdf
├── ops/              ← Operations 부서 문서
│   └── OPS_신규서비스런칭전략_v1.0.pdf
└── security/         ← Security 부서 문서
    └── SEC_보안규정_v1.0.docx
```

---

## 4. 파일명 → 메타데이터 자동 파싱

네이밍 규칙을 따르면 코드 한 줄로 메타데이터를 추출할 수 있습니다.
이 메타데이터는 CH06에서 ChromaDB에 저장되고, CH07에서 부서별 필터 검색에 사용됩니다.

```python
from pathlib import Path

def parse_filename_metadata(filename: str) -> dict:
    """
    네이밍 규칙 {부서}_{문서명}_{버전}.확장자 에서 메타데이터를 자동 추출합니다.

    Args:
        filename: 파일명 (경로 포함 가능)

    Returns:
        {"department": str, "doc_name": str, "version": str, "source": str}

    Example:
        >>> parse_filename_metadata("HR_취업규칙_v1.0.pdf")
        {"department": "HR", "doc_name": "취업규칙", "version": "v1.0", "source": "HR_취업규칙_v1.0.pdf"}
    """
    stem = Path(filename).stem        # HR_취업규칙_v1.0
    parts = stem.split("_", 2)        # ["HR", "취업규칙", "v1.0"]
    return {
        "department": parts[0] if len(parts) > 0 else "UNKNOWN",
        "doc_name":   parts[1] if len(parts) > 1 else stem,
        "version":    parts[2] if len(parts) > 2 else "v1.0",
        "source":     Path(filename).name,
    }


# 실행 예시
if __name__ == "__main__":
    files = [
        "HR_취업규칙_v1.0.pdf",
        "FIN_부서별예산기안서_v3.2.xlsx",
        "SEC_보안규정_v1.0.docx",
    ]
    for f in files:
        meta = parse_filename_metadata(f)
        print(f"{f:40s} → {meta}")
```

**실행 결과**:
```
HR_취업규칙_v1.0.pdf                     → {'department': 'HR', 'doc_name': '취업규칙', 'version': 'v1.0', 'source': 'HR_취업규칙_v1.0.pdf'}
FIN_부서별예산기안서_v3.2.xlsx            → {'department': 'FIN', 'doc_name': '부서별예산기안서', 'version': 'v3.2', 'source': 'FIN_부서별예산기안서_v3.2.xlsx'}
SEC_보안규정_v1.0.docx                   → {'department': 'SEC', 'doc_name': '보안규정', 'version': 'v1.0', 'source': 'SEC_보안규정_v1.0.docx'}
```

---

## 5. CH06과의 연결

`parse_filename_metadata()`는 CH06 `extractor.py`에 그대로 이식됩니다.

```python
# CH06 extractor.py에서 사용 예시
pages = extract_text_pdfplumber("data/HR_취업규칙_v1.0.pdf")
meta  = parse_filename_metadata("HR_취업규칙_v1.0.pdf")

# ChromaDB에 저장 시 메타데이터로 사용
chunks = fixed_size_chunk(pages, source=meta["source"])
# → 각 chunk의 metadata에 department="HR", version="v1.0" 자동 포함

# CH07 검색 시 부서 필터 가능
results = search(collection, query_embedding, filter_dept="HR")
```

---

## 6. 네이밍 규칙 체크리스트

문서를 RAG 시스템에 추가하기 전 아래 항목을 확인하십시오.

- [ ] 파일명이 `{부서}_{문서명}_{버전}.확장자` 형식인가
- [ ] 부서 코드가 영문 대문자 약어인가 (`HR`, `FIN`, `SEC`, `OPS`, `DEV`)
- [ ] 문서명에 공백, 괄호, 특수문자가 없는가
- [ ] 버전이 `v{숫자}.{숫자}` 형식인가 (`final`, `최종`, `수정중` 사용 금지)
- [ ] 동일 부서 문서가 해당 부서 폴더(`hr/`, `finance/` 등)에 위치하는가
- [ ] HWP 파일은 PDF로 변환 후 동일 네이밍 규칙 적용했는가
