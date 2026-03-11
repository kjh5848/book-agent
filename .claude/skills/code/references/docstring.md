# Python Docstring and Type Hint Rules

## 1. Docstring Standard
<!-- 모든 함수에 역할과 인자를 설명하는 Docstring 포함 규칙 -->

All functions must include a Docstring that describes the role and arguments.

```python
def load_pdf(file_path: str, chunk_size: int = 500) -> list[str]:
    """Loads a PDF file and returns a list of text chunks.

    Args:
        file_path: Absolute path to the PDF file
        chunk_size: Maximum number of characters per chunk (default: 500)

    Returns:
        List of text chunks

    Raises:
        FileNotFoundError: If the file does not exist
    """
```

## 2. Type Hints
<!-- 모든 함수에 타입 힌트 적용 규칙 -->

- Apply Type Hinting to all functions where possible.
- Use built-in types such as `list`, `dict`, `tuple`. (Python 3.9+)

```python
# Good
def search(query: str, top_k: int = 5) -> list[dict[str, float]]:

# Bad
def search(query, top_k=5):
```

## 3. Class Docstring
<!-- 클래스 Docstring 형식 -->

```python
class DocumentLoader:
    """A class that loads documents and splits them into chunks.

    Attributes:
        file_path: Path to the document file
        chunk_size: Chunk size
    """
```
