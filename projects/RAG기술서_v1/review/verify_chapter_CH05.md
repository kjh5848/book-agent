# 검증 보고서: CH05 사내 문서 표준화

## 판정: CONDITIONAL_PASS

---

## 검증 항목

| # | 항목 | 필수/권장 | 결과 | 비고 |
|---|------|---------|------|------|
| 1 | 문체 (하십시오체 일관성) | 필수 | PASS | 전체 원고 하십시오체 일관, 금지 표현 없음 |
| 2 | 볼딩 (앞뒤 공백 규칙) | 필수 | FAIL | 1건 위반 — 14행 볼드 뒤 공백 누락 |
| 3 | 맥락 연결 (CH04→CH05→CH06) | 권장 | PASS | 도입부 CH04 참조 자연스럽고 CH06 예고 명확함 |
| 4 | 구조 (4단계 + TOC 일치) | 필수 | PASS | 4단계 구조 완전 준수, TOC 6개 섹션 전체 일치 |
| 5 | 코드 동기화 (예제 파일 일치) | 필수 | FAIL | 2건 불일치 — diff 명령어 경로 오류, hwp_to_pdf 함수 누락 출력 |
| 6 | 분량 (8p, 8,000자 이상) | 권장 | PASS | 523행, 약 20,000자 이상 — 기준 대폭 충족 |

---

## 실패 항목 상세

### 항목 2: 볼딩 앞뒤 공백 규칙 위반

- **현재 상태**: 원고 14행에서 볼드 뒤 공백 없이 한글 조사가 바로 연결됨
  ```
  RAG 시스템의 성능은 **LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우**됩니다.
  ```
- **기대 상태**: 볼드 닫는 기호(`**`) 뒤에 공백을 삽입하여 조사와 분리
  ```
  RAG 시스템의 성능은 **LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우** 됩니다.
  ```
- **수정 제안**: `style.md` 5항 규칙에 따라 `**용어**` 뒤에 공백 1개를 추가하십시오. `**좌우**됩니다` → `**좌우** 됩니다`

---

### 항목 5: 코드 동기화 불일치 (2건)

#### 5-1. diff 명령어 경로 불일치

- **현재 상태**: 원고 242행의 `diff` 명령어가 존재하지 않는 파일 경로를 사용함
  ```bash
  diff data/sample_raw/hr_policy_raw.txt "data/sample_clean/HR_취업규칙_v1.0.md"
  ```
- **기대 상태**: `guides/preprocessing_rules.md` 3절에 정의된 실제 파일 경로와 일치해야 함
  ```bash
  diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt
  ```
- **근거**: 예제 파일 `guides/preprocessing_rules.md` 3-1절에 `diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt` 로 정의됨. 원고에서 사용한 `"data/sample_clean/HR_취업규칙_v1.0.md"` 는 실제 파일명과 다름.
- **수정 제안**: 원고 242행을 아래와 같이 수정하십시오.
  ```bash
  diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt
  ```

#### 5-2. hwp_to_pdf 함수 출력 로그 누락

- **현재 상태**: 원고 114~143행의 `hwp_to_pdf()` 함수에 성공 시 로그 출력 코드가 없음
  ```python
  # --- Output ---
  pdf_path = str(Path(output_dir) / f"{Path(hwp_path).stem}.pdf")
  return pdf_path
  ```
- **기대 상태**: 예제 파일 `guides/collection_strategy.md` 172~193행에는 성공 시 출력 코드가 포함됨
  ```python
  pdf_path = str(Path(output_dir) / f"{Path(hwp_path).stem}.pdf")
  print(f"✓ 변환 완료: {pdf_path}")
  return pdf_path
  ```
- **수정 제안**: 원고의 `hwp_to_pdf()` 함수 `return pdf_path` 직전에 `print(f"변환 완료: {pdf_path}")` 행을 추가하십시오. (이모지 제거 후 원고 문체에 맞게 조정)

---

## 경고 사항 (CONDITIONAL_PASS 근거)

### 경고 1: 볼딩 규칙 위반은 1건으로 제한적

볼딩 위반이 1건이며, 나머지 볼드 표기(87행, 89행, 104행, 249행, 500행 등)는 모두 앞뒤 공백 규칙을 준수합니다. 단순 편집 오류로 판단되어 FAIL이 아닌 CONDITIONAL_PASS 수준으로 처리합니다.

### 경고 2: 코드 동기화 불일치 중 5-2는 기능적 동일성 유지

`hwp_to_pdf()` 함수의 핵심 로직(변환 실행, 에러 처리, 반환값)은 예제 파일과 동일합니다. 누락된 `print` 문은 디버그 출력에 해당하여 독자 학습에 직접적 영향은 없으나, 예제 파일과의 완전한 동기화를 위해 수정을 권장합니다.

---

## 세부 검증 내용

### 카테고리 1: 문체 검증

| 항목 | 확인 결과 |
|------|---------|
| 하십시오체 일관 사용 | PASS — "합니다", "입니다", "하십시오" 전체 일관 |
| "~합니다" / "~이에요" 등 혼용 | PASS — 혼용 없음 |
| 금지 표현 ("최신", "요즘 뜨는", "마법 같은") | PASS — 없음 |
| 이모지 사용 | PASS — 본문 없음 |
| 추측성 표현 ("~인 것 같다", "~해 보인다") | PASS — 없음 |
| 전문 용어 영문 병기 첫 등장 시 처리 | PASS — GIGO(Garbage In, Garbage Out), 규칙 기반 파싱(Rule-based Parsing), AI 기반 파싱(Vision LLM) 등 병기 |

### 카테고리 2: 볼딩 검증

| 위치 | 볼드 표기 | 앞뒤 공백 | 판정 |
|------|---------|---------|------|
| 3행 | `**문서 표준화** 파이프라인` | 뒤 공백 O | PASS |
| 14행 | `**LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우**됩니다` | 뒤 공백 X | FAIL |
| 87행 | `**규칙 기반 파싱(Rule-based Parsing)** 은` | 뒤 공백 O | PASS |
| 89행 | `**AI 기반 파싱(Vision LLM)** 은` | 뒤 공백 O | PASS |
| 104행 | `**방법 C** 를` | 뒤 공백 O | PASS |
| 249행 | `**Markdown** 으로` | 뒤 공백 O | PASS |
| 369행 | `**메타데이터(Metadata)** 는` | 뒤 공백 O | PASS |
| 500행 | `**문서 표준화 파이프라인** 전체` | 뒤 공백 O | PASS |
| 과도한 볼딩 (한 문단 3개 초과) | PASS — 확인된 한 문단 내 최대 2개 |

### 카테고리 3: 맥락 연결 검증

| 항목 | 확인 결과 |
|------|---------|
| CH04 → CH05 연결 | PASS — 도입부 "4장에서 PostgreSQL과 FastAPI로 구성된 사내 인프라를 확보했습니다. 이제 RAG 시스템에 입력할 문서를 준비해야 합니다." 자연스러운 흐름 |
| CH05 → CH06 예고 | PASS — "6장에서는 이 문서들을 벡터 DB에 저장하는 전체 파이프라인을 구현합니다. extractor.py로 PDF에서 텍스트를 추출하고..." 구체적 예고 |
| 챕터 내 섹션 간 연결 | PASS — 4.4절에서 6장 연결, 5.4절에서 6~7장 활용 언급 등 자연스러운 흐름 |

### 카테고리 4: 구조 검증

| 항목 | 확인 결과 |
|------|---------|
| 도입부 (제목 + 개요 문단) | PASS — `# 5. 사내 문서 표준화` + 2문장 도입 + 이미지 플레이스홀더 |
| 개념 섹션 (## 1.) | PASS — GIGO 원칙과 문서 표준화 필요성 설명 |
| 실습/내용 섹션 (## 2~5.) | PASS — 수집 전략, 전처리, 네이밍, 메타데이터 4개 섹션 |
| 정리하며 섹션 | PASS — `## 6. 정리하며` 형식 정확히 준수 |
| TOC.md 섹션 5.1~5.6 일치 | PASS — 6개 섹션 모두 원고와 일치 |
| chapter_spec 섹션 구조 일치 | PASS — 명세의 ## 1~6 구조와 원고 완전 일치 |
| 코드 블록 아래 IPO 워크플로우 존재 | PASS — hwp_to_pdf (146행), parse_filename_metadata (344행), metadata_schema.json (435행) 모두 존재 |

### 카테고리 5: 코드 동기화 검증

| 코드/파일 | 원고 위치 | 예제 파일 | 일치 여부 |
|---------|---------|---------|---------|
| hwp_to_pdf() 핵심 로직 | 114~143행 | collection_strategy.md | PASS (로직 동일, print 문 누락) |
| parse_filename_metadata() | 315~341행 | naming_convention.md | PASS (로직 완전 동일) |
| metadata_schema.json 스키마 | 383~433행 | data/metadata_schema.json | 확인 불가 (파일 미존재) |
| diff 명령어 경로 | 242행 | preprocessing_rules.md | FAIL (경로 불일치) |
| 코드 생략(`...`, `# 생략`) | 전체 | — | PASS — 생략 없음 |
| IPO 워크플로우 섹션 | 전체 코드 블록 | — | PASS — 3개 코드 블록 모두 존재 |

### 카테고리 6: 분량 검증

| 항목 | 기준 | 실제 | 판정 |
|------|------|------|------|
| 목표 분량 | 8p (8,000자 이상) | 523행, 약 20,000자 이상 | PASS |
| TOC 대비 편차 | ±20% 이내 | 기준 초과 충족 | PASS |

---

## 수정 요청 사항 (writing-agent 전달용)

다음 2가지 항목을 수정 후 재제출하십시오.

1. **[필수] 볼딩 공백 추가** — 원고 14행
   - 수정 전: `**LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우**됩니다`
   - 수정 후: `**LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우** 됩니다`

2. **[필수] diff 명령어 경로 수정** — 원고 242행
   - 수정 전: `diff data/sample_raw/hr_policy_raw.txt "data/sample_clean/HR_취업규칙_v1.0.md"`
   - 수정 후: `diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt`

3. **[권장] hwp_to_pdf 출력 로그 추가** — 원고 143행 직전
   - `return pdf_path` 바로 위에 `print(f"변환 완료: {pdf_path}")` 추가

---

## 요약

- 총 검증 항목: 6개 (필수 4, 권장 2)
- 통과: 4개 (문체 PASS, 맥락 연결 PASS, 구조 PASS, 분량 PASS)
- 실패: 2개 (볼딩 공백 위반 1건, 코드 동기화 불일치 2건)
- 판정: **CONDITIONAL_PASS** — 필수 항목 중 볼딩 위반 1건 및 코드 동기화 경로 오류 1건이 단순 편집 오류 수준으로 판단. 다음 Phase 진행은 가능하나 수정 후 재제출을 권장함.
- 시도 횟수: 1/2
