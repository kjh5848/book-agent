# CH05 사내 문서 수집 표준화

> 사내 문서 기반 AI 업무 비서 (RAG + MCP) — 5장 실습 코드

## 목적 및 학습 목표

- 문서 품질이 RAG 성능의 핵심 요소임을 이해한다
- `{부서}_{문서종류}_v{버전}.{확장자}` 파일명 표준 규칙을 적용한다
- PDF, DOCX, XLSX 형식별 처리 차이를 체감한다
- 메타데이터(doc_id, title, department, version, date, format)를 자동 추출하는 도구를 만든다
- 검증 결과(PASS / WARN / FAIL)를 `outputs/metadata.json`으로 저장한다

## 실행 환경

- Python 3.10+
- 외부 서비스 불필요 (로컬 실행 전용)

## 설치 및 실행

이 챕터의 예제 코드 저장소를 클론한다.

```bash
git clone https://github.com/{repo}/CH05_사내_문서_수집_표준화
```

`CH05_사내_문서_수집_표준화` 폴더로 이동한다.

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
python src/validator.py
```

## 예상 출력

<!-- [CAPTURE NEEDED: 전체 터미널 실행 화면 — validator.py 정상 실행 후] -->

```
============================================================
   CH05 문서 수집 표준화 검증 도구
============================================================
문서 폴더: .../data/docs
출력 경로: .../outputs/metadata.json

총 6개 문서 검증 시작...

------------------------------------------------------------
[WARN] FIN_2025_상반기_매출현황.xlsx
       부서: 재무 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: FIN_2025_상반기_매출현황_v1.0.xlsx)

[WARN] FIN_부서별_예산기안서.xlsx
       부서: 재무 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: FIN_부서별_예산기안서_v1.0.xlsx)

[WARN] HR_정보보안서약서.pdf
       부서: 인사 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: HR_정보보안서약서_v1.0.pdf)

[PASS] HR_취업규칙_v1.0.pdf
       부서: 인사 | 버전: 1.0
       메시지: 파일명 규칙 준수

[WARN] OPS_신규서비스_런칭전략.pdf
       부서: 운영 | 버전: unversioned
       메시지: 버전 정보 누락 (권장 형식: OPS_신규서비스_런칭전략_v1.0.pdf)

[PASS] SEC_보안규정_v1.0.docx
       부서: 보안 | 버전: 1.0
       메시지: 파일명 규칙 준수

메타데이터 저장 완료: .../outputs/metadata.json

============================================================
            문서 검증 결과 요약
============================================================
  전체 문서:  6개
  PASS:       2개  (33.3%)
  WARN:       4개  (66.7%)
  FAIL:       0개  (0.0%)
------------------------------------------------------------

조치가 필요한 항목:
  [WARN] FIN_2025_상반기_매출현황.xlsx
         → 버전 정보 누락 (권장 형식: FIN_2025_상반기_매출현황_v1.0.xlsx)
  [WARN] FIN_부서별_예산기안서.xlsx
         → 버전 정보 누락 (권장 형식: FIN_부서별_예산기안서_v1.0.xlsx)
  [WARN] HR_정보보안서약서.pdf
         → 버전 정보 누락 (권장 형식: HR_정보보안서약서_v1.0.pdf)
  [WARN] OPS_신규서비스_런칭전략.pdf
         → 버전 정보 누락 (권장 형식: OPS_신규서비스_런칭전략_v1.0.pdf)
============================================================

최종 판정: WARN (4개 문서에 경고가 있습니다. 표준 규칙 적용을 권장합니다.)
```

> **참고**: 위 출력은 실제 실행 결과를 그대로 복사한 것입니다. 터미널 출력과 한 글자씩 비교하여 디버깅에 활용하십시오.

## 전체 구조

```mermaid
flowchart LR
    A["원본 문서(PDF/DOCX/XLSX)"] -- "폴더 배치" --> B["data/docs/{부서}/"]
    B -- "파일명 검증" --> C["validator.py"]
    C -- "메타데이터 추출" --> D["metadata.json"]
    D -- "PASS" --> E["CH06으로 전달"]
```

## 폴더 구조

```
CH05_사내_문서_수집_표준화/
├── README.md
├── requirements.txt
├── data/
│   └── docs/
│       ├── hr/
│       │   ├── HR_취업규칙_v1.0.pdf
│       │   └── HR_정보보안서약서.pdf
│       ├── security/
│       │   └── SEC_보안규정_v1.0.docx
│       ├── ops/
│       │   └── OPS_신규서비스_런칭전략.pdf
│       └── finance/
│           ├── FIN_부서별_예산기안서.xlsx
│           └── FIN_2025_상반기_매출현황.xlsx
├── src/
│   ├── __init__.py
│   └── validator.py
└── outputs/
    └── metadata.json  ← 실행 후 생성됨
```
