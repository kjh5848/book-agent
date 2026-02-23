# Python 네이밍 규칙

## 네이밍 테이블

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수 / 함수 | `snake_case` | `load_documents`, `chunk_size` |
| 클래스 | `PascalCase` | `DocumentLoader`, `VectorStore` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_TOKENS`, `DEFAULT_MODEL` |
| 파일명 | `snake_case.py` | `pdf_loader.py`, `vector_store.py` |

## 주석 규칙

- **인라인 주석**: 복잡한 로직에만 사용합니다. 자명한 코드에는 달지 않습니다.
- **섹션 구분**: 긴 코드는 `# --- 섹션명 ---` 형식으로 구분합니다.

```python
# --- PDF 텍스트 추출 ---
raw_text = extract_text(pdf_path)

# --- AI 정제 ---
# 줄바꿈/특수문자가 섞인 원본을 정리된 문단으로 변환
cleaned_text = refine_with_llm(raw_text)
```

## 코드 전체 제공 원칙

- 코드를 설명할 때는 **생략 없이 전체 코드** 를 보여줍니다.
- `...` 이나 `# 생략` 으로 축약하지 않습니다.
- 독자가 복사/붙여넣기로 바로 실행할 수 있어야 합니다.
