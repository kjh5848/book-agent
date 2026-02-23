# CH05 예제 코드 명세 — 사내 문서 표준화

## 1. 프로젝트 유형
인프라·설명 챕터. 별도 GitHub 레포 없음. 가이드라인 문서 + 메타데이터 스키마 파일만 생성.

## 2. 디렉토리 구조

```
CH05_사내문서표준화/
├── README.md
├── data/
│   ├── metadata_schema.json           ← 섹션 5: 메타데이터 스키마 정의
│   ├── sample_raw/
│   │   └── hr_policy_raw.txt          ← 전처리 전 원본 예시 (헤더/푸터/불필요 공백 포함)
│   └── sample_clean/
│       └── HR_취업규칙_v1.0.md        ← 전처리 후 네이밍 표준 적용 + Markdown 변환
└── guides/
    ├── collection_strategy.md         ← 섹션 2: 수집 전략 매트릭스 (PDF/Word/HWP/Excel)
    ├── preprocessing_rules.md         ← 섹션 3: 전처리 정규화 규칙 표
    └── naming_convention.md           ← 섹션 4: 네이밍 표준 규칙 + 잘못된 사례 vs 올바른 사례
```

## 3. 파일별 상세 명세

### `data/metadata_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "사내 문서 메타데이터 스키마",
  "type": "object",
  "required": ["doc_id", "source_file", "department", "created_date", "version", "doc_type"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "문서 고유 ID (UUID 형식)",
      "example": "doc-2024-hr-001"
    },
    "source_file": {
      "type": "string",
      "description": "원본 파일명 (경로 포함)",
      "example": "hr/연차규정_v2.1.pdf"
    },
    "department": {
      "type": "string",
      "enum": ["HR", "기획", "마케팅", "개발", "재무", "전사"],
      "description": "문서 소유 부서"
    },
    "created_date": {
      "type": "string",
      "format": "date",
      "description": "문서 작성일 (YYYY-MM-DD)",
      "example": "2024-01-15"
    },
    "version": {
      "type": "string",
      "description": "문서 버전",
      "example": "v2.1"
    },
    "doc_type": {
      "type": "string",
      "enum": ["규정", "가이드", "보고서", "공지", "매뉴얼"],
      "description": "문서 유형"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "검색 태그 (선택)",
      "example": ["연차", "휴가", "인사"]
    },
    "page_count": {
      "type": "integer",
      "description": "총 페이지 수"
    }
  }
}
```

### `data/sample_raw/hr_policy_raw.txt`
전처리 전 원본 예시:
- 페이지 헤더: "사내 인사 규정 | 대외비 | 2024.01"
- 페이지 푸터: "- 3 -"
- 불필요한 공백과 개행
- 특수문자 혼재

### `data/sample_clean/HR_취업규칙_v1.0.md`
전처리 후 네이밍 표준 + Markdown 변환 예시:
- 파일명: `HR_취업규칙_v1.0.md` (네이밍 규칙 `{부서}_{문서명}_{버전}.확장자` 적용)
- 헤더/푸터 제거, 공백 정규화
- **Markdown 형식으로 변환**: `#` 헤더, `|` 표, `- ` 목록 사용
- raw 파일과 diff로 전처리 전/후 비교 가능

### `guides/collection_strategy.md`
문서 유형별 수집 우선순위 매트릭스:
| 유형 | 우선순위 | 수집 방법 | AI 개입 | 전처리 난이도 |
|------|---------|---------|--------|------------|
| PDF (텍스트 레이어 있음) | 높음 | pdfplumber (규칙 기반) | 선택 | 낮음 |
| Word (.docx) | 높음 | python-docx | 불필요 | 낮음 |
| Markdown | 높음 | 직접 읽기 | 불필요 | 없음 |
| HWP / HWPX | 중간 | PDF 변환 후 처리 | 선택 | 중간~높음 |
| PDF (스캔/복합 도해) | 낮음 | Vision LLM (최후 수단) | 필수 | 높음 |
| Excel | 중간 | pandas + openpyxl | 선택 | 중간 |

> **핵심 원칙**: 규칙 기반 파싱(라이브러리)으로 최대한 처리하고, AI(Vision LLM)는 파이썬 코드로 규칙화 불가능한 시각적 한계에서만 사용.
> HWP는 PDF로 저장 후 PDF 파이프라인으로 위임하는 것을 권장.

### `guides/naming_convention.md`
사내 문서 네이밍 표준 규칙:

**포맷**: `{부서}_{문서명}_{버전}.확장자`
- 부서: `HR`, `FIN`, `SEC`, `OPS`, `DEV` 등 영문 약어
- 문서명: 한글 또는 영문, 공백 없이
- 버전: `v1.0`, `v2.1` 형식

**올바른 사례 vs 잘못된 사례**:
| 잘못된 사례 ❌ | 올바른 사례 ✅ |
|-------------|-------------|
| `2025년본.pdf` | `HR_취업규칙_v1.0.pdf` |
| `최종수정(진짜최종).xlsx` | `FIN_부서별예산기안서_v3.2.xlsx` |
| `보안규정.docx` | `SEC_보안규정_v1.0.docx` |
| `신규서비스런칭전략.pdf` | `OPS_신규서비스런칭전략_v1.0.pdf` |

**폴더 구조** (부서별 분리):
```
data/docs/
├── hr/          ← HR 부서 문서
├── finance/     ← Finance 부서 문서
├── ops/         ← Operations 부서 문서
└── security/    ← Security 부서 문서
```

**파일명 → 메타데이터 자동 파싱 예시**:
```python
def parse_filename_metadata(filename: str) -> dict:
    """
    HR_취업규칙_v1.0.pdf → {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}
    """
    stem = Path(filename).stem  # HR_취업규칙_v1.0
    parts = stem.split("_", 2)   # ["HR", "취업규칙", "v1.0"]
    return {
        "department": parts[0] if len(parts) > 0 else "UNKNOWN",
        "doc_name": parts[1] if len(parts) > 1 else stem,
        "version": parts[2] if len(parts) > 2 else "v1.0",
    }
```

### `guides/preprocessing_rules.md`
전처리 규칙 표:
| 항목 | 처리 방법 | 예시 |
|------|---------|------|
| 헤더/푸터 제거 | 정규식으로 페이지 번호, 문서명 반복 패턴 제거 | "- 3 -" → 삭제 |
| 인코딩 통일 | UTF-8 강제 변환 | EUC-KR → UTF-8 |
| 과도한 공백 | 2개 이상 연속 공백 → 단일 공백 | "연차  규정" → "연차 규정" |
| 표/이미지 | 표: 텍스트 추출 시 셀 내용 유지 / 이미지: 10장 OCR 섹션 참조 | |

## 4. 실행 시나리오
코드 실행 없음. 독자는 파일을 열어 내용을 확인한다.

```bash
# 메타데이터 스키마 확인
cat data/metadata_schema.json

# 전처리 전/후 비교 (raw txt vs 정제된 Markdown)
diff data/sample_raw/hr_policy_raw.txt "data/sample_clean/HR_취업규칙_v1.0.md"

# 네이밍 규칙 확인
cat guides/naming_convention.md

# 수집 전략 확인
cat guides/collection_strategy.md
```

## 5. 의존성
없음 (코드 실행 불필요).

## 6. CH06와의 연결
`data/metadata_schema.json`의 필드는 CH06 `store.py`의 `add_documents()` 함수에서
ChromaDB 문서 메타데이터로 그대로 사용된다.

```python
# CH06 store.py에서 사용 예시
collection.add(
    documents=[chunk_text],
    metadatas=[{
        "doc_id": "doc-2024-hr-001",
        "source_file": "hr/연차규정_v2.1.pdf",
        "department": "HR",
        "page_count": 5
    }],
    ids=[chunk_id]
)
```
