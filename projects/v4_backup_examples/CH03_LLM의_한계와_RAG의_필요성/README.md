# CH03 LLM의 한계와 RAG의 필요성

> 사내 문서 기반 AI 업무 비서 (RAG + MCP) - 3장 실습 코드

## 학습 목표

- LLM의 환각(Hallucination) 현상을 직접 체험하고 원인을 이해합니다.
- Context Injection의 작동 원리와 토큰 한계 문제를 체감합니다.
- RAG(Retrieval-Augmented Generation)가 환각 문제를 어떻게 해결하는지 확인합니다.
- DeepSeek R1의 Chain-of-Thought 추론 능력을 RAG와 결합하여 활용합니다.

## 4단계 실습 구성

| 스크립트 | 단계 | 핵심 체험 |
|---------|------|---------|
| `src/01_llm_only.py` | 실패 | LLM 단독 질의 → 환각 응답 체험 |
| `src/02_context_injection.py` | 임시 해결 | 문서 삽입 → 정확도 향상, 토큰 한계 체감 |
| `src/03_rag_preview.py` | 성공 | 인메모리 ChromaDB 검색+답변 |
| `src/04_rag_reasoning.py` | 심화 | RAG + 계산/분석 추론 질문 |

## 실행 환경

- Python 3.10 이상
- Ollama + DeepSeek R1 모델 (`deepseek-r1:8b` 또는 더 작은 모델)
- 인터넷 연결 (최초 1회 한국어 임베딩 모델 다운로드 ~400MB)

## 사전 준비 — Ollama 설치 및 모델 다운로드

이 챕터는 별도의 Docker 인프라가 필요 없습니다. Ollama만 설치하면 됩니다.

Ollama를 설치합니다.

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: https://ollama.ai 에서 설치 파일 다운로드
```

DeepSeek R1 모델을 다운로드합니다.

```bash
ollama pull deepseek-r1:8b
```

> RAM이 부족한 경우 더 작은 모델을 사용하십시오.
> ```bash
> ollama pull deepseek-r1:1.5b
> ```
> .env 파일에서 `OLLAMA_MODEL=deepseek-r1:1.5b`로 변경하면 됩니다.

Ollama 서버를 실행합니다. 별도 터미널에서 실행하거나 백그라운드로 실행합니다.

```bash
ollama serve
```

## 설치 및 실행

이 챕터의 예제 코드 저장소를 clone합니다.

```bash
git clone https://github.com/{repo}/ch03-llm-rag-preview
cd ch03-llm-rag-preview
```

환경 변수를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열고 필요한 값을 입력합니다.
# 기본값(Ollama + deepseek-r1:8b)이면 별도 수정 없이 바로 실행 가능합니다.
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (WSL2 또는 PowerShell)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> 최초 실행 시 한국어 임베딩 모델(`jhgan/ko-sroberta-multitask`)이 자동으로 다운로드됩니다.
> 약 400MB이며, 다운로드 이후에는 캐시에서 즉시 로드됩니다.

## 실행 순서

4개의 스크립트를 순서대로 실행하여 RAG의 필요성을 단계별로 체험합니다.

### 단계 1: LLM 단독 질의 (환각 체험)

```bash
python src/01_llm_only.py
```

### 단계 2: Context Injection (토큰 한계 체감)

```bash
python src/02_context_injection.py
```

### 단계 3: RAG 미리보기 (인메모리 ChromaDB)

```bash
python src/03_rag_preview.py
```

### 단계 4: RAG + 추론 능력 확인

```bash
python src/04_rag_reasoning.py
```

## 예상 실행 결과

<!-- [CAPTURE NEEDED: 각 스크립트 실행 후 전체 터미널 화면] -->

### 단계 1 실행 결과 예시

```
[실습 시작] LLM 단독 질의
  LLM 제공자: OLLAMA
  질문: 김철수 사원의 남은 연차는 며칠인가요?

  LLM에 질문 중... (최대 120초 대기)

============================================================
[실습 1] LLM 단독 질의 — 사내 정보 질문하기
============================================================

[사용 모델] OLLAMA / deepseek-r1:8b

[질문]
김철수 사원의 남은 연차는 며칠인가요?

[LLM 응답]
----------------------------------------
죄송합니다만, 저는 특정 직원의 개인 연차 정보에 접근할 수 없습니다.
김철수 사원의 남은 연차를 확인하시려면 인사팀에 문의하시거나
사내 HR 포털에 로그인하여 확인하시기 바랍니다.
----------------------------------------

[분석]
  위 응답은 그럴듯하게 보이지만, 실제 사내 데이터와 다릅니다.
  LLM은 학습 데이터에 없는 사내 비공개 정보를 알 수 없어
  그럴듯한 내용을 '만들어내는' 환각(Hallucination)을 일으킵니다.

  다음 실습: python src/02_context_injection.py
```

> **참고**: LLM 응답은 모델과 실행 환경에 따라 다를 수 있습니다. 실제 환각은 "김철수 사원의 남은 연차는 10일입니다."처럼 전혀 다른 숫자를 그럴듯하게 생성하는 형태로 나타납니다.

### 단계 3 실행 결과 예시

```
[실습 3] RAG 미리보기 — 인메모리 ChromaDB 검색+답변
============================================================

[사용 모델] OLLAMA / deepseek-r1:8b
[임베딩 모델] jhgan/ko-sroberta-multitask
[데이터베이스] ChromaDB 인메모리 (실행 종료 시 데이터 소멸)

  [ChromaDB] 컬렉션 'ch03_rag_no_chunk' 생성 중...
  [임베딩 모델] jhgan/ko-sroberta-multitask
  [완료] 4개 문서 → 4개 청크 저장 (청킹 없음(전체 문서))
  [LLM] 답변 생성 중...

============================================================
[RAG 실험] 청킹 없음 (전체 문서)
============================================================

[질문] 김철수 사원의 남은 연차는 며칠인가요?

[검색된 관련 문서 — 상위 3개]
  [1] 출처: 인사팀 | 유사도: 0.891
      내용 미리보기: 인사팀 직원 연차 현황 (2025년 기준)
김철수 사원: 부서=개발팀, 입사일=2021-03...

[LLM 답변]
----------------------------------------
김철수 사원의 남은 연차는 6일입니다.

인사팀 직원 연차 현황 문서에 따르면:
- 연차 총일수: 15일
- 사용 연차: 9일
- 남은 연차: 15 - 9 = 6일
----------------------------------------
```

## 전체 아키텍처

```mermaid
flowchart LR
    A["Step 1: LLM 단독"] -- "환각" --> B["Step 2: 원인 분석"]
    B -- "해결 시도" --> C["Step 3: Context Injection"]
    C -- "토큰 한계" --> D["Step 4: RAG 미리보기"]
    D -- "성공" --> E["Step 5: 추론 심화"]
```

## 자주 발생하는 오류

| 오류 메시지 | 원인 | 해결 방법 |
|------------|------|---------|
| `Ollama 서버에 연결할 수 없습니다` | Ollama가 실행되지 않음 | `ollama serve` 실행 |
| `모델 'deepseek-r1:8b'이 pull되어 있는지 확인` | 모델 미다운로드 | `ollama pull deepseek-r1:8b` |
| `임베딩 모델 로드에 실패` | 인터넷 연결 없음 또는 첫 다운로드 실패 | 인터넷 연결 확인 후 재실행 |
| `Ollama 응답 시간이 초과` | 모델이 너무 크거나 RAM 부족 | `deepseek-r1:1.5b` 소형 모델 사용 |

## 다음 챕터 안내

- **CH04**: FastAPI + PostgreSQL로 실제 사내 시스템(직원/휴가/매출 CRUD)을 구축합니다.
- **CH06**: 이 챕터의 인메모리 ChromaDB를 영속화하고 PDF/DOCX를 자동 인덱싱합니다.
