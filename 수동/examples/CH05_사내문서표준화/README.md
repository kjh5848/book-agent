# CH05 사내 문서 표준화 — 예제 파일 안내

이 디렉토리는 **5장 사내 문서 표준화** 챕터에서 사용하는 예제 파일을 담고 있습니다.
이 챕터는 별도의 실행 가능한 Python 코드 없이 **가이드라인 문서**와 **샘플 데이터** 중심으로 구성됩니다.
실제 코드 구현은 6장(벡터 DB 구축)에서 시작됩니다.

---

## 디렉토리 구조

```
CH05_사내문서표준화/
├── README.md                          ← 이 파일
├── data/
│   ├── metadata_schema.json           ← 메타데이터 스키마 정의 (JSON Schema)
│   ├── sample_raw/
│   │   └── hr_policy_raw.txt          ← 전처리 전 원본 문서 (헤더/푸터/과도한 공백 포함)
│   └── sample_clean/
│       └── hr_policy_clean.txt        ← 전처리 후 정제 문서
└── guides/
    ├── collection_strategy.md         ← 문서 유형별 수집 전략 + 코드 예시
    └── preprocessing_rules.md         ← 전처리 규칙 표 + Python 전처리 함수
```

---

## 각 파일의 역할

### data/metadata_schema.json

RAG 시스템에 입력되는 모든 사내 문서에 부착되는 **메타데이터 스키마**를 JSON Schema 형식으로 정의합니다.

- `doc_id`, `source_file`, `department`, `created_date`, `version`, `doc_type` 6개 필드가 필수입니다.
- `tags`, `page_count`는 선택 필드입니다.
- 이 스키마는 6장에서 ChromaDB에 문서를 저장할 때 `metadata` 파라미터로 그대로 사용됩니다.

확인 방법:

```bash
cat data/metadata_schema.json
```

### data/sample_raw/hr_policy_raw.txt

전처리 전 원본 문서의 예시입니다. 실제 사내 문서에서 자주 발생하는 문제점을 의도적으로 포함시켰습니다.

포함된 문제점:
- 페이지 헤더: `사내 인사 규정 | 대외비 | 2024.01`
- 페이지 푸터: `- 1 -`, `- 2 -`, `- 3 -`
- 불필요한 연속 공백 및 과도한 개행

### data/sample_clean/hr_policy_clean.txt

`hr_policy_raw.txt`에 `guides/preprocessing_rules.md`의 규칙을 적용한 결과물입니다.

- 헤더/푸터가 제거되었습니다.
- 공백이 단일 공백으로 정규화되었습니다.
- UTF-8 인코딩이 명시된 주석이 상단에 추가되었습니다.

원본과 정제본의 차이를 확인하는 방법:

```bash
diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt
```

`-`로 시작하는 줄이 제거된 내용(헤더/푸터, 과도한 공백)이고,
`+`로 시작하는 줄이 추가된 내용(UTF-8 주석)입니다.

### guides/collection_strategy.md

문서 유형별 수집 우선순위 매트릭스와 Python 수집 코드 예시를 담고 있습니다.

- PDF(텍스트 레이어), Word, Markdown, Excel 각각의 수집 방법을 설명합니다.
- 스캔 PDF(이미지 기반)는 우선순위가 낮으며, 처리 방법은 10장을 참조합니다.

### guides/preprocessing_rules.md

전처리 규칙 표와 실제 실행 가능한 Python 전처리 함수를 제공합니다.

- `remove_header_footer()`: 정규식으로 페이지 번호 및 문서명 패턴 제거
- `normalize_whitespace()`: 연속 공백/개행 정규화
- `normalize_encoding()`: EUC-KR, CP949를 UTF-8로 변환
- `normalize_special_chars()`: 전각 문자, 중점 등 특수문자 정규화
- `preprocess_document()`: 위 함수들을 순서대로 적용하는 파이프라인 함수

---

## CH06과의 연결

이 챕터에서 수립한 기준은 6장에서 직접 사용됩니다.

| 5장에서 정의한 것 | 6장에서 사용되는 곳 |
|-----------------|------------------|
| `metadata_schema.json` 스키마 | ChromaDB `.add()` 호출 시 `metadatas` 파라미터 |
| `preprocessing_rules.md`의 함수들 | `extractor.py`, `chunker.py` 전처리 단계 |
| `collection_strategy.md`의 수집 코드 | `extractor.py` 파일별 추출 로직 |

6장 예제 코드(`CH06_벡터DB구축/`)를 실행하기 전에 이 디렉토리의 파일들을 먼저 숙지하십시오.
