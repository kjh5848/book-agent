# Python Naming Conventions

## Naming Table
<!-- Python 네이밍 규칙 표 -->

| Target | Rule | Example |
|--------|------|---------|
| Variable / Function | `snake_case` | `load_documents`, `chunk_size` |
| Class | `PascalCase` | `DocumentLoader`, `VectorStore` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_TOKENS`, `DEFAULT_MODEL` |
| File Name | `snake_case.py` | `pdf_loader.py`, `vector_store.py` |

## Comment Rules
<!-- 코드 주석 작성 규칙 -->

- **Inline comments**: Use only for complex logic. Do not add to self-explanatory code.
- **Section separators**: Use `# --- Section Name ---` format for long code files.

```python
# --- PDF Text Extraction ---
raw_text = extract_text(pdf_path)

# --- AI Refinement ---
# Convert raw text with mixed line breaks/special characters into clean paragraphs
cleaned_text = refine_with_llm(raw_text)
```

## Docker Command Convention
<!-- Docker 명령어 표기 규칙 -->

- **`docker compose`** (V2, 하이픈 없음)를 표준으로 사용한다.
- `docker-compose` (V1, 하이픈 포함)는 사용하지 않는다.
- 모든 챕터에서 `docker compose up -d`, `docker compose down` 형태로 통일한다.

## Full Code Provision Principle
<!-- 생략 없이 전체 코드를 제공하는 원칙 -->

- When explaining code, show the **complete code without omissions**.
- Do not abbreviate with `...` or `# omitted`.
- Readers must be able to copy and run the code immediately.
