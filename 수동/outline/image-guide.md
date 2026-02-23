# 이미지 생성 가이드 — AI 업무 비서 구축 (RAG + MCP)

> 이 파일은 이 책 전용 Gemini 이미지 아이콘 사전이다.
> 범용 규칙(플레이스홀더 문법, 베이스 스타일)은 `.claude/skills/visual/references/image.md`를 참조한다.

---

## 1. 이 책 전용 아이콘 사전

집필 에이전트는 Gemini 프롬프트 작성 시 아래 키워드를 일관되게 사용한다.

| 대상 | Gemini 프롬프트 키워드 | 레이블 |
|------|----------------------|--------|
| 사용자 | `minimalist line-art person icon` | `'User'` |
| AI 에이전트 / LLM | `minimalist line-art brain icon` | `'AI'` |
| 벡터 DB (RAG) | `minimalist line-art stack of papers icon` | `'RAG (DOC)'` |
| 관계형 DB (MCP) | `minimalist line-art cylinder database icon` | `'MCP (DB)'` |
| API 서버 | `minimalist line-art server rack icon` | `'API Server'` |
| Ollama (로컬 LLM) | `minimalist line-art laptop icon` | `'Ollama'` |

---

## 2. 이 책 전용 화살표·흐름 정의

| 흐름 | 화살표 스타일 | 레이블 |
|------|-------------|--------|
| 사용자 질문 | 얇은 수평 화살표 → | `"Query"` |
| 벡터 검색 | 얇은 수평 화살표 ← → | `"Search"` |
| 문서 조각 반환 | 점선 화살표 ← | `"Chunks"` |
| LLM 최종 답변 | 굵은 수평 화살표 → | `"Answer"` |
| DB 조회 | 얇은 수직 화살표 ↓ | `"Query"` |
| DB 결과 | 얇은 수직 화살표 ↑ | `"Result"` |

---

## 3. Gemini 프롬프트 작성 예시

아래 예시를 템플릿으로 활용한다.

```
A minimalist black and white technical diagram with a strict 16:9 aspect ratio
on a solid white background. No shading, no 3D effects, only clean thin line art.
The entire assembly is perfectly centered within the 16:9 frame, leaving generous margins.

Show left-to-right flow:
minimalist line-art person icon labeled 'User'
→ thin horizontal arrow labeled "Query"
→ minimalist line-art brain icon labeled 'AI'
→ thin horizontal arrow labeled "Search"
→ minimalist line-art stack of papers icon labeled 'RAG (DOC)'
← dashed arrow labeled "Chunks" back to AI
→ thick horizontal arrow labeled "Answer" exits right.
```
