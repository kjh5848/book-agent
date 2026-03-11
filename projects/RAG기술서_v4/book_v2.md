# 1단계: 이 책의 목표와 최종 완성본 미리보기

### ◈ 학습 목표
1. 이 책이 만드는 **"커넥트HR AI 비서"** 의 전체 모습을 미리 확인합니다.
2. **RAG(Retrieval-Augmented Generation)** 와 **MCP(Model Context Protocol)** 가 왜 필요한지 이해합니다.
3. 10개 챕터가 어떤 순서로 연결되는지 파악합니다.

---

## 1) 이 책이 다루는 범위

30명 규모의 중소기업에서 사내 문서가 3,000건 이상 쌓여 있고, 직원들은 매일 평균 30분을 문서 검색에 소비합니다. "김 대리 연차 며칠 남았어요?", "신입사원 온보딩 절차가 어떻게 되죠?" 같은 질문이 인사팀에 하루 20건 이상 들어옵니다.

이 문제를 해결하기 위해 처음 떠올리는 방법은 LLM을 사내 데이터로 **파인튜닝(Fine-tuning)** 하는 것입니다. 그런데 이 방법에는 현실적인 장벽이 있습니다.

### Fine-tuning vs RAG 비교

| 항목 | Fine-tuning | RAG |
|------|-------------|-----|
| 데이터 요구량 | 수천~수만 건 정제 데이터 | 원본 문서 그대로 사용 |
| 초기 비용 | 높음 (GPU 학습 비용) | 낮음 (임베딩 비용만) |
| 업데이트 주기 | 재학습 필요 (일~주 단위) | 문서 추가 즉시 반영 |
| 적합 상황 | 특정 도메인 언어 스타일 학습 | 최신 문서 기반 정확한 답변 |

**RAG** 는 LLM에게 "직접 외우게" 하는 대신 "필요할 때 검색해서 답하게" 하는 기법입니다. 취업 규칙이 개정되어도 파일 하나를 교체하면 됩니다.

그런데 직원들의 질문 중 일부는 문서가 아니라 DB에 있는 정형 데이터를 필요로 합니다. "김철수 사원의 남은 연차는?"이라는 질문은 HR 정책 문서가 아니라 DB 테이블에서 꺼내야 합니다. 이 정형 데이터 조회를 처리하는 표준 방법이 **MCP** 입니다.

---

## 2) 최종 결과물 데모 시나리오

완성된 커넥트HR AI 비서가 처리하는 세 가지 질문 유형입니다.

### 정형 질문 — DB 직접 조회
```
질문: "김철수 사원의 남은 연차는 며칠인가요?"
답변: 김철수 사원의 현재 연차 잔여일은 7일입니다.
출처: PostgreSQL — leave_balance 테이블 (실시간 조회)
```

### 비정형 질문 — 문서 검색
```
질문: "신입사원 온보딩 절차를 알려주세요."
답변: 신입사원 온보딩은 다음 절차로 진행됩니다.
      1. 입사 첫날: 사원증 발급 및 PC 셋업
      2. 1주차: 부서 오리엔테이션 및 업무 시스템 교육
출처: HR_취업규칙_v1.0.pdf, 23페이지
```

### 복합 질문 — DB + 문서 조합
```
질문: "올해 매출 상위 부서의 복지 정책을 비교해 주세요."
답변: 올해 상반기 매출 1위는 영업팀(2.3억), 2위는 개발팀(1.8억)입니다.
      영업팀 복지: 분기별 성과 인센티브, 유연 근무 허용
      개발팀 복지: 교육비 지원 연 200만 원, 재택 근무 주 2회
출처: PostgreSQL — sales 테이블 + OPS_신규서비스_런칭전략.pdf 15페이지
```

---

## 3) 아키텍처 한 장 요약

| 구성 요소 | 역할 |
|-----------|------|
| **FastAPI 서버** | 사용자 요청을 받아 라우터로 전달하고 최종 응답을 반환 |
| **QueryRouter** | 질문 유형(정형/비정형/복합)을 판단하여 적절한 처리 경로로 분기 |
| **MCP Tools** | PostgreSQL에 SQL을 실행하여 정형 데이터를 조회 |
| **RAG Chain** | ChromaDB에서 관련 문서 청크를 검색하고 LLM에 주입하여 답변 생성 |
| **ReAct Agent** | 복합 질문을 단계별로 분해하여 MCP와 RAG를 조합 |
| **ChromaDB** | 문서 임베딩 벡터를 저장하고 의미 기반 유사도 검색 수행 |
| **PostgreSQL** | 직원, 휴가, 매출 등 정형 데이터 저장 |

---

## 4) 사용 기술 스택

| 영역 | 기술 | 역할 |
|------|------|------|
| 텍스트 LLM | Ollama + DeepSeek R1 8b | 질의응답 추론 |
| Tool Calling LLM | Ollama + Llama 3.1 8b | 에이전트 도구 호출 |
| 백엔드 | FastAPI | REST API 웹 서버 |
| 정형 DB | PostgreSQL 16+ | 직원·휴가·매출 데이터 |
| 벡터 DB | ChromaDB | 문서 임베딩 저장·검색 |
| 오케스트레이션 | LangChain 0.3+ | RAG 체인 + 에이전트 |
| 임베딩 | ko-sroberta-multitask | 한국어 텍스트 벡터화 |

### 최소 및 권장 하드웨어 스펙

| 항목 | 최소 사양 | 권장 사양 |
|------|---------|---------|
| RAM | 16GB | 32GB |
| 저장공간 | 20GB 여유 | 50GB 여유 |
| OS | macOS 13+ / Ubuntu 22.04+ / Windows WSL2 | macOS (Apple Silicon) |
| GPU | 불필요 (CPU 추론 가능) | NVIDIA GPU 또는 Apple Silicon |

> 💡 **팁**: 이 책의 모든 코드는 `.env` 파일의 `LLM_PROVIDER` 값 하나로 Ollama(로컬 무료), OpenAI(클라우드 유료) 사이에서 전환됩니다.

---

## 5) 챕터별 빌드업 로드맵

| 챕터 | 해결하는 문제 | 산출물 |
|------|------------|--------|
| CH01 | 무엇을 만들지 몰라 막막함 | 전체 아키텍처 이해 |
| CH02 | 개발 환경이 없음 | 검증된 로컬 LLM 환경 |
| CH03 | LLM이 왜 틀리는지 모름 | RAG 필요성 체감 |
| CH04 | 사내 데이터를 담을 시스템 없음 | FastAPI + DB 기반 사내 시스템 |
| CH05 | 문서가 뒤섞여 있어 품질 보장 불가 | 표준화된 문서 세트 |
| CH06 | 문서를 AI가 검색할 수 없음 | ChromaDB 인덱스 + CLI 검증 |
| CH07 | 개발자만 검색 가능, 전 직원 사용 불가 | 웹 채팅 UI + 멀티턴 대화 |
| CH08 | RAG만으로 정형 데이터 질문 처리 불가 | 통합 에이전트 |
| CH09 | 운영 중 타임아웃·에러 관리 불가 | 운영 설정 완비된 연결 구조 |
| CH10 | "가끔 틀리는" 문제를 개선할 방법 모름 | 튜닝 프레임워크 + 품질 측정 |

---

### ↳ Next Step
"이제 전체 그림을 파악했습니다!"
다음은 실제로 코드를 작성할 개발 환경을 준비하는 **2단계: 개발 환경 설정**으로 넘어갑니다.


---

# 2단계: 개발 환경 설정

### ◈ 학습 목표
1. **Ollama** 와 **DeepSeek R1** 을 로컬 머신에 설치하고 대화를 테스트합니다.
2. **Docker** 로 PostgreSQL을 실행하고 시드 데이터를 확인합니다.
3. **Python 가상환경** 을 구성하고 환경 검증 스크립트로 4/4 PASS를 달성합니다.

---

## 1) 필수 요구사항 확인

### 하드웨어 최소 요건

| 항목 | 최소 요건 | 권장 사양 |
|------|----------|---------|
| RAM | 16GB | 32GB |
| 저장 공간 | 20GB 여유 | 50GB 이상 |
| CPU | 4코어 이상 | 8코어 이상 |

### 사전 체크리스트

- [ ] Python 3.11 또는 3.12 설치 (`python3 --version` 으로 확인)
- [ ] Docker Desktop 설치 및 실행 (`docker --version` 으로 확인)
- [ ] RAM 16GB 이상
- [ ] Git 설치 (`git --version` 으로 확인)

---

## 2) Ollama + DeepSeek R1 설치

**Ollama** 는 로컬 머신에서 오픈소스 LLM을 실행할 수 있는 경량 런타임입니다.

### 설치 (macOS)
```bash
brew install ollama
ollama serve
```

### 모델 다운로드
```bash
# 메인 LLM (약 4.7GB, 10~60분 소요)
ollama pull deepseek-r1:8b

# 임베딩 모델
ollama pull nomic-embed-text
```

> ⚠️ RAM이 16GB 미만이라면 경량 모델 `deepseek-r1:1.5b` 을 사용하세요.

### 대화 테스트
```bash
ollama run deepseek-r1:8b
```
```
>>> 안녕하세요. 한 문장으로 자기소개를 해 주십시오.
```
모델이 응답하면 정상입니다. `/bye` 로 종료합니다.

---

## 3) Python 가상환경 설정

```bash
# Python 버전 확인 (3.11 또는 3.12 필요)
python3 --version

# 가상환경 생성
python3.12 -m venv .venv

# 활성화 (macOS / Linux)
source .venv/bin/activate

# 활성화 (Windows PowerShell)
# .\.venv\Scripts\Activate.ps1
```

활성화 성공 시 프롬프트 앞에 `(.venv)` 가 표시됩니다.

> 💡 **트러블슈팅**: Python 3.13 이상에서 `pg_config executable not found` 오류가 나면 Python 3.12로 가상환경을 다시 생성하세요.

---

## 4) PostgreSQL 설치 (Docker)

```bash
cd examples/CH02_개발_환경_설정
cp .env.example .env
docker compose up -d
```

`.env` 파일 내용:
```ini
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=connect_hr
POSTGRES_USER=connect_hr
POSTGRES_PASSWORD=connect_hr_pass
```

---

## 5) 환경 검증 실행

```bash
pip install -r requirements.txt
python src/verify_env.py
```

### 📋 실제 실행 결과
```text
[1/4] Python 버전 확인... ✅ PASS (Python 3.12.4)
[2/4] Ollama 연결 확인... ✅ PASS (deepseek-r1:8b 응답 정상)
[3/4] PostgreSQL 연결 확인... ✅ PASS (connect_hr DB 접속 성공)
[4/4] 임베딩 모델 확인... ✅ PASS (nomic-embed-text 로드 완료)

✅ 환경 검증 완료: 4/4 PASS
```

---

## 6) 결과 분석

1. **Ollama**: 로컬에서 LLM을 무료로 실행합니다. 사내 데이터를 외부 서버로 보내지 않으므로 보안 정책을 충족합니다.
2. **Docker PostgreSQL**: OS에 관계없이 동일한 환경을 보장합니다. `docker compose up -d` 한 줄이면 DB + 시드 데이터가 자동으로 준비됩니다.
3. **가상환경**: 프로젝트별 독립된 Python 패키지 공간을 만들어 의존성 충돌을 방지합니다.

---

### ↳ Next Step
"개발 환경 준비 완료!"
이제 LLM이 실제로 어떤 한계를 가지는지 직접 체험하고, 그 한계를 극복하는 **3단계: LLM의 한계와 RAG의 필요성**으로 넘어갑니다.


---

# 3단계: [실패 → 성공] LLM의 한계와 RAG의 필요성

### ◈ 학습 목표
1. LLM이 학습하지 않은 사내 정보에 대해 어떻게 답변하는지 확인합니다.
2. **할루시네이션(Hallucination)** 현상을 직접 목격하고 그 위험성을 이해합니다.
3. **컨텍스트 주입(Context Injection)** 과 **RAG** 를 비교하여 각각의 한계와 장점을 파악합니다.

---

가장 먼저, 학습되지 않은 사내 비공개 정보를 물어봤을 때 어떤 문제가 생기는지 확인합니다.

---

## Step 1: [실패] LLM에게 그냥 물어보기

### 실습 준비
```bash
cd examples/CH03_LLM의_한계와_RAG의_필요성
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

| 패키지 | 역할 |
|-------|------|
| `langchain` | LLM 애플리케이션 프레임워크 |
| `langchain-ollama` | Ollama LLM/임베딩 연결 |
| `langchain-chroma` | ChromaDB 벡터스토어 연동 |
| `langchain-classic` | RetrievalQA 체인 제공 |
| `chromadb` | 벡터 데이터베이스 |

### 코드: `step1_fail.py`

```python
from langchain_ollama import ChatOllama

# 로컬 LLM 연결
llm = ChatOllama(model="deepseek-r1:8b", temperature=0)

# 질문: 모델이 학습했을 리 없는 가상의 회사 규정
question = "우리 회사(커넥트)의 신입사원 연차 발생 규정이 어떻게 돼?"

print(f"질문: {question}\n")
response = llm.invoke(question)
print(f"답변:\n{response.content}")
```

### 📋 실제 실행 결과
```text
질문: 우리 회사(커넥트)의 신입사원 연차 발생 규정이 어떻게 돼?

답변:
우리 회사의 신입사원 연차 발생 규정은 다음과 같이 일반적으로 적용됩니다.

### 신입사원 연차 발생 규정
1. **연차 시작 시기**: 신입사원은 입사일로부터 1년 경과 후 연차가 발생합니다.
2. **연차 일수**: 1년 차 연차 1일, 2년 차 1.5일 ...
3. **연차 사용 방법**: 연 1회에 한정하여 사용 가능...
```

### ⌥ 결과 분석: 왜 실패인가요?

1. **지식의 부재**: DeepSeek-R1은 인터넷에 공개된 데이터만 학습했습니다. **'커넥트'**라는 회사의 내부 규정은 알 수 없습니다.
2. **그럴싸한 거짓말 (Hallucination)**: 모델은 "모른다"고 답하기보다, 자신이 아는 **일반적인 근로기준법**을 마치 정답인 것처럼 이야기합니다.
3. **✓ 결론**: **외부 지식(우리 회사 데이터)이 없는 LLM은 내부 업무에 활용하기 어렵습니다.**

---

### 왜 LLM은 환각을 일으키는가

LLM은 두 종류의 지식을 사용합니다.

| 지식 유형 | 설명 | 한계 |
|----------|------|------|
| **파라메트릭 지식** | 모델 가중치에 저장된 학습 데이터 | 사내 비공개 정보 없음, 학습 이후 정보 없음 |
| **컨텍스트 지식** | 프롬프트를 통해 실시간 주입하는 정보 | 토큰 한계 내에서만 가능 |

LLM의 본질은 주어진 맥락에서 **가장 그럴듯한 다음 토큰을 예측**하는 것입니다. "모른다"고 말하도록 설계되어 있지 않기 때문에, 사실 여부를 검증하지 않고 그럴듯한 형태의 답변을 생성합니다.

---

### ↳ Next Step
"모르면 가르쳐주면 되지!"
직접 문서를 복사해서 대화창에 넣어주는 **Step 2: 컨텍스트 주입(Context Injection)** 방식으로 문제를 해결해 보겠습니다.


---

## Step 2: [반쪽 성공] 프롬프트에 텍스트 주입 (Context Injection)

LLM에게 정보를 강제로 주입하면 어떻게 되는지 봅니다. 문서가 짧을 때는 가장 확실하고 쉬운 방법입니다.

### 코드: `step2_context.py`

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="deepseek-r1:8b", temperature=0)

# 1. 정보를 변수에 담습니다 (아직 DB 안 씀)
context_data = """
[커넥트 취업규칙]
1. 신입사원은 입사 후 3년 동안은 연차가 없다. (파격적인 규정)
2. 대신 매월 1회 '리프레시 데이'를 유급으로 제공한다.
3. 3년 근속 시 30일의 연차가 일시에 발생한다.
"""

question = "우리 회사(커넥트)의 신입사원 연차 발생 규정이 어떻게 돼?"

# 2. 프롬프트에 정보를 포함시킵니다.
prompt = f"""
아래 [참고 정보]를 보고 질문에 답해줘.
[참고 정보]
{context_data}

질문: {question}
"""
print(f"질문: {question}\n")
response = llm.invoke(prompt)
print(f"답변:\n{response.content}")
```

### 📋 실제 실행 결과
```text
질문: 우리 회사(커넥트)의 신입사원 연차 발생 규정이 어떻게 돼?

답변:
[커넥트 취업규칙]에 따르면, **신입사원의 연차 발생 규정**은 다음과 같습니다:

1. **신입사원은 입사 후 3년 동안 연차가 없다.**
2. **대신 매월 1회 '리프레시 데이'를 유급으로 제공한다.**
3. **3년 근속 시 30일의 연차가 일시에 발생한다.**
```

### ⌥ 핵심 개념: 그라운딩 (Grounding)

- **정의**: AI가 학습된 기억에 의존하지 않고, **제공된 증거(Context)**에 기반하여 답변하도록 묶어두는 기술입니다.
- **Grounding 실패**: "상상해서 말해봐" → (AI: 막 지어냄)
- **Grounding 성공**: "이 문서만 보고 답해" → (AI: 문서 내용만 말함)

### ⌥ 결과 분석

1. **정확도 향상**: 외부 데이터(`context_data`)를 주었으므로 AI가 정확하게 답변합니다. (Grounding 성공)
2. **치명적인 한계**:
    - **입력 길이 제한**: 문서가 수천 페이지라면 프롬프트에 다 넣을 수 없습니다. (Context Window 초과)
    - **비용 문제**: 입력하는 글자 수가 많을수록 API 비용이나 처리 시간이 늘어납니다.

**✓ 결론**: 이 방법은 문서가 매우 짧을 때만 유효하며, 방대한 데이터를 처리하기 위해서는 **Step 3(VectorDB & RAG)**가 필요합니다.

| 접근 방식 | 정확도 | 토큰 사용량 | 실현 가능성 |
|---------|--------|---------|----------|
| LLM 단독 | 0% (환각) | 소량 | 가능 (단, 부정확) |
| Context Injection | 높음 | 문서 수에 비례 폭증 | 소수 문서만 가능 |
| RAG | 높음 | 관련 청크만 사용 | 가능 (수천 문서) |

---

### ↳ Next Step
"문서가 1,000페이지라면 어떡하지?"
모든 문서를 다 읽게 하는 대신, 필요한 부분만 광속으로 찾아내는 **Step 3: VectorDB와 RAG**의 세계로 들어갑니다.


---

## Step 3: [성공] VectorDB와 RAG (청킹의 마법)

데이터가 많을 때를 대비해, 정보를 조각내어 저장하고 필요한 부분만 검색하는 방식(RAG)을 학습합니다.

### 핵심 개념: 청킹, 임베딩, 그리고 k-값

| 개념 | 설명 | 비유 |
| :--- | :--- | :--- |
| **청킹 (Chunking)** | 긴 문서를 AI가 처리하기 좋은 작은 단위로 쪼개는 것 | 책을 찢어서 **포스트잇**으로 만들기 |
| **임베딩 (Embedding)** | 텍스트를 AI가 이해하는 숫자(좌표)로 변환하는 것 | 단어를 **지도상의 위치**로 바꾸기 |
| **Top-K 검색 (k-값)** | 검색 시 가져올 문서 조각의 개수 | 질문과 관련된 **상위 N개의 포스트잇** 고르기 |

> 💡 `nomic-embed-text` 모델이 필요합니다. 아직 다운로드하지 않았다면 `ollama pull nomic-embed-text` 를 실행하세요.

---

### 3-1. 청킹 없이 통째로 넣기 (❌ 비권장)

문서를 쪼개지 않고 하나의 긴 텍스트로 처리합니다.

**코드**: `step3_rag_no_chunking.py`

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

docs_bad = [Document(page_content=context_all, metadata={"source": "전체규정"})]

# 2. VectorDB 생성
print("문서를 학습(임베딩) 중입니다... (청킹 미적용)")
try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=docs_bad, embedding=embeddings)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다.
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}, return_source_documents=True
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

#### ⌥ 분석
- AI가 전체 텍스트 덩어리를 훑은 뒤, 해당 문장을 **복사+붙여넣기** 하듯 출력했습니다.
- **문제**: 데이터가 3줄뿐이라 괜찮지만, 1,000줄이면 AI는 불필요한 999줄을 전부 읽어야 합니다. **속도 저하**와 **비용 낭비**로 직결됩니다.

---

### 3-2. 청킹으로 쪼개서 넣기 (✅ 권장)

문서를 의미 단위로 쪼개어 리스트에 담습니다. 검색엔진이 질문과 가장 관련 있는 '조각'만 찾아냅니다.

**코드**: `step3_rag.py`

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
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)

    # 3. 검색기(Retriever) 설정 (k=3으로 설정하여 성공률 극대화)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다.
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever,
        return_source_documents=True, chain_type_kwargs={"prompt": PROMPT}
    )

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
문서를 학습(임베딩) 중입니다... (청킹 적용)

질문: 신입사원 휴가 규정에 대해 알려줘.
------------------------------

--- 검색된 문서(근거) ---
[인사규정]: [인사규정] 신입사원 휴가 및 연차: ...
[복지규정]: [복지규정] 식대 지원: ...
[보안규정]: [보안규정] 업무 보안: ...

--- AI 답변 ---
신입사원 휴가 규정은 다음과 같습니다:

1. 입사 후 3년 동안 법정 연차 휴가가 발생하지 않습니다.
2. 대신 매월 1회의 유급 '리프레시 데이'를 휴가로 사용할 수 있습니다.
```

#### ⌥ 분석
- AI가 각 문서의 출처를 인지하고, 필요한 정보만 쏙 뽑아 **리스트 형태**로 재구성했습니다.
- **정확도**: 관련 청크만 줬기 때문에 할루시네이션 확률이 매우 낮습니다.
- **✓ 결론**: 청킹은 AI에게 **"정답이 적힌 포스트잇만 골라서 주는 것"**과 같습니다.

| 구분 | 청킹 적용 (✅) | 청킹 미사용 (❌) |
| :--- | :--- | :--- |
| **검색 품질** | 질문과 딱 맞는 부분만 정확히 찾아냄 | 관련 없는 내용까지 섞여서 검색됨 |
| **AI 집중력** | 관련 정보가 농축되어 답변이 정확함 | 정보가 너무 많아 엉뚱한 소리를 함 |
| **비유** | **포스트잇**에서 답 찾기 | **두꺼운 백과사전** 통째로 읽고 답 찾기 |

---

### ↳ Next Step
"내 정보를 찾긴 찾았는데, 복잡한 계산이나 논리 추론도 잘할까?"
단순 검색을 넘어 AI가 스스로 생각하게 만드는 **Step 4: 추론(Reasoning) 능력 활용**으로 넘어갑니다.


---

## Step 4: [심화] AI의 추론(Reasoning) 능력이 필요한 이유

단순히 검색해서 보여주는 것을 넘어, AI가 규정을 이해하고 논리적으로 **추론(Reasoning/Thinking)**하여 복잡한 질문에 답하는 능력이 왜 필요한지 학습합니다.

### 시나리오: 단순 검색으로 풀 수 없는 논리 질문

- **사용자 상황**: "나 입사한 지 6개월 됐는데, 지금까지 쓴 리프레시 데이가 2번이야. 나 남은 리프레시 데이 몇 개야?"
- **AI가 수행해야 할 Thinking 과정**:
  1. **검색**: "리프레시 데이 관련 규정을 찾자." → 매월 1회 제공 확인
  2. **분석**: "사용자는 입사 6개월차이므로 총 6번 발생했다."
  3. **계산**: "6번 - 2번 = 4번 남았다."
  4. **최종 답변**: "남은 리프레시 데이는 4번입니다."

### 코드: `step4_rag.py`

```python
from langchain_classic.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 1. 데이터 준비 (Step 3과 동일)
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
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    template = """당신은 회사의 규정에 대해 설명해주는 AI 비서입니다.
아래의 참고 정보를 바탕으로 질문에 답하세요. 반드시 한국어로 답변해야 합니다.

참고 정보: {context}

질문: {question}
답변:"""
    PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOllama(model="deepseek-r1:8b", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever,
        return_source_documents=True, chain_type_kwargs={"prompt": PROMPT}
    )

    # 추론이 필요한 복잡한 질문
    question = "입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘."
    print(f"\n질문: {question}")
    print("-" * 30)
    result = qa_chain.invoke({"query": question})
    print("\n--- AI 답변 ---")
    print(result['result'])

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
```

### 📋 실제 실행 결과
```text
질문: 입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘.
------------------------------

--- AI 답변 ---
입사 6개월차 신입사원으로서 총 6개월 동안 매월 1회씩 리프레시 데이를 사용할 수 있습니다.
이미 2회 사용했으므로, 남은 리프레시 데이는 **6 - 2 = 4회**입니다.
```

### ⌥ 왜 '추론 모델(Reasoning Model)'인가요?

1. **생각의 사슬 (Chain of Thought)**: 답을 내놓기 전, 스스로 문제를 단계별로 쪼개어 생각합니다.
2. **복합 문맥 이해**: 문서에 없는 '사용자의 현재 상황(6개월차)'을 문서의 '일반 규칙(매월 1회)'에 대입합니다.
3. **수학적 정확도**: 추론 모델은 논리적 인과관계를 따지기 때문에 산술 연산에서 훨씬 높은 정확도를 보입니다.

**✓ 결론**: 진정한 사내 AI 비서를 만들고 싶다면, 단순히 정보를 찾는 RAG를 넘어 **찾은 정보를 똑똑하게 요약하고 계산할 수 있는 추론 모델**을 결합하는 것이 필수적입니다.

---

## Step 3 정리: RAG 학습 여정 복습

| 기둥 | 기술 | 역할 | 비유 |
| :--- | :--- | :--- | :--- |
| **Search (탐색)** | Vector DB (ChromaDB) | 방대한 지식 중 질문과 관련된 정보만 광속으로 찾기 | 똑똑한 도서관 사서 |
| **Context (맥락)** | Prompt Engineering | 찾은 정보를 AI에게 정확히 전달하기 | 책상 위 참고 자료 |
| **Reasoning (추론)** | Reasoning LLM (DeepSeek-R1) | 논리적으로 생각해서 최종 답변하기 | 사려 깊은 인턴 사원 |

| 단계 | 방법 | 정확도 | 출처 제시 | 확장 가능성 |
|------|------|--------|---------|-----------|
| Step 1 | LLM 단독 | 낮음 (환각) | 없음 | 높음 |
| Step 2 | Context Injection | 높음 | 없음 | 낮음 |
| Step 3 | RAG | 높음 | 있음 | 높음 |
| Step 4 | RAG + 추론 | 높음 | 있음 | 높음 |

---

### ↳ Next Step
"이제 RAG의 기본은 끝났습니다!"
그런데 RAG가 답변할 "사내 데이터"가 아직 없습니다. **4단계: FastAPI로 초간단 사내 시스템 만들기**에서 정형 데이터 기반을 구축합니다.


---

# 4단계: FastAPI로 초간단 사내 시스템 만들기

### ◈ 학습 목표
1. **FastAPI** + **PostgreSQL** 로 직원, 휴가, 매출을 관리하는 사내 시스템을 구축합니다.
2. 엑셀에 흩어진 데이터를 **관계형 DB**로 통합합니다.
3. Admin UI로 비기술자도 브라우저에서 데이터를 관리할 수 있게 합니다.

---

## 1) 실습 준비

```bash
cd examples/CH04_FastAPI_기본_시스템
cp .env.example .env
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn app.main:app --reload
```

| 패키지 | 역할 |
|--------|------|
| `fastapi` | 비동기 웹 프레임워크 |
| `uvicorn` | ASGI 서버 |
| `jinja2` | HTML 템플릿 엔진 (Admin UI) |
| `psycopg2-binary` | PostgreSQL 드라이버 |
| `python-dotenv` | `.env` 환경 변수 로드 |
| `pydantic` | 요청/응답 데이터 검증 |

### 실행 확인

| 주소 | 용도 |
|------|------|
| `http://localhost:8000/admin/dashboard` | Admin UI (대시보드) |
| `http://localhost:8000/docs` | Swagger 자동 API 문서 |

---

## 2) 데이터 모델 — 3개 테이블

AI 비서가 답해야 할 질문들을 역순으로 추적하면 3개의 테이블이 필요합니다.

### ERD

| 테이블 | 역할 | 주요 컬럼 |
|--------|------|----------|
| `employee` | 직원 정보 | `emp_no`, `name`, `dept`, `position`, `hire_date` |
| `leave_balance` | 연차 잔여 | `employee_id`, `total_days`, `used_days`, `remaining_days` (자동 계산) |
| `sales` | 매출 현황 | `dept`, `sale_date`, `amount`, `item` |

### schema.sql (핵심)

```sql
CREATE TABLE employee (
    id          SERIAL PRIMARY KEY,
    emp_no      VARCHAR(10)  NOT NULL UNIQUE,
    name        VARCHAR(50)  NOT NULL,
    dept        VARCHAR(50)  NOT NULL,
    position    VARCHAR(50)  NOT NULL,
    hire_date   DATE         NOT NULL
);

CREATE TABLE leave_balance (
    id              SERIAL  PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    year            INTEGER NOT NULL,
    total_days      NUMERIC(4,1) NOT NULL,
    used_days       NUMERIC(4,1) NOT NULL DEFAULT 0,
    remaining_days  NUMERIC(4,1) GENERATED ALWAYS AS (total_days - used_days) STORED,
    UNIQUE (employee_id, year)
);

CREATE TABLE sales (
    id          SERIAL PRIMARY KEY,
    dept        VARCHAR(50)  NOT NULL,
    sale_date   DATE         NOT NULL,
    amount      BIGINT       NOT NULL,
    item        VARCHAR(200) NOT NULL
);
```

> 💡 `remaining_days`는 PostgreSQL **계산 컬럼**입니다. `total_days - used_days`를 DB가 직접 계산하므로 애플리케이션 버그가 없습니다.

`docker compose up -d` 한 줄이면 DDL + 시드 데이터(직원 5명, 연차 5건, 매출 10건)까지 자동 완료됩니다.

---

## 3) API 엔드포인트 목록

| 경로 | 메서드 | 기능 |
|------|--------|------|
| `/api/employees` | GET | 직원 목록 (이름/부서 필터) |
| `/api/employees` | POST | 직원 등록 |
| `/api/leaves/{id}` | GET | 연차 잔여 조회 |
| `/api/leaves/{id}/use` | POST | 연차 사용 등록 |
| `/api/sales` | GET | 매출 조회 (부서/기간 필터) |
| `/api/sales` | POST | 매출 등록 |

---

## 4) Admin UI 확인

1. `http://localhost:8000/admin/dashboard` → 통계 카드 3개
2. `http://localhost:8000/admin/employees` → 직원 목록 + 등록 폼
3. `http://localhost:8000/admin/leaves` → 연차 잔여 현황
4. `http://localhost:8000/admin/sales` → 매출 현황 + 부서별 합계

---

## 5) 결과 분석

| 항목 | Before | After |
|------|--------|-------|
| 직원 현황 파악 | `직원현황.xlsx` 수기 확인 | Admin UI 즉시 조회 |
| 휴가 잔여 집계 | 팀장 수기 스프레드시트 (30분) | DB 계산 컬럼 즉시 반환 (0분) |
| 매출 데이터 취합 | 부서별 개별 파일 취합 (1시간) | 부서·기간 필터 즉시 조회 |
| AI 비서 연동 | 불가 (구조화 데이터 없음) | CH08 MCP Tool이 SQL로 직접 조회 |

> ⚠️ **실습 환경 정리**: `Ctrl+C`로 서버 종료, `docker compose down`으로 컨테이너 종료

---

### ↳ Next Step
"사내 DB는 완성됐는데, AI가 검색할 비정형 문서는?"
**5단계: 사내 문서 수집 전략과 문서 표준 만들기**에서 RAG 인덱싱에 적합한 문서를 준비합니다.


---

# 5단계: 사내 문서 수집 전략과 문서 표준 만들기

### ◈ 학습 목표
1. **"Garbage In, Garbage Out"** 원칙을 이해합니다. 정제되지 않은 문서는 RAG 품질을 떨어뜨립니다.
2. 파일명 규칙과 폴더 구조를 표준화합니다.
3. 파일 형식별(PDF, DOCX, XLSX) 파싱 특성을 이해합니다.

---

## 1) 교재용 문서 세트 (6개)

| 파일명 | 형식 | 부서 | 설명 |
|--------|------|------|------|
| `HR_취업규칙_v1.0.pdf` | PDF | 인사 | 연차, 급여, 복지 규정 전문 |
| `HR_정보보안서약서.pdf` | PDF (이미지) | 인사 | 입사 시 서명 보안 서약 |
| `SEC_보안규정_v1.0.docx` | DOCX | 보안 | 정보보안 규정 (표 포함) |
| `OPS_신규서비스_런칭전략.pdf` | PDF | 운영 | 신규 서비스 출시 전략 |
| `FIN_부서별_예산기안서.xlsx` | XLSX | 재무 | 부서별 예산 기안 |
| `FIN_2025_상반기_매출현황.xlsx` | XLSX | 재무 | 매출 현황표 |

---

## 2) 파일명 규칙

```
{부서코드}_{문서종류}_v{버전}.{확장자}
```

| 코드 | 부서 |
|------|------|
| `HR` | 인사 |
| `SEC` | 보안 |
| `OPS` | 운영 |
| `FIN` | 재무 |

> 💡 CH06에서 파일명에서 부서·버전 정보를 자동 추출하여 메타데이터로 활용합니다.

---

## 3) 폴더 구조

```
data/docs/
├── hr/
│   ├── HR_취업규칙_v1.0.pdf
│   └── HR_정보보안서약서.pdf
├── security/
│   └── SEC_보안규정_v1.0.docx
├── ops/
│   └── OPS_신규서비스_런칭전략.pdf
└── finance/
    ├── FIN_부서별_예산기안서.xlsx
    └── FIN_2025_상반기_매출현황.xlsx
```

---

## 4) 형식별 파싱 특성

| 형식 | 파싱 라이브러리 | 파싱 난이도 | 비고 |
|------|---------------|-----------|------|
| PDF (텍스트) | `pypdf` | 보통 | 레이아웃 정보 손실 가능 |
| PDF (이미지) | Vision LLM (LLaVA) | 높음 | 텍스트 추출 불가, CH10에서 해결 |
| DOCX | `python-docx` | 낮음 | 표, 단락 구조 보존 |
| XLSX | `openpyxl` | 낮음 | 시트별 데이터 추출 |

---

## 5) 메타데이터 7개 항목

| 항목 | 설명 | 예시 |
|------|------|------|
| `doc_id` | 문서 고유 식별자 | `HR_취업규칙_1.0` |
| `title` | 문서 종류 | `취업규칙` |
| `department` | 부서명 | `인사` |
| `version` | 버전 번호 | `1.0` |
| `date` | 파일 수정일 | `2025-01-15` |
| `format` | 파일 형식 | `PDF` |
| `file_size_bytes` | 파일 크기 | `153600` |

---

## 6) 결과 분석

| 지표 | Before | After |
|------|--------|-------|
| 파일명 규칙 | 없음 (자유 형식) | `{부서}_{종류}_v{버전}.{확장자}` |
| 폴더 구조 | 단일 폴더 100+ 파일 | 부서별 4개 폴더 분류 |
| 메타데이터 | 없음 | 7개 항목 정의 완료 |

**✓ 결론**: 문서 표준화에 30분이 걸리지만, 이 30분이 이후 모든 챕터의 RAG 품질을 결정합니다.

---

### ↳ Next Step
"문서는 정리했는데, AI가 읽을 수 있나?"
**6단계: VectorDB 구축**에서 실제로 텍스트를 추출하고, 청크로 분할하여 ChromaDB에 저장합니다.


---

# 6단계: VectorDB 구축 — 문서를 검색 가능한 지식으로 바꾸기

### ◈ 학습 목표
1. Python 파싱 라이브러리(`pypdf`, `python-docx`, `openpyxl`)로 텍스트를 추출합니다.
2. 500자 단위 청킹과 **ko-sroberta-multitask** 임베딩을 거쳐 **ChromaDB**에 저장합니다.
3. CLI에서 자연어 검색을 테스트하여 인덱스 품질을 검증합니다.

---

## 1) 실습 환경 준비

```bash
cd examples/CH06_VectorDB_구축
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

| 패키지 | 역할 |
|--------|------|
| `pypdf` | PDF 텍스트 추출 |
| `python-docx` | DOCX 단락·표 추출 |
| `openpyxl` | XLSX 시트·셀 추출 |
| `sentence-transformers` | ko-sroberta 임베딩 모델 |
| `chromadb` | VectorDB 저장 및 검색 |

---

## 2) 핵심 개념

### 청킹 — 왜 500자인가

| 크기 | 장단점 |
|------|--------|
| 너무 작음 (300자) | 문장이 잘려 의미 손실 |
| **적절 (500자 + 100자 오버랩)** | **균형점** |
| 너무 큼 (1000자) | 검색 정밀도 낮아짐 |

```
원본 텍스트:  [...400자...][...400자...][...400자...]
청크 1:        [________500자_________]
청크 2:               [___100자___][________500자_______]
```

오버랩으로 청크 경계에서 잘리는 문장의 맥락 손실을 줄입니다.

### ko-sroberta-multitask

한국어에 특화된 임베딩 모델입니다. 768차원 벡터를 생성하며, 최초 실행 시 약 400MB를 다운로드합니다.

### ChromaDB

로컬 파일 시스템에 영속 저장(`PersistentClient`)하며, Docker 없이 `pip install`만으로 설치됩니다.

---

## 3) [Step 1] Python 파싱 실행

```bash
python src/main.py --step 1
```

### 📋 실제 실행 결과

| 파일명 | 형식 | 추출 글자 수 | 상태 |
|--------|------|------------|------|
| `HR_취업규칙_v1.0.pdf` | PDF (다단 레이아웃) | 1,906자 | 텍스트 추출됨, 배치 무너짐 |
| `HR_정보보안서약서.pdf` | PDF (이미지 스캔) | **0자** | 텍스트 레이어 없음 (전량 손실) |
| `OPS_신규서비스_런칭전략.pdf` | PDF (슬라이드) | 1,435자 | 텍스트 추출됨 |
| `SEC_보안규정_v1.0.docx` | DOCX | 896자 | 정상 추출 |
| `FIN_2025_상반기_매출현황.xlsx` | XLSX | 891자 | 정상 추출 |
| `FIN_부서별_예산기안서.xlsx` | XLSX | 633자 | 정상 추출 |

> ⚠️ 이미지 스캔 PDF는 텍스트 레이어가 없어 글자를 전혀 추출하지 못합니다. CH10에서 Vision LLM으로 해결합니다.

---

## 4) 전체 파이프라인 실행

```bash
python src/main.py
```

Step 1(파싱) → 청킹(500자 + 100자 오버랩) → ko-sroberta 임베딩 → ChromaDB 저장까지 한 번에 실행합니다.

---

## 5) CLI 검색 검증

```bash
python src/cli_search.py --query "연차 사용 규정"
```

### 📋 검색 결과 해석

| 유사도 | 의미 | 조치 |
|--------|------|------|
| 80% 이상 | 관련도 높음 | 정상 |
| 70~80% | 관련도 보통 | 청크 크기 또는 임베딩 모델 검토 |
| 70% 미만 | 관련도 낮음 | 쿼리 표현 방식 또는 문서 내용 확인 |

---

## 6) 결과 분석

| 지표 | Before | After |
|------|--------|-------|
| 문서 검색 방식 | 파일명으로 수동 탐색 | 의미 기반 벡터 검색 |
| 검색 소요 시간 | 10~30분 | 1초 미만 |
| 출처 확인 | 파일 직접 열어 검색 | 파일명 + 페이지 즉시 표시 |

---

### ↳ Next Step
"검색은 되는데, 직원들이 터미널을 쓸 수 있을까?"
**7단계: RAG로 Q&A 엔진 만들기**에서 브라우저 채팅 UI를 구현합니다.


---

# 7단계: RAG로 Q&A 엔진 만들기

### ◈ 학습 목표
1. **LCEL(LangChain Expression Language)** 기반 RAG 체인으로 질문 → 검색 → 답변 파이프라인을 조립합니다.
2. 출처가 포함된 구조화된 응답과 **채팅 웹 UI**를 구현합니다.
3. 세션 기반 **멀티턴 대화**를 관리합니다.

---

## 1) 실습 환경 준비

```bash
cd examples/CH07_RAG_QA_엔진
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
python app/main.py
```

브라우저에서 `http://localhost:8000/chat` 접속

---

## 2) LCEL이란 무엇인가

| 구성 요소 | 역할 |
|----------|------|
| **Retriever** | ChromaDB에서 유사한 문서 검색 |
| **Prompt Template** | 시스템 규칙 + 컨텍스트 + 질문 조립 |
| **LLM** | DeepSeek R1이 답변 생성 |
| **OutputParser** | LLM 응답에서 순수 문자열 추출 |

### RAG 체인 핵심 코드

```python
# src/rag_chain.py (핵심 발췌)
chain = (
    {
        "context": itemgetter("question") | retriever | _format_docs,
        "history": itemgetter("history"),
        "question": itemgetter("question"),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

파이프 연산자(`|`)로 데이터 흐름이 왼쪽에서 오른쪽으로 한눈에 보입니다.

---

## 3) 출처 강제 프롬프트

```
규칙:
1. 반드시 제공된 문서에서만 근거를 찾아 답변하시오.
2. 문서에서 답을 찾을 수 없으면 "해당 내용은 제공된 문서에서 확인되지 않습니다."라고 답하시오.
3. 답변 마지막에 근거 문서명을 반드시 명시하시오. 형식: [출처: 문서명]
4. 추측이나 외부 지식을 사용하지 마시오.
```

### 응답 JSON 구조

```json
{
  "answer": "신입사원 온보딩 절차는...\n[출처: HR_취업규칙_v1.0]",
  "sources": [
    {"doc": "HR_취업규칙_v1.0", "page": 12, "snippet": "제3조 (온보딩 절차)..."}
  ],
  "session_id": "a1b2c3d4-..."
}
```

---

## 4) 멀티턴 대화

`WindowMemory`로 최근 N턴만 유지합니다. `deque(maxlen=k)`를 사용하여 k+1번째 항목이 들어오면 가장 오래된 항목을 자동 제거합니다.

```
> "온보딩 절차를 알려줘."
> "그 중 보안 서약은 언제까지 해야 해?"  ← "그 중"이 무엇인지 이전 대화에서 파악
> "아, 그러면 입사 첫날 어디로 가면 돼?"
```

---

## 5) 결과 분석

| 지표 | Before (CLI 검색) | After (웹 채팅 UI) |
|------|------------------|--------------------|
| 사용 가능한 인원 | 개발자 1명 | 전 직원 30명 |
| 질의 방식 | 터미널 명령어 | 브라우저 채팅 |
| 출처 표시 | 텍스트 출력 | 근거 아코디언 UI |
| 대화 맥락 유지 | 불가능 | 멀티턴 대화 지원 |

---

### ↳ Next Step
"온보딩 절차는 잘 답하는데, '김철수 연차 며칠 남았어?'는 못 답합니다."
**8단계: 정형 MCP + 비정형 RAG 통합 에이전트**에서 DB 데이터까지 처리합니다.


---

# 8단계: 정형 MCP + 비정형 RAG 통합 에이전트

### ◈ 학습 목표
1. **QueryRouter** 로 질문을 정형/비정형/복합으로 자동 분류합니다.
2. **MCP 도구 4종**으로 PostgreSQL DB를 직접 조회합니다.
3. **ReAct Agent**로 DB + 문서 결과를 통합하여 답변합니다.

---

## 1) 질문 유형 분류

| 유형 | 데이터 위치 | 처리 경로 | 예시 |
|------|-----------|----------|------|
| 정형 | PostgreSQL DB | MCP 도구로 SQL 조회 | "김민준 연차 잔여일수" |
| 비정형 | 사내 문서 | VectorDB + RAG 체인 | "온보딩 절차를 알려줘" |
| 복합 | DB + 문서 | 두 경로를 순차/병렬 실행 | "매출 상위 부서의 복지 정책" |

---

## 2) QueryRouter — 3단계 폴백

| 단계 | 방법 | 속도 |
|------|------|------|
| Step 1 | 키워드 기반 ("연차", "매출" → 정형 / "절차", "정책" → 비정형) | 1ms 미만 |
| Step 2 | DB 컬럼명 기반 (`remaining_days`, `amount` 포함 여부) | 1ms 미만 |
| Step 3 | LLM에게 판단 위임 (모호한 질문만) | 수 초 |

```python
STRUCTURED_KEYWORDS = ["잔여", "연차", "휴가", "매출", "합계", "목록", "명단", "통계"]
UNSTRUCTURED_KEYWORDS = ["절차", "방법", "어떻게", "규정", "정책", "온보딩", "가이드"]

def _step1_rule_based(self, query: str):
    s_hits = sum(1 for kw in STRUCTURED_KEYWORDS if kw in query)
    u_hits = sum(1 for kw in UNSTRUCTURED_KEYWORDS if kw in query)
    if s_hits > 0 and u_hits > 0:
        return "hybrid"
    if s_hits > 0:
        return "structured"
    if u_hits > 0:
        return "unstructured"
    return None  # 다음 단계로 폴백
```

---

## 3) MCP 도구 4종

| 도구 | 기능 | 파라미터 |
|------|------|---------|
| `leave_balance` | 직원 연차 잔여 조회 | `emp_no` (번호 또는 이름) |
| `sales_sum` | 매출 합계 조회 | `dept`, `start_date`, `end_date` |
| `list_employees` | 직원 목록 조회 | `dept` (부서 필터) |
| `search_documents` | 사내 문서 벡터 검색 | `query`, `k` |

> ⚠️ 이 챕터는 Tool Calling을 지원하는 `llama3.1:8b` 모델을 사용합니다.
> ```bash
> ollama pull llama3.1:8b
> ```

---

## 4) ReAct Agent — 복합 질문 처리

**ReAct(Reasoning + Acting)** 패턴: "먼저 생각하고, 행동하고, 관찰하고, 다시 생각하는" 반복

```
질문: "매출 상위 부서의 워케이션 규정은?"

[Reasoning] "매출 상위 부서"는 DB 조회가 필요하다. sales_sum을 호출하자.
[Acting]    sales_sum 도구 호출 → 영업부 매출 합계 반환
[Reasoning] "워케이션 규정"은 문서 검색이 필요하다. search_documents를 호출하자.
[Acting]    search_documents("워케이션 규정") → 규정 문서 발견
[Reasoning] 두 결과를 합쳐 최종 답변을 만들 수 있다.
[Acting]    최종 답변 생성
```

---

## 5) 실습

```bash
cd examples/CH08_통합_에이전트_설계
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
docker compose up -d
uvicorn app.main:app --reload --port 8008
```

브라우저에서 `http://localhost:8008/chat` 접속

### 대표 시나리오 3개 테스트

| 시나리오 | 질문 | 기대 경로 |
|---------|------|----------|
| 정형 | "김민준 연차 잔여일수 알려줘" | `leave_balance` 도구 |
| 비정형 | "보안 정책에 대해 설명해줘" | `search_documents` 도구 |
| 복합 | "매출 상위 부서의 워케이션 규정은?" | `sales_sum` + `search_documents` |

---

## 6) 결과 분석

| 지표 | Before (RAG만) | After (RAG + MCP) |
|------|----------------|-------------------|
| 처리 가능한 질문 유형 | 비정형만 | 정형 + 비정형 + 복합 |
| 10개 시나리오 정답률 | 4/10 | 10/10 |
| 연차 조회 | 불가능 | DB에서 즉시 조회 |
| 매출 통계 | 불가능 | 부서별·기간별 집계 |

---

### ↳ Next Step
"10개 시나리오는 통과했는데, 하루 100건이 넘어가면 느려집니다."
**9단계: LangChain으로 연결 전략 세팅**에서 운영 안정성을 확보합니다.


---

# 9단계: LangChain으로 연결 전략 세팅

### ◈ 학습 목표
1. Router/Agent/Tools **분리 구조**로 코드를 정리합니다.
2. **Timeout + Retry** 로 타임아웃 발생률 15% → 2%로 감소시킵니다.
3. **응답 캐시**로 동일 질문 응답 시간 5초 → 0.3초로 단축합니다.
4. **구조화된 로그**로 에러 추적과 비용 모니터링을 확보합니다.

---

"되는 것"과 "운영할 수 있는 것"은 다릅니다. 하루 50건이던 질의가 100건을 넘기자 세 가지 문제가 동시에 터졌습니다.

1. LLM 호출이 30초를 넘기는 경우 발생
2. 동일한 질문이 반복되어도 매번 LLM을 호출
3. 에러가 발생해도 로그가 없어 원인 불명

---

## 1) 코드 구조 분리

```
src/
├── agent_config.py    ← Router + Agent + RAG Chain 통합
├── cache.py           ← 응답 캐시 + 임베딩 캐시
├── monitoring.py      ← 구조화 로그 + 토큰 추적
└── tools/
    ├── __init__.py
    ├── leave_balance.py
    ├── sales_sum.py
    ├── list_employees.py
    └── search_documents.py
```

> 💡 새 도구를 추가할 때 파일 하나만 만들면 됩니다. 기존 코드 수정 불필요.

---

## 2) Router 전략

| 경로 | 실행 방식 | 장점 |
|------|----------|------|
| `"db"` | Agent가 DB 도구 직접 호출 | 도구 1회 호출로 빠른 응답 |
| `"rag"` | LCEL RAG 체인 직접 실행 | Agent 없이 한 번에 답변 |
| `"agent"` | ReAct Agent가 도구 반복 선택 | 복합 질문에 유연 대응 |

---

## 3) Timeout + Retry

- **Timeout**: `max_execution_time=60` 초, 도구를 아무리 많이 호출해도 60초 초과 시 자동 종료
- **Retry**: 실패 시 2초 대기 후 최대 3회 재시도

---

## 4) 응답 캐시

질문 문자열을 SHA-256 해시로 변환하여 캐시 키를 만듭니다. TTL(기본 3600초) 이내 동일 질문은 LLM 호출 없이 저장된 응답을 반환합니다.

---

## 5) 구조화된 로그

```json
{"timestamp": "2026-02-28T09:15:32+00:00", "level": "INFO", "logger": "agent_config", "message": "[Router] 쿼리 분류 완료: route=db"}
```

---

## 6) 실습

```bash
cd examples/CH09_LangChain_연결
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
docker compose up -d
uvicorn app.main:app --reload --port 8009
```

### 캐시 테스트
1. `김민준 연차 잔여일수 알려줘` → 첫 질문: LLM 호출 (수 초)
2. 동일 질문 재입력 → 캐시 히트: 즉시 응답 (0.3초)

---

## 7) 결과 분석

| 지표 | Before (CH08) | After (운영 최적화) |
|------|--------------|-------------------|
| 타임아웃 발생률 | 15% | 2% (Timeout + Retry) |
| 동일 질문 응답 시간 | 5초 | 0.3초 (TTL 캐시) |
| 에러 추적 | 불가능 | JSON 로그 + Langfuse |
| 도구 추가 소요 시간 | 코드 전체 수정 | 파일 1개 추가 (10분) |

---

### ↳ Next Step
"운영은 안정됐는데, '보안 정책 물어봤는데 출장 규정이 나왔어요'라는 피드백이..."
**10단계: RAG 튜닝**에서 증상별 처방으로 정확도를 높입니다.


---

# 10단계: RAG 튜닝 — 되는 수준에서 쓸만한 수준으로

### ◈ 학습 목표
1. 증상별 패턴을 진단하고 **비용이 적은 순서**로 처방합니다.
2. 프롬프트 튜닝, Chunk 조정, ReRanker, Hybrid Search, Query Rewrite 5가지 기법을 실습합니다.
3. 각 처방의 효과를 비교하여 최적 조합을 찾습니다.

---

AI 비서를 배포한 지 2주, 직원 피드백을 분석해봤습니다.

- "보안 정책을 물어봤는데 출장 규정이 나왔습니다." → 관련 없는 문서 검색됨
- "옛날 버전 답변이 나왔습니다." → 메타데이터 필터링 미적용
- "재택 물어봤는데 WFH를 인식 못합니다." → 약어 처리 부재
- "문서에 없는 내용을 자신 있게 답변합니다." → LLM 환각 발생

---

## 문제 → 처방 매핑

| 증상 | 원인 | 처방 | 비용 |
|------|------|------|------|
| 환각 발생 | 프롬프트 규칙 미비 | 프롬프트 튜닝 | 0원 |
| 답변 부정확 | 청크 품질 낮음 | Chunk 조정 | 0원 |
| 관련 없는 문서 상위 | 벡터 유사도만 사용 | ReRanker | 모델 80MB |
| 키워드 질문 약함 | 의미 검색만 사용 | Hybrid Search | 구현 1시간 |
| 약어 인식 못함 | 동의어 미처리 | Query Rewrite | LLM 1회 추가 |

> 💡 핵심: **비용이 적은 처방부터** 시도합니다. 한꺼번에 적용하면 어떤 처방이 효과를 낸 건지 알 수 없습니다.

---

## 실습 환경 준비

```bash
cd examples/CH10_RAG_튜닝
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
docker compose up -d
```

---

## 처방 1: 프롬프트 튜닝 (비용 0원)

**비유**: 의사의 진료 지침. "적당히 답변하세요" vs "검사 결과를 근거로 답변하세요"

```
[기존 프롬프트]
"다음 문서를 참고하여 질문에 답변하세요."

[개선 프롬프트]
"반드시 제공된 문서의 내용만 사용하여 답변하십시오.
답변 시 근거 문서의 제목과 섹션을 명시하십시오.
문서에 없는 내용은 '해당 내용을 문서에서 찾을 수 없습니다'라고 답변하십시오.
추측이나 외부 지식을 사용하지 마십시오."
```

| 규칙 | 효과 |
|------|------|
| "문서에 없으면 모른다고 답변" | 환각률 15% → 5% |
| "출처 필수 표시" | 사용자가 답변을 검증 가능 |
| "추측 금지" | 자신 있게 틀린 답변 방지 |

**✓ 결과**: 프롬프트 수정만으로 환각률 15% → 5%. 코드 변경 없이 텍스트만 바꾼 것이므로 비용 0원.

---

## 처방 2: Chunk 튜닝 (비용 0원)

**비유**: 노트 카드 크기. 너무 작으면 문맥 없음, 너무 크면 노이즈 혼재.

| 전략 | 방식 | 장점 | 단점 |
|------|------|------|------|
| **Fixed-size** | 글자 수로 자른다 | 가장 빠르고 단순 | 문장 중간에서 잘릴 수 있음 |
| **Recursive** | 문단·문장 경계를 존중하며 자른다 | 자연스러운 분할 | Fixed보다 약간 느림 |
| **Semantic** | 의미 유사도가 달라지는 지점에서 자른다 | 주제 단위 분할 | 가장 느림 |

```bash
python -m tuning.chunk_experiment
```

**✓ 결과**: Fixed-size(500자)가 속도와 품질의 균형점.

---

## 처방 3: ReRanker (모델 80MB)

**비유**: 서류 심사(벡터 검색) 후 면접관(Cross-Encoder)이 직접 재평가

```python
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, documents, top_k=5):
        pairs = [(query, doc["content"]) for doc in documents]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked[:top_k]]
```

```bash
python -m tuning.reranker
```

**✓ 결과**: 벡터 검색 상위 20개를 Cross-Encoder가 5개로 추린다. 관련 없는 문서가 하위로 밀려남.

---

## 처방 4: Hybrid Search (구현 1시간)

**비유**: 목차 검색(키워드) + 내용 검색(의미)을 합치기

```python
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

bm25_retriever = BM25Retriever.from_texts(texts=documents, metadatas=metadatas)
bm25_retriever.k = 5

vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

ensemble = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6],  # BM25 40% + Vector 60%
)
results = ensemble.invoke("보안 정책에서 USB 사용 규정")
```

```bash
python -m tuning.hybrid_search
```

| alpha 값 | BM25 비중 | Vector 비중 | 적합한 질문 유형 |
|----------|----------|------------|----------------|
| 0.0 | 100% | 0% | 키워드가 명확한 질문 |
| **0.4** | **40%** | **60%** | **대부분의 사내 질문에 적합 (기본값)** |
| 1.0 | 0% | 100% | 추상적 질문 |

---

## 처방 5: Query Rewrite (LLM 1회 추가)

**비유**: 통역사가 약어를 정식 명칭으로 번역

```python
ABBREVIATION_MAP = {
    "WFH": "재택근무",
    "OT": "초과근무",
    "HR": "인사부서",
    "PIP": "성과개선계획",
    "반차": "반일 연차",
}

def expand_query(query):
    for abbr, full in ABBREVIATION_MAP.items():
        query = query.replace(abbr, full)
    return query
```

```bash
python -m tuning.query_rewrite
```

**✓ 결과**: "WFH 정책" → "재택근무 정책"으로 변환되어 올바른 문서를 찾습니다.

---

## 문서 파싱 고도화: 텍스트 복사기 vs 사진사

| 전략 | 방식 | 속도 | 이미지/차트 |
|------|------|------|------------|
| 라이브러리 파싱 | pypdf + pdfplumber | 빠름 (0.3초) | ❌ 불가 |
| vLLM 파싱 | PDF → PNG → LLaVA | 느림 (4.2초) | ✅ 분석 가능 |

```python
import fitz  # PyMuPDF
import base64, httpx

doc = fitz.open("HR_취업규칙_v1.0.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save("page_1.png")

img_b64 = base64.b64encode(open("page_1.png", "rb").read()).decode()

resp = httpx.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llava:7b",
        "messages": [{"role": "user",
            "content": "이 문서 이미지의 텍스트, 표, 차트를 마크다운으로 추출하세요.",
            "images": [img_b64]}],
        "stream": False,
    },
)
markdown_text = resp.json()["message"]["content"]
```

---

## 최종 결과 분석

| 처방 | 비용 | 주요 효과 |
|------|------|----------|
| 프롬프트 튜닝 | 0원 | 환각률 15% → 5% |
| Chunk 조정 | 0원 | 검색 정밀도 향상 |
| ReRanker | 80MB 모델 | 관련 없는 문서 필터링 |
| Hybrid Search | 구현 1시간 | 키워드 + 의미 검색 결합 |
| Query Rewrite | LLM 1회 | 약어·동의어 해결 |

---

## 마치는 글

RAG는 단순한 기술이 아니라, **"AI에게 정확한 근거를 제시하고 논리적으로 생각할 시간을 주는 철학"** 입니다.

이 책을 마치면 세 가지 핵심 역량을 갖추게 됩니다.

1. **RAG 파이프라인 구축 능력** — 사내 문서를 벡터 DB에 인덱싱하고, 사용자 질문에 맞는 청크를 검색하여 LLM 답변에 근거를 붙이는 전체 파이프라인
2. **MCP 통합 에이전트 설계 능력** — 정형 DB와 비정형 문서를 하나의 에이전트에서 처리하는 구조
3. **실전 RAG 튜닝 능력** — 증상에서 원인을 찾아 체계적으로 개선 효과를 측정하는 방법론

| 지표 | Before | After (목표) |
|------|--------|-------------|
| 직원 1인 문서 검색 시간 | 30분/일 | 30초/건 |
| 인사팀 반복 질의 처리 | 20건/일 (수동) | 0건 (AI 자동 응답) |
| 신입사원 정보 접근 | 선배에게 직접 질문 | AI 비서에 즉시 질문 |

**✓ 수고하셨습니다! 이제 당신만의 커스텀 RAG AI를 만들 준비가 되었습니다.**
