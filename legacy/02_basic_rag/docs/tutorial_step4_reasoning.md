# 4단계: [심화] AI의 추론(Reasoning) 능력이 필요한 이유

### ◈ 학습 목표
1. 단순 검색을 넘어 검색된 정보를 바탕으로 논리적으로 생각하는 **추론(Thinking)**의 과정을 이해합니다.
2. DeepSeek-R1과 같은 추론 모델이 복잡한 상황(계산, 인과관계 파악)을 어떻게 풀어내는지 확인합니다.
3. 실전 비즈니스 환경에서 추론 모델이 필수적인 이유를 파악합니다.

---

단순히 검색(Search)해서 보여주는 것을 넘어, AI가 규정을 이해하고 논리적으로 **추론(Reasoning/Thinking)**하여 복잡한 질문에 답하는 능력이 왜 필요한지 학습합니다.

---

## 1) RAG에서 '추론(Reasoning)'이 왜 중요한가요?

RAG는 흔히 **"검색해서(Retrieval) 답변하기(Generation)"**라고 합니다. 하지만 현실의 질문은 단순히 문서의 한 문장을 찾는 것으로 끝나지 않습니다.

- **기존 RAG의 한계**: 문서에 "A는 B다"라고 적혀 있으면 답변을 잘 하지만, "A가 B이고 C가 D라면, 지금 내 상황에서 E는 뭐야?"라는 식의 **복잡한 논리**나 **수학적 계산**이 들어가면 엉뚱한 답을 내놓기 쉽습니다.
- **추론의 역할**: AI가 검색된 문서들을 보고 **"생각하는 시간"**을 갖는 것입니다. 문서들 사이의 연결 고리를 찾고, 사용자의 구체적인 숫자를 계산하여 최종적인 '진짜 정답'을 도출합니다.

---

## 2) 시나리오: 단순 검색으로 풀 수 없는 논리 질문

- **사용자 상황**: "나 입사한 지 6개월 됐는데, 지금까지 쓴 리프레시 데이가 2번이야. 나 남은 리프레시 데이 몇 개야?"
- **AI가 수행해야 할 'Thinking' 과정**:
  1. **검색**: "내부 규정에서 리프레시 데이 관련 문장을 찾자." -> (결과: 매월 1회 제공 확인)
  2. **분석**: "사용자는 입사 6개월차구나. 그럼 총 발생한 휴가는 6개겠네."
  3. **계산**: "사용한 게 2개라고 했으니, 6개 - 2개 = 4개가 남았군."
  4. **최종 답변**: "남은 휴가는 4개입니다."

---

## 3) 전체 코드: `step4_reasoning.py`

학습 가이드의 일관성을 위해 3단계와 동일한 구조의 전체 코드를 사용합니다.

```python
from langchain_classic.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 1. 데이터 준비 (3단계와 동일)
docs = [
    Document(page_content="[인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.", metadata={"source": "인사규정"}),
    Document(page_content="[보안규정] 업무 보안: 모든 임직원은 회사에서 지급한 승인된 보안 USB만 사용해야 하며, 개인 USB나 외부 저장 매체 사용은 엄격히 금지됩니다.", metadata={"source": "보안규정"}),
    Document(page_content="[복지규정] 식대 지원: 점심 식사는 무제한 법인카드로 지원하며, 저녁 식사는 오후 9시 이후 야근 시에만 사용이 가능합니다.", metadata={"source": "복지규정"}),
]

# 2. VectorDB 생성
print("문서를 학습(임베딩) 중입니다...")
try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)

    # 3. 검색기(Retriever) 설정 (k=3으로 전체를 참고하도록 설정)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 4. 프롬프트 템플릿
    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다. 
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    
    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    # 5. RAG 체인 연결 (추론 모델 사용)
    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    # 6. 추론이 필요한 복잡한 질문 던지기
    question = "입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘."
    print(f"\n질문: {question}")
    print("-" * 30)

    result = qa_chain.invoke({"query": question})

    print("\n--- AI 답변 ---")
    print(result['result'])

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
```

---

## 4) 실제 실행 결과 결과

```text
질문: 입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘.
------------------------------
문서를 학습(임베딩) 중입니다...

--- AI 답변 ---
입사 6개월차 신입사원으로서 총 6개월 동안 매월 1회씩 리프레시 데이를 사용할 수 있습니다.  
이미 2회 사용했으므로, 남은 리프레시 데이는 **6 - 2 = 4회**입니다.  

**참고**: 신입사원은 입사 후 3년 동안 매월 1회씩 리프레시 데이를 사용할 수 있습니다.
```

---

## 5) 왜 '추론 모델(Reasoning Model)'인가요?

실험에 사용된 **DeepSeek-R1**이나 OpenAI의 **o1**과 같은 모델들을 흔히 '추론 모델' 또는 **'Thinking Model'**이라고 부릅니다. 이들은 기존 LLM과 무엇이 다를까요?

1.  **생각의 사슬 (Chain of Thought)**: 답을 내놓기 전, 스스로 문제를 단계별로 쪼개어 생각하는 과정을 거칩니다. (예: 6개월 발생 -> 2개 사용 -> 뺄셈 수행)
2.  **복합 문맥 이해**: 단순히 문서를 요약하는 것이 아니라, 문서에 없는 '사용자의 현재 상황(6개월차)'을 문서의 '일반 규칙(매월 1회)'에 대입하는 지능을 보여줍니다.
3.  **수학적/논리적 정확도**: 일반 모델이 언어적 패턴으로 답변을 생성한다면, 추론 모델은 논리적 인과관계를 따지기 때문에 산술 연산에서도 훨씬 높은 정확도를 보입니다.

**✓ 결론**: 진정한 사내 AI 비서를 만들고 싶다면, 단순히 정보를 찾는 RAG를 넘어 **찾은 정보를 똑똑하게 요약하고 계산할 수 있는 추론 모델**을 결합하는 것이 필수적입니다.

---

### ↳ Next Step
"이제 완벽한 이론과 코드를 갖췄습니다!"
마지막으로 지금까지 배운 내용을 총정리하고 실전 서비스로 나아가기 위한 로드맵을 확인하는 **5단계: 피니쉬(Finish)**로 여정을 마무리합니다.
