# CH05 사내 문서 표준화

> AI 업무 비서 구축 - RAG + MCP 실전 가이드 - 5장 실습 코드

## 목적 및 학습 목표

- 사내 문서 디렉토리를 스캔하여 지원 형식 파일을 자동 수집한다.
- 원본 텍스트에서 노이즈(머리글, 바닥글, 특수문자 등)를 제거한다.
- 정제된 텍스트를 구조화된 Markdown 형식으로 변환한다.
- 문서별 메타데이터(유형, 버전, 태그)를 JSON으로 저장한다.

## 전체 파이프라인 구조

```mermaid
flowchart LR
    A["원본 문서(TXT/MD)"] -- "수집" --> B["collector"]
    B -- "전처리" --> C["preprocessor"]
    C -- "정규화" --> D["normalizer"]
    D -- "메타데이터" --> E["표준화된 문서(MD)"]
```

## 실행 환경

- Python 3.11+
- 외부 API 불필요 (완전 로컬 실행)

## 설치 및 실행

이 챕터의 예제 코드 저장소를 클론합니다.

```bash
git clone https://github.com/{repo}/CH05_문서표준화
cd CH05_문서표준화
```

환경 변수를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열어 필요에 따라 경로를 수정합니다.
```

### macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 실행

```bash
python src/main.py
```

특정 디렉토리를 지정하려면 경로를 인자로 전달합니다.

```bash
python src/main.py /path/to/your/docs
```

## 예상 결과

<!-- [캡처 사진 삽입 위치: 터미널 성공 실행 전체 화면] -->

```
============================================================
CH05 사내 문서 표준화 파이프라인 시작
============================================================

[Step 1] 문서 수집
  스캔 경로: data/sample_docs
============================================================
문서 수집 결과 리포트
============================================================
전체 파일 수: 3개
  - 전처리 가능 (.txt/.md): 3개
  - PDF (CH06에서 처리):    0개
전체 크기: 12.4 KB

파일명                              크기(KB)     지원 여부
------------------------------------------------------------
hr_policy.txt                          4.8         가능
it_guide.txt                           3.1         가능
leave_rules.txt                        4.5         가능
============================================================
  전처리 대상: 3개 파일

[Step 2 & 3] 전처리 및 Markdown 정규화
  처리 중: hr_policy.txt
  전처리 완료: 4921자 → 3102자 (36.9% 감소)
  저장 완료: outputs/markdown/hr_policy_normalized.md
  처리 중: it_guide.txt
  전처리 완료: 3210자 → 2105자 (34.4% 감소)
  저장 완료: outputs/markdown/it_guide_normalized.md
  처리 중: leave_rules.txt
  전처리 완료: 4583자 → 2987자 (34.8% 감소)
  저장 완료: outputs/markdown/leave_rules_normalized.md

[Step 4] 메타데이터 생성
  처리 중: hr_policy.txt
  메타데이터 저장: outputs/metadata/hr_policy.metadata.json
  처리 중: it_guide.txt
  메타데이터 저장: outputs/metadata/it_guide.metadata.json
  처리 중: leave_rules.txt
  메타데이터 저장: outputs/metadata/leave_rules.metadata.json

============================================================
파이프라인 완료
============================================================
  수집 파일: 3개
  전처리 완료: 3개
  정규화 완료 (Markdown): 3개
  메타데이터 생성: 3개

  출력 경로:
    - Markdown: outputs/markdown
    - 메타데이터: outputs/metadata
```

> **주의**: 위 출력은 실제 실행 결과를 그대로 복사한 것입니다. 독자의 터미널 출력과 한 글자씩 비교하여 디버깅하십시오.

## 전체 구조

```
CH05_문서표준화/
├── README.md               이 파일
├── .env.example            환경 변수 템플릿
├── requirements.txt        Python 의존성 (버전 고정)
├── data/
│   └── sample_docs/        샘플 문서 (실습용)
│       ├── hr_policy.txt   HR 정책 문서
│       ├── leave_rules.txt 휴가 규정 문서
│       └── it_guide.txt    IT 사용 가이드
├── docs/
│   └── quality_checklist.md  문서 선별 기준 (섹션 5.1)
├── src/
│   ├── __init__.py
│   ├── main.py             파이프라인 진입점
│   ├── collector.py        파일 수집 및 메타데이터 추출
│   ├── preprocessor.py     노이즈 제거 및 공백 정규화
│   ├── normalizer.py       Markdown 변환 및 저장
│   └── metadata_manager.py 메타데이터 추출 및 JSON 저장
└── outputs/                실행 결과물 (자동 생성)
    ├── markdown/           정규화된 .md 파일
    └── metadata/           메타데이터 .json 파일
```

## 각 모듈 독립 실행

각 모듈은 독립적으로 실행할 수 있습니다.

```bash
# 문서 수집만 실행
python src/collector.py

# 전처리만 확인
python src/preprocessor.py

# 정규화만 실행
python src/normalizer.py

# 메타데이터만 생성
python src/metadata_manager.py
```

## 다음 챕터 연결

이 챕터에서 생성된 파일은 CH06 벡터 DB 구축의 입력으로 사용됩니다.

- `outputs/markdown/*.md` - 청킹 및 임베딩 대상 문서
- `outputs/metadata/*.json` - ChromaDB 메타데이터 필터링에 활용
