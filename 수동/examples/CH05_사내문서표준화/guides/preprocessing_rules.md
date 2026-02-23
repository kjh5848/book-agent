# 문서 전처리 규칙 가이드

이 가이드는 수집된 사내 문서를 RAG 시스템에 입력하기 전에 적용해야 할 전처리 규칙을 정의합니다.
전처리 품질은 6장 벡터 DB 검색 정확도와 7장 Q&A 응답 품질에 직접적인 영향을 미칩니다.

---

## 1. 전처리 규칙 표

| 항목 | 처리 방법 | 예시 |
|------|---------|------|
| 헤더/푸터 제거 | 정규식으로 페이지 번호, 문서명 반복 패턴 제거 | `"- 3 -"` → 삭제 |
| 인코딩 통일 | UTF-8 강제 변환 | EUC-KR → UTF-8 |
| 과도한 공백 | 2개 이상 연속 공백 → 단일 공백 | `"연차  규정"` → `"연차 규정"` |
| 중복 개행 | 3개 이상 연속 개행 → 최대 2개 | `"\n\n\n\n"` → `"\n\n"` |
| 표/이미지 | 표: 텍스트 추출 시 셀 내용 유지 / 이미지: 10장 OCR 섹션 참조 | `"항목 \| 값"` 형식 유지 |
| 선행/후행 공백 | 각 줄의 시작·끝 공백 제거 | `"  제1조  "` → `"제1조"` |
| 특수문자 정규화 | 전각 문자 → 반각, 불필요한 특수문자 제거 | `"∙"` → `"-"` |

---

## 2. Python 전처리 함수

아래 함수들은 실제 전처리 파이프라인에서 바로 사용할 수 있습니다.

### 2-1. 기본 전처리 함수

```python
import re


def remove_header_footer(text: str) -> str:
    """
    문서에 반복적으로 등장하는 헤더와 푸터 패턴을 제거합니다.

    제거 대상:
    - 페이지 번호 패턴: "- 1 -", "- 2 -", "Page 1" 등
    - 문서명 반복 패턴: 짧은 줄이 여러 페이지에 반복되는 경우

    Args:
        text: 원본 텍스트

    Returns:
        헤더/푸터가 제거된 텍스트
    """
    # 페이지 번호 패턴 제거 (예: "- 1 -", "- 12 -", "Page 1", "1 / 10")
    text = re.sub(r"-\s*\d+\s*-", "", text)
    text = re.sub(r"Page\s+\d+(\s*/\s*\d+)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+\s*/\s*\d+\s*쪽", "", text)

    # "대외비", "기밀" 등 문서 분류 마크 제거 (선택적 적용)
    text = re.sub(r"\|\s*(대외비|기밀|내부용|사내)\s*\|", "", text)

    # 날짜 패턴만 있는 줄 제거 (예: "2024.01", "2024-01-15" 단독 줄)
    text = re.sub(r"^\s*\d{4}[.\-]\d{2}([.\-]\d{2})?\s*$", "", text, flags=re.MULTILINE)

    return text


def normalize_whitespace(text: str) -> str:
    """
    과도한 공백과 개행을 정규화합니다.

    처리 항목:
    - 2개 이상 연속 공백 → 단일 공백
    - 3개 이상 연속 개행 → 최대 2개
    - 각 줄의 선행/후행 공백 제거

    Args:
        text: 전처리 중인 텍스트

    Returns:
        공백이 정규화된 텍스트
    """
    # 각 줄의 선행/후행 공백 제거
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # 2개 이상 연속 공백 → 단일 공백
    text = re.sub(r" {2,}", " ", text)

    # 3개 이상 연속 개행 → 최대 2개
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_encoding(raw_bytes: bytes) -> str:
    """
    다양한 인코딩의 원본 바이트를 UTF-8 문자열로 변환합니다.

    시도 순서: UTF-8 → EUC-KR → CP949 → UTF-8 (오류 무시)

    Args:
        raw_bytes: 파일에서 읽은 원본 바이트

    Returns:
        UTF-8로 디코딩된 문자열
    """
    for encoding in ["utf-8", "euc-kr", "cp949"]:
        try:
            return raw_bytes.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue

    # 모든 인코딩 실패 시 오류 문자 무시하고 UTF-8로 강제 변환
    return raw_bytes.decode("utf-8", errors="ignore")


def normalize_special_chars(text: str) -> str:
    """
    전각 문자와 불필요한 특수문자를 정규화합니다.

    처리 항목:
    - 전각 숫자/영문 → 반각 (① ② ③ → ① 유지, 단 ｆｏｏ → foo)
    - 중점(·, ∙, •) → 하이픈(-) 통일
    - 말줄임표(…) → 마침표 3개(...)

    Args:
        text: 전처리 중인 텍스트

    Returns:
        특수문자가 정규화된 텍스트
    """
    # 전각 공백 → 반각 공백
    text = text.replace("\u3000", " ")

    # 중점 계열 → 하이픈
    text = re.sub(r"[·∙•]", "-", text)

    # 말줄임표 → 마침표 3개
    text = text.replace("…", "...")

    # 전각 영문/숫자 → 반각 (ｆｏｏ → foo)
    result = []
    for char in text:
        code = ord(char)
        if 0xFF01 <= code <= 0xFF5E:  # 전각 알파벳/숫자 범위
            result.append(chr(code - 0xFEE0))
        else:
            result.append(char)

    return "".join(result)
```

### 2-2. 파이프라인 통합 함수

위의 개별 함수들을 하나의 파이프라인으로 묶습니다.

```python
def preprocess_document(raw_text: str) -> str:
    """
    원본 텍스트에 전체 전처리 파이프라인을 순서대로 적용합니다.

    처리 순서:
    1. 특수문자 정규화
    2. 헤더/푸터 제거
    3. 공백 정규화

    순서가 중요합니다. 공백 정규화는 항상 마지막에 수행하십시오.

    Args:
        raw_text: 파일에서 추출된 원본 텍스트

    Returns:
        전처리가 완료된 정제 텍스트
    """
    # 1단계: 특수문자 정규화
    text = normalize_special_chars(raw_text)

    # 2단계: 헤더/푸터 제거
    text = remove_header_footer(text)

    # 3단계: 공백 정규화
    text = normalize_whitespace(text)

    return text


# 파일 단위 전처리 실행 예시
if __name__ == "__main__":
    # 바이트로 읽어 인코딩 자동 감지
    with open("data/sample_raw/hr_policy_raw.txt", "rb") as f:
        raw_bytes = f.read()

    # 인코딩 정규화
    raw_text = normalize_encoding(raw_bytes)

    # 전체 전처리 파이프라인 적용
    clean_text = preprocess_document(raw_text)

    # 정제된 텍스트 저장
    with open("data/sample_clean/hr_policy_clean.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

    print(f"전처리 완료: {len(raw_text)}자 → {len(clean_text)}자")
```

---

## 3. 전처리 결과 검증 방법

전처리가 올바르게 적용되었는지 확인하는 간단한 방법을 소개합니다.

### 3-1. diff 명령어로 원본/정제본 비교

터미널에서 아래 명령어를 실행하면 원본과 정제본의 차이를 확인할 수 있습니다.

```bash
diff data/sample_raw/hr_policy_raw.txt data/sample_clean/hr_policy_clean.txt
```

`-`로 시작하는 줄은 원본에만 있는 내용(제거된 헤더/푸터 등)이고,
`+`로 시작하는 줄은 정제본에만 있는 내용(UTF-8 주석 등)입니다.

### 3-2. 전처리 품질 체크 함수

```python
def check_preprocessing_quality(raw_text: str, clean_text: str) -> dict:
    """
    전처리 전후 텍스트를 비교하여 품질 지표를 반환합니다.

    Args:
        raw_text: 원본 텍스트
        clean_text: 전처리된 텍스트

    Returns:
        품질 지표 딕셔너리
    """
    # 페이지 번호 패턴 잔존 여부 확인
    page_num_pattern = re.compile(r"-\s*\d+\s*-")
    remaining_page_nums = page_num_pattern.findall(clean_text)

    # 3개 이상 연속 공백 잔존 여부
    excess_spaces = re.findall(r" {3,}", clean_text)

    return {
        "원본_문자수": len(raw_text),
        "정제본_문자수": len(clean_text),
        "감소율": f"{(1 - len(clean_text) / len(raw_text)) * 100:.1f}%",
        "잔존_페이지번호": remaining_page_nums,
        "잔존_과도한공백": len(excess_spaces),
        "전처리_통과": len(remaining_page_nums) == 0 and len(excess_spaces) == 0,
    }
```

---

## 4. 자주 발생하는 오류와 해결 방법

| 증상 | 원인 | 해결 방법 |
|------|------|---------|
| 한글이 깨져 보임 | EUC-KR 파일을 UTF-8로 잘못 읽음 | `normalize_encoding()` 함수 사용 |
| 조문 번호가 사라짐 | 페이지 번호 정규식이 `①②③`까지 제거 | 정규식 패턴 범위를 `\d+`로 한정 |
| 표 내용이 한 줄로 뭉침 | 셀 구분자 없이 공백만 남음 | 추출 시 ` | ` 구분자 명시 |
| 빈 문서로 추출됨 | 스캔 PDF에 텍스트 레이어 없음 | 10장 OCR 섹션 참조 |

---

## 5. 전처리 완료 체크리스트

각 문서에 대해 아래 항목을 확인한 후 6장(벡터 DB 구축)으로 진행하십시오.

- [ ] 헤더/푸터가 완전히 제거되었는가
- [ ] 인코딩이 UTF-8로 통일되었는가
- [ ] 2개 이상 연속 공백이 없는가
- [ ] 3개 이상 연속 개행이 없는가
- [ ] 표 내용이 ` | ` 구분자로 보존되어 있는가
- [ ] 이미지 전용 섹션은 `[이미지]` 플레이스홀더로 표시되었는가 (또는 10장 OCR 적용)
- [ ] `check_preprocessing_quality()` 함수 실행 결과 `전처리_통과: True`인가
