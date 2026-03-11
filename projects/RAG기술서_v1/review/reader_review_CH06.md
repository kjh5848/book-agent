# CH06 벡터 DB 구축 독자 리뷰 리포트

**페르소나**: 입문자 (beginner) — Python 기초 지식 보유, LLM/RAG 개념 없음 | **총점**: 63/100점

---

## 1위 개선 항목: 실행 가능성 (15/25점)

**현재 상태**: README의 "실행 순서"는 `data/create_sample_pdfs.py`를 실행하여 PDF를 생성하라고 안내하지만, 실제 `main.py` 코드는 `data/docs/` 폴더를 탐색한다(`glob.glob(os.path.join(docs_dir, "**", "*.pdf"), recursive=True)`). 입문자가 README 안내대로 `python data/create_sample_pdfs.py`를 실행하면 PDF는 `data/` 폴더에 생성되고, `main.py`는 `data/docs/` 폴더에 PDF가 없다며 종료된다. 이 불일치를 발견하려면 소스 코드를 읽어야 하는데, 이는 입문자에게 진입 장벽이다.

추가로, `.env.example` 파일에 어떤 환경 변수가 있는지 README에 예시가 없다. "기본값으로도 실습이 가능합니다"라고만 쓰여 있어, 입문자는 `.env` 파일을 열어도 무엇을 확인해야 하는지 모른다.

**개선 방향**:
1. README의 "1단계: 샘플 PDF 생성" 명령어를 실제 코드 동작과 일치하도록 수정한다. `create_sample_pdfs.py`가 `data/docs/` 하위에 파일을 저장하도록 바꾸거나, main.py의 탐색 경로를 `data/`로 맞춘다.
2. "설치 및 실행" 섹션에 `.env.example` 주요 변수(예: `EMBED_MODEL`, `CHROMA_PERSIST_DIR`, `COLLECTION_NAME`)와 기본값을 한 줄 표로 추가한다.
3. `data/docs/` 폴더가 없으면 발생하는 오류 메시지와 해결 방법을 README "자주 묻는 오류" 섹션에 명시한다.

---

## 2위 개선 항목: 오류 대응성 (7/15점)

**현재 상태**: Ollama 서버 미실행 시 발생하는 `ConnectionError`에 대한 안내("Ollama 서버 실행 상태를 유지해야 합니다")는 있다. 그러나 입문자가 실제로 마주치는 나머지 오류 상황에 대한 안내가 없다.

- `data/docs/` 폴더가 없거나 PDF가 없을 때: `sys.exit(1)`로 종료되지만 해결 방법이 README에 없다.
- `pip install -r requirements.txt` 중 `pymupdf` 빌드 실패(Windows 환경에서 빈번함): 안내 없음.
- ChromaDB가 이미 존재하는 상태에서 재실행할 때 중복 저장 여부: 안내 없음.
- Ollama 모델이 아직 다운로드 중일 때 `ollama serve`를 실행하는 순서 오류: 안내 없음.

**개선 방향**:
1. README에 "자주 발생하는 오류" 섹션을 추가하고, 최소 3가지(PDF 없음, Ollama 미실행, ChromaDB 중복) 오류 증상과 해결 명령어를 표 형태로 제공한다.
2. `main.py` 실행 전 사전 점검 단계(Ollama 서버 응답 확인 명령어: `curl http://localhost:11434/`)를 README에 한 줄 추가한다.
3. 재실행 시 기존 ChromaDB를 초기화하는 방법(`outputs/chroma_db/` 폴더 삭제)을 안내한다.

---

## 3위 개선 항목: 코드 이해도 (16/25점)

**현재 상태**: 함수마다 docstring이 잘 갖춰져 있고 IPO 주석 블록도 명확하다. 그러나 입문자에게는 "왜 이 설계인지"에 대한 설명이 부족하다.

- `fixed_size_chunk`의 `overlap=50` 파라미터: "인접 청크 간 겹치는 문자 수"라고 설명하지만 왜 필요한지 이유가 없다. 입문자는 overlap이 0이면 안 되는지 모른다.
- `chunker.py`의 내부 함수 `get_page_for_position`: 페이지 번호 추적이 왜 필요한지 맥락이 없다.
- `extractor.py`의 `is_complex_layout` 함수: 임계값 `threshold=0.3`이 어떤 근거로 정해진 값인지 설명이 없어, 입문자가 이 함수가 언제 동작하는지 직관적으로 이해하기 어렵다.
- `requirements.txt`에 `reportlab`이 없는데 README에는 "reportlab (샘플 PDF 생성용)"이 명시되어 있다. `create_sample_pdfs.py` 실행에 필요한 패키지가 누락되어 있다.

**개선 방향**:
1. `fixed_size_chunk` docstring에 overlap의 존재 이유를 한 문장 추가한다. 예: "overlap이 없으면 청크 경계에서 문장이 잘려 검색 품질이 저하됩니다."
2. `requirements.txt`에 `reportlab`을 추가하거나, `create_sample_pdfs.py` 파일 상단에 `pip install reportlab` 안내 주석을 추가한다.
3. `is_complex_layout`의 `expected_chars_per_page = 1500` 상수 옆에 근거를 주석으로 추가한다. 예: "A4 기준 약 30행 × 50자 = 1,500자 추정"

---

## 잘된 점

- README에 OS별(macOS/Linux/Windows) 설치·실행 명령어가 분리되어 있어 플랫폼 혼란이 없다.
- 예상 터미널 출력이 상세하게 제공되어 "내 실행 결과가 맞는지" 비교할 수 있다.
- Mermaid 다이어그램이 전체 파이프라인(PDF → 추출 → 청킹 → 임베딩 → ChromaDB → CH07)을 한 눈에 보여준다.
- CH05 네이밍 규칙 연결과 CH07 복사 명령어가 명시되어 챕터 간 흐름이 자연스럽다.
- 모든 핵심 함수에 Args/Returns/Raises가 Google-style docstring으로 문서화되어 있다.
- `--vision` 플래그 동작 방식을 표로 비교하여 두 모드의 차이가 직관적으로 전달된다.

---

## 종합 의견

Python 기초만 알고 LLM·RAG 개념이 없는 입문자 입장에서, 이 프로젝트의 가장 큰 문제는 "안내대로 따라했는데 실행이 안 되는" 상황이다. README의 실행 순서와 실제 코드의 PDF 탐색 경로 불일치는 첫 실행에서 막히게 만드는 치명적 오류이며, 이 한 가지만 수정해도 실행 가능성 점수가 크게 오를 수 있다. 코드 구조와 문서화 수준은 전반적으로 양호하지만, 개념 설명 없이 기술 용어(임베딩, 청킹, ChromaDB, Ollama)를 나열하는 방식은 입문자가 "이게 왜 필요한가"를 이해하지 못한 채 따라 치는 데 그치게 만든다. 각 단계 앞에 한두 문장의 "왜" 설명을 추가하면 학습 효과가 크게 향상될 것이다.
