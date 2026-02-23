# Python Docstring 및 타입 힌트 규칙

## 1. Docstring 표준

모든 함수에는 역할과 인자를 설명하는 한국어 Docstring을 포함합니다.

```python
def load_pdf(file_path: str, chunk_size: int = 500) -> list[str]:
    """PDF 파일을 로드하여 텍스트 청크 리스트로 반환합니다.

    Args:
        file_path: PDF 파일의 절대 경로
        chunk_size: 각 청크의 최대 문자 수 (기본값: 500)

    Returns:
        텍스트 청크 리스트

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
    """
```

## 2. 타입 힌트

- 가능한 모든 함수에 Type Hinting을 적용합니다.
- `list`, `dict`, `tuple` 등 내장 타입을 사용합니다. (Python 3.9+)

```python
# Good
def search(query: str, top_k: int = 5) -> list[dict[str, float]]:

# Bad
def search(query, top_k=5):
```

## 3. 클래스 Docstring

```python
class DocumentLoader:
    """문서를 로드하고 청크로 분할하는 클래스입니다.

    Attributes:
        file_path: 문서 파일 경로
        chunk_size: 청크 크기
    """
```
