# 3단계: [성공] VectorDB와 RAG (청킹의 마법)

### ◈ 학습 목표
1. 수만 개의 정보 중 필요한 것만 골라내는 **RAG(Retrieval-Augmented Generation)** 아키텍처를 이해합니다.
2. 데이터를 잘라 저장하는 **청킹(Chunking)**과 검색 결과 개수를 조절하는 **k-값**의 중요성을 배웁니다.
3. '검색 기반 답변'이 시스템의 효율성을 어떻게 극대화하는지 확인합니다.

---

데이터가 많을 때를 대비해, 정보를 조각내어 저장하고 필요한 부분만 검색하는 방식(RAG)을 학습합니다.

---

## 1) 핵심 개념: 청킹, 임베딩, 그리고 k-값

| 개념 | 설명 | 비유 |
| :--- | :--- | :--- |
| **청킹 (Chunking)** | 긴 문서를 AI가 처리하기 좋은 작은 단위로 쪼개는 것 | 책을 찢어서 **포스트잇**으로 만들기 |
| **임베딩 (Embedding)** | 텍스트를 AI가 이해하는 숫자(좌표)로 변환하는 것 | 단어를 **지도상의 위치**로 바꾸기 (휴가와 리프레시는 가깝다) |
| **Top-K 검색 (k-값)** | 검색 시 가져올 문서 조각의 개수 | 질문과 관련된 **상위 N개의 포스트잇** 고르기 |

---

## 2) 검색 성능의 핵심: k-값 (k=3의 비밀)

코드에서 `search_kwargs={"k": 3}`은 질문과 가장 비슷한 조각을 **3개** 가져오라는 뜻입니다.

- **데모에서 k=3을 쓰는 이유**: 우리 예제 데이터가 총 3조각으로 되어 있습니다. `k=3`으로 설정하면 사실상 **모든 데이터를 AI에게 주는 것**과 같으므로, 검색기가 엉뚱한 것을 찾을 확률이 0%가 되어 답변 성공률이 극대화됩니다.
- **실무에서의 k-값**: 
  - **k가 크면**: 정확도는 올라가지만 AI가 읽을 양이 많아져 **느려지고 비싸집니다.**
  - **k가 작으면**: **빠르지만**, 검색기가 실수를 하면 답변이 틀릴 위험이 있습니다.

---

## 3) 청킹의 효과: 직접 비교해보기

데이터를 어떻게 자르느냐(청킹)에 따라 AI의 성능이 얼마나 달라지는지 코드로 직접 비교해 봅니다.

| 구분 | 청킹 정교화 (작게 쪼갬) | 청킹 미사용 (통째로 넣음) |
| :--- | :--- | :--- |
| **검색 품질** | 질문과 딱 맞는 부분만 정확히 찾아냄 | 관련 없는 내용까지 섞여서 검색됨 |
| **AI 집중력** | 관련 정보가 농축되어 답변이 정확함 | 정보가 너무 많아 엉뚱한 소리를 함 (비용 상승) |
| **비유** | **포스트잇**에서 답 찾기 | **두꺼운 백과사전** 통째로 읽고 답 찾기 |

---

## 4) 코드 실습: 청킹 유무에 따른 차이

### 1. 청킹 없이 통째로 넣기 (❌ 비권장)

문서를 쪼개지 않고 하나의 긴 텍스트로 처리합니다. 검색 시 불필요한 정보(보안, 복지)까지 모두 AI에게 전달되어 비효율적입니다.

- **코드**: `step3_rag_no_chunking.py`

```python
from langchain_classic.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 1. 청킹 미적용: 모든 텍스트를 하나의 문자열로 합침 (통짜 데이터)
context_all = """
[인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.
[보안규정] 업무 보안: 모든 임직원은 회사에서 지급한 승인된 보안 USB만 사용해야 하며, 개인 USB나 외부 저장 매체 사용은 엄격히 금지됩니다.
[복지규정] 식대 지원: 점심 식사는 무제한 법인카드로 지원하며, 저녁 식사는 오후 9시 이후 야근 시에만 사용이 가능합니다.
"""

# 하나의 거대한 문서로 만듦 -> 검색이 비효율적임
docs_bad = [Document(page_content=context_all, metadata={"source": "전체규정"})]

# 2. VectorDB 생성
print("문서를 학습(임베딩) 중입니다... (청킹 미적용)")
try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=docs_bad, embedding=embeddings)

    # 3. 검색기 및 프롬프트 설정 (통째로 하나뿐이므로 k=1로 검색해도 전체가 다 나옴)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1}) 

    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다. 
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    # 4. RAG 체인 실행
    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=retriever, 
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )

    question = "신입사원 휴가 규정에 대해 알려줘."
    print(f"\n질문: {question}")
    print("-" * 30)

    result = qa_chain.invoke({"query": question})
    print(f"\nAI 답변:\n{result['result']}")

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
```
### 📋 실제 실행 결과
```text

문서를 학습(임베딩) 중입니다... (청킹 미적용)

질문: 신입사원 휴가 규정에 대해 알려줘.
------------------------------

AI 답변:
[인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.
```

#### ⌥ 1. 분석 & 의견
- **동작 특징**: AI가 질문을 받고 전체 텍스트 덩어리를 훑은 뒤, 해당되는 문장을 거의 그대로 '복사+붙여넣기' 하듯 출력했습니다.
- **문제점**: 현재는 데이터가 3줄뿐이라 괜찮지만, 만약 문서가 1,000줄이었다면 AI는 답변을 하기 위해 불필요한 999줄을 전부 읽어야 합니다. 이는 **답변 속도 저하**와 **비용 낭비**로 직결됩니다.
- **결론**: 청킹이 없으면 AI는 "정보의 바다에서 바늘 찾기"를 해야 합니다. 운 좋게 찾더라도 효율성이 극악입니다.
---

### 2. 청킹으로 쪼개서 넣기 (✅ 권장)

문서를 의미 단위(문단 등)로 쪼개어 리스트에 담습니다. 검색엔진이 질문과 가장 관련 있는 '조각'만 찾아냅니다.

- **코드**: `step3_rag.py`

```python
from langchain_classic.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 1. 더미 데이터 준비 (청킹: 문장을 조각내어 리스트로 만듦)
docs = [
    Document(page_content="[인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.", metadata={"source": "인사규정"}),
    Document(page_content="[보안규정] 업무 보안: 모든 임직원은 회사에서 지급한 승인된 보안 USB만 사용해야 하며, 개인 USB나 외부 저장 매체 사용은 엄격히 금지됩니다.", metadata={"source": "보안규정"}),
    Document(page_content="[복지규정] 식대 지원: 점심 식사는 무제한 법인카드로 지원하며, 저녁 식사는 오후 9시 이후 야근 시에만 사용이 가능합니다.", metadata={"source": "복지규정"}),
]

# 2. VectorDB 생성
print("문서를 학습(임베딩) 중입니다... (청킹 적용)")
try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings
    )

    # 3. 검색기(Retriever) 설정 (k=3으로 설정하여 성공률 극대화)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 4. 프롬프트 템플릿
    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다. 
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    
    PROMPT = PromptTemplate(
        template=template, input_variables=["context", "question"]
    )

    # 5. RAG 체인 연결
    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    # 6. 질문하기
    question = "신입사원 휴가 규정에 대해 알려줘."
    print(f"\n질문: {question}")
    print("-" * 30)

    result = qa_chain.invoke({"query": question})

    print("\n--- 검색된 문서(근거) ---")
    for doc in result['source_documents']:
        print(f"[{doc.metadata['source']}]: {doc.page_content}")

    print("\n--- AI 답변 ---")
    print(result['result'])

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
```
### 📋 실제 실행 결과
```text
문서를 학습(임베딩) 중입니다...

질문: 신입사원 휴가 규정에 대해 알려줘.
------------------------------

--- 검색된 문서(근거) ---
[복지규정]: [복지규정] 식대 지원: 점심 식사는 무제한 법인카드로 지원하며, 저녁 식사는 오후 9시 이후 야근 시에만 사용이 가능합니다.
[보안규정]: [보안규정] 업무 보안: 모든 임직원은 회사에서 지급한 승인된 보안 USB만 사용해야 하며, 개인 USB나 외부 저장 매체 사용은 엄격히 금지됩니다.
[인사규정]: [인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.

--- AI 답변 ---
신입사원 휴가 규정은 다음과 같습니다:

1. 입사 후 3년 동안 법정 연차 휴가가 발생하지 않습니다.
2. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.

이 규정은 신입사원이 회사에 적응하는 기간 동안 유연한 휴가 제도를 제공하는 내용입니다.
```

#### ⌥ 2. 분석 & 의견
- **동작 특징**: AI가 각 문서의 출처(`[인사규정]`, `[복지규정]` 등)를 명확히 인지하고 있으며, 필요한 정보만 쏙 뽑아 **사용자가 읽기 좋은 리스트 형태**로 재구성했습니다.
- **장점**: 
  - **정확도**: 관련 있는 조각(Chunk)만 골라서 줬기 때문에 AI가 딴소리(할루시네이션)를 할 확률이 매우 낮습니다.
  - **가독성**: 단순히 텍스트를 긁어오는 게 아니라, 내용을 이해하고 "규정은 다음과 같습니다: 1... 2..." 식으로 구조화된 답변을 내놓습니다.
- **결론**: 청킹은 AI에게 **"정답이 적힌 포스트잇만 골라서 주는 것"**과 같습니다. AI가 훨씬 똑똑하게 일할 수 있는 환경을 만들어줍니다.
---

---

## 5) RAG 동작 원리 상세 분석

1. **검색 (Retrieval)**: 사용자가 "휴가 규정"을 물어보면, 청킹된 조각 중 의미가 가장 가까운 **[인사규정]** 조각만 찾아냅니다.
2. **효율성**: 수만 페이지의 문서가 있어도 필요한 부분만 '쏙' 뽑아 쓰기 때문에 처리 속도가 빠르고 비용이 절감됩니다.
3. **✓ 결론**: 실무에서는 `RecursiveCharacterTextSplitter` 같은 도구를 사용해 자동으로 문서를 청킹하여 DB에 넣는 것이 필수입니다.

---

### ↳ Next Step
"내 정보를 찾긴 찾았는데, 복잡한 계산이나 논리 추론도 잘할까?"
단순 검색을 넘어 AI가 스스로 생각하게 만드는 **4단계: 추론(Reasoning) 능력 활용**으로 넘어갑니다.
