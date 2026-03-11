# Planning Review Loop and LLM Design Principles

## Planning Review Loop (Phase 1 Mandatory Protocol)
<!-- plan.md 초안 완성 후 반드시 따라야 하는 절차 -->

After completing the plan.md draft, the following procedure **must** be followed.
Proceeding to Phase 2 (code generation) without explicit user approval is prohibited.

### Required Content in Approval Request
<!-- 승인 요청 시 반드시 포함해야 할 내용 -->

1. **Chapter composition summary table** (chapter name + estimated volume)
2. **3 feedback questions**:
   - Is the difficulty target and technology stack appropriate?
   - Is the chapter order and learning flow natural?
   - Are there any topics to add or exclude?
3. **[Planning Enhancement Proposal]** — propose missing items based on the latest trends (must not be omitted even if the draft is sufficient)

### [Planning Enhancement Proposal] Format
<!-- 기획 고도화 제안 형식 -->

```
## 💡 [Planning Enhancement Proposal]
| Proposed Item | Specific Reason | Estimated Additional Volume |
|--------------|-----------------|----------------------------|
| {item}       | {reader problem or practical value} | ~{N}p |
```

### Loop Operation Rules
<!-- 루프 동작 규칙 -->

- On revision request → immediately update plan.md → request re-approval
- Repeat until explicit approval ("Approved" or "Pass") is given

---

## LLM Provider Design Principles
<!-- 특정 LLM에 종속되지 않는 설계 원칙 -->

Planning and code that is tied to a specific LLM is prohibited.
Specify the Provider to be used in the project outline and design so that switching is possible via `.env`.

| Provider Type | Environment Variable Pattern |
|---------------|------------------------------|
| Local (Ollama) | `LLM_PROVIDER=ollama`, `OLLAMA_MODEL=` |
| Cloud | `LLM_PROVIDER=openai`, `OPENAI_API_KEY=` |
| Self-hosted (vLLM) | `LLM_PROVIDER=vllm`, `VLLM_BASE_URL=` |

Follow the LLM configuration section in the project outline as the primary reference.
