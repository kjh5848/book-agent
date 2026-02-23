# IPO(Input/Process/Output) 패턴

## 1. 본문 코드 워크플로우 섹션

코드 블록 바로 아래에 반드시 배치합니다.

```markdown
#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 함수나 클래스로 들어오는 데이터
2. **처리(Process)**: 핵심 로직 1~2줄 요약
3. **출력(Output)**: 반환값 또는 생성되는 파일
```

## 2. 소스 코드 내 구간 주석

실제 소스 코드 파일에도 IPO 구간을 주석으로 표시합니다.

```python
def process_document(file_path: str) -> list[str]:
    """문서를 처리하여 청크 리스트를 반환합니다."""

    # --- Input ---
    raw_text = load_file(file_path)

    # --- Process ---
    cleaned_text = clean_text(raw_text)
    chunks = split_into_chunks(cleaned_text, chunk_size=500)

    # --- Output ---
    return chunks
```

## 3. 규칙

- 코드 블록 아래 코드 워크플로우가 없으면 품질 체크에서 FAIL 처리됩니다.
- 입력/처리/출력은 각각 1~2문장으로 간결하게 작성합니다.
- 복잡한 함수는 처리(Process)를 여러 단계로 나눌 수 있습니다.
