# [학습 가이드] DeepSeek-R1: 실패에서 성공까지 RAG 단계별 정복

이 문서는 복잡한 기능을 배제하고, **"LLM은 왜 내 데이터를 모를까?"**라는 문제에서 시작해 RAG로 이를 해결하는 과정을 단계별 코드로 학습합니다.

---

## 📂 프로젝트 구조 (Project Structure)

현재 프로젝트는 학습 단계에 따라 다음과 같이 구성되어 있습니다.

### 01. Basic RAG (기초 개념)
RAG의 핵심 원리인 검색(Search), 컨텍스트(Context), 추론(Reasoning)을 배우는 입문 과정입니다.
- **가이드**: `01_basic_rag/tutorial_step1_fail.md` ~ `tutorial_step5_finish.md`
- **코드**: `01_basic_rag/step1_fail.py` ~ `step4_rag.py`
- **심화**: `01_basic_rag/청킹심화.md`

---

## 0. 사전 준비 (인프라 세팅)
로컬 환경(내 PC)에서 인터넷 없이 동작하는 환경을 만듭니다.

### 0.1 Ollama 및 모델 설치
- **Ollama 다운로드**: [ollama.com](https://ollama.com)
- **모델 다운로드 (터미널 실행)**:
  - 생성 모델 (DeepSeek-R1): 추론 능력이 뛰어난 모델
    ```bash
    ollama pull deepseek-r1:8b
    ```
  - 임베딩 모델 (Nomic): 한글/영어 텍스트를 숫자로 바꿔주는 모델
    ```bash
    ollama pull nomic-embed-text
    ```

### 0.3 라이브러리별 역할 (설치 및 용도)

#### 💡 한 줄 설치 명령어 (터미널용)
```bash
pip install langchain langchain-community langchain-ollama langchain-chroma langchain-classic
```

| 라이브러리 | 설치 명령어 (`pip`) | 역할 | 비유 |
| :--- | :--- | :--- | :--- |
| **`langchain`** | `pip install langchain` | AI 앱을 만들기 위한 핵심 뼈대 | **공장 전체 시스템** |
| **`langchain-community`** | `pip install langchain-community` | 문서 읽기, 도구 사용 등 커뮤니티 부품 모음 | **다양한 소형 부품** |
| **`langchain-ollama`** | `pip install langchain-ollama` | 내 PC의 Ollama AI 모델과 연결 | **AI와 대화하는 전화선** |
| **`langchain-chroma`** | `pip install langchain-chroma` | 데이터를 저장하고 검색하는 벡터 데이터베이스 | **똑똑한 도서관 보관함** |
| **`langchain-classic`** | `pip install langchain-classic` | 구버전 코드와 신버전 구조를 연결해주는 호환 라이브러리 | **레거시 커넥터** |
| **`langchain-core`** | `(langchain 설치 시 동시 설치)` | 인터페이스와 기본 데이터 구조 정의 | **표준 규격서** |

---

## 1단계: [실패] LLM에게 그냥 물어보기
가장 먼저, 학습되지 않은 사내 비공개 정보를 물어봤을 때 어떤 문제가 생기는지 확인합니다.

- **코드**: `01_basic_rag/step1_fail.py`
- **가이드**: `01_basic_rag/tutorial_step1_fail.md`
```python
from langchain_ollama import ChatOllama

# 로컬 LLM 연결
llm = ChatOllama(model="deepseek-r1:8b", temperature=0)

# 질문: 모델이 학습했을 리 없는 가상의 회사 규정
question = "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?"

print(f"질문: {question}\n")
response = llm.invoke(question)
print(f"답변:\n{response.content}")
```

### ✅ 결과 분석
LLM은 내부 규정을 모르기 때문에 **"일반적인 근로기준법"**을 말하거나 **"인사팀에 문의하라"**는 원론적인 답변만 내놓습니다. (지식의 부재)

---

## 2단계: [반쪽 성공] 프롬프트에 텍스트 주입 (Context Injection)
문서가 짧을 때 가장 확실한 방법입니다. 정보를 직접 전달합니다.

- **코드**: `01_basic_rag/step2_context.py`
- **가이드**: `01_basic_rag/tutorial_step2_context.md`
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="deepseek-r1:8b", temperature=0)

# 1. 정보를 변수에 담습니다
context_data = """
[테크컴퍼니 취업규칙]
1. 신입사원은 입사 후 3년 동안은 연차가 없다. 
2. 대신 매월 1회 '리프레시 데이'를 유급으로 제공한다.
"""

# 2. 프롬프트에 정보를 포함시킵니다.
question = "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?"
prompt = f"""
아래 [참고 정보]를 보고 질문에 답해줘.
[참고 정보]
{context_data}

질문: {question}
"""

response = llm.invoke(prompt)
print(f"답변:\n{response.content}")
```

### ✅ 결과 분석
AI가 정확하게 답변합니다. 하지만 문서가 수천 페이지라면 **컨텍스트 창(Context Window)** 용량 초과와 비용 문제로 이 방식은 불가능해집니다.

---

## 3단계: [성공] VectorDB와 RAG (청킹의 마법)
데이터가 많을 때를 대비해, 정보를 조각내어 저장하고 필요한 부분만 검색하는 방식을 학습합니다.

> **심화 학습**: 청킹(Chunking) 유무에 따른 성능 차이가 궁금하다면 별도의 심화 가이드 문서인 `01_basic_rag/청킹심화.md`를 참고하세요.

### 코드: `01_basic_rag/step3_rag.py`
**가이드**: `01_basic_rag/tutorial_step3_rag.md`
문서를 의미 있는 조각(Chunk)으로 나누어 저장하고, 질문에 맞는 조각만 찾아 AI에게 전달합니다.

```python
from langchain_classic.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 1. 학습 데이터 준비 (청킹: 문장을 조각내어 리스트로 만듦)
docs = [
    Document(page_content="[인사규정] 신입사원은 입사 후 처음 3년 동안은 연차가 없습니다. 대신 매월 1회 '리프레시 데이'를 사용합니다.", metadata={"source": "인사규정"}),
    Document(page_content="[보안규정] 모든 직원은 사내에서 승인된 보안 USB만 사용해야 합니다.", metadata={"source": "보안규정"}),
    Document(page_content="[복지규정] 점심 식대는 무제한 법인카드를 지원합니다.", metadata={"source": "복지규정"}),
]

# 2. VectorDB 생성 (임베딩 모델: nomic-embed-text)
print("문서를 학습(임베딩) 중입니다...")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)

### 💡 핵심 개념: 임베딩과 시맨틱 검색
# - 임베딩: 글자를 숫자의 집합(좌표)으로 바꾸는 기술
# - 시맨틱 검색: "휴가"라고 물어도 "리프레시 데이"를 찾아냄

# 3. 검색기 및 프롬프트 설정 (할루시네이션 방지 안전장치)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다. 
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

[주의사항]
- 참고 정보에 답변에 필요한 내용이 없다면 "죄송합니다. 해당 규정에 대한 정보를 찾을 수 없습니다."라고 답하세요.
- 스스로 지어내지 마세요.

참고 정보: {context}

질문: {question}
답변:"""
PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

# 4. 실행
llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    retriever=retriever, 
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

question = "신입사원 휴가 규정 알려줘."
result = qa_chain.invoke({"query": question})
print(f"\nAI 답변:\n{result['result']}")
```

---

## 4단계: [심화] DeepSeek-R1의 추론 능력 활용하기
단순 검색을 넘어, AI가 규정을 이해하고 논리적으로 **추론(Reasoning)**하여 복잡한 질문에 답하는지 확인합니다.

- **코드**: `01_basic_rag/step4_rag.py`
- **가이드**: `01_basic_rag/tutorial_step4_reasoning.md`
```python
# 질문: 단순 검색이 아닌 계산과 논리가 필요한 질문
question = "입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘."
```

### 📋 실제 실행 결과
```text
질문: 입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘.
------------------------------
문서를 학습(임베딩) 중입니다...

--- 검색된 문서(근거) ---
[인사규정]: [인사규정] 신입사원 휴가 및 연차: 신입사원은 입사 후 처음 3년 동안은 법정 연차가 발생하지 않습니다. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.

--- AI 답변 ---
입사 6개월차 신입사원으로서 총 6개월 동안 매월 1회씩 리프레시 데이를 사용할 수 있습니다.  
이미 2회 사용했으므로, 남은 리프레시 데이는 **6 - 2 = 4회**입니다.  

**참고**: 신입사원은 입사 후 3년 동안 매월 1회씩 리프레시 데이를 사용할 수 있습니다.
```

---

## 5단계: [결론] RAG 학습 요약 및 프로젝트 응용

지금까지 1단계부터 4단계까지 LLM의 한계를 RAG로 극복하는 과정을 학습했습니다.

### 📍 요약: RAG 시스템의 핵심 3요소

| 단계 | 기술 | 비유 | 역할 |
| :--- | :--- | :--- | :--- |
| **Search** | **Vector DB** | 똑똑한 도서관 사서 | 방대한 데이터 중 가장 관련 있는 정보만 빠르게 찾기 |
| **Context** | **Prompt** | 참고 자료 전달 | 찾은 정보를 AI에게 "이것만 보고 답해"라고 전달하기 |
| **Reasoning** | **DeepSeek-R1** | 사려 깊은 전문가 | 전달받은 정보를 바탕으로 논리적으로 생각해서 답변하기 |

### 🚀 다음 단계: 실전으로 가는 길
1. **영구 저장 (Persistence)**: 현재는 실행할 때마다 DB를 새로 만듭니다. `Chroma(persist_directory="./db")` 설정을 통해 하드디스크에 저장하고 불러오는 법을 익히세요.
2. **파일 업로드 기능**: 현재는 코드에 텍스트를 직접 넣었지만, `PyPDFLoader`를 사용해 PDF/Excel/Word 파일을 읽도록 확장할 수 있습니다.
3. **UI 연결**: Streamlit이나 Gradio를 사용해 웹 화면을 만들면 진정한 '사내 챗봇'이 완성됩니다.
4. **지속적 학습**: 데이터가 변경되면 Vector DB에 새 데이터만 임베딩하여 업데이트하면 됩니다.

**수고하셨습니다! 이제 당신만의 커스텀 RAG AI를 만들 준비가 되었습니다.**