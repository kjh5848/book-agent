# 📖 Case 06: 복합 레이아웃 (Complex Layout)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 최상 (High)
- **주요 기술 (Key Tech)**: **Zone Splitting, Pipeline Orchestration, Header Caching**
- **핵심 개념 (Core Concept)**: 복잡한 문서는 '한 번에' 읽을 수 없습니다. 사람이 문서를 볼 때처럼 **"상단 제목 -> 본문 -> 중간 표 -> 하단 결론"** 순서로 시선(Cursor)을 이동시키는 로직을 코드로 구현해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 단일 페이지 복합 레이아웃 (Single-Page Complex)
- **입력 (Input)**: `06_case1_복합문서.pdf`
- **문제 (Problem)**: **"레이아웃의 혼돈"**. 2단 다단, 표, 본문이 한 페이지 내에서 수시로 교차합니다. 단순 추출 시 표 데이터가 본문 문장 사이에 끼어드는 문맥 파괴가 발생합니다.
- **해결 (Solution)**: **Zone Splitting Strategy**.
    1. **Table Isolation**: 표의 위치(`bbox`)를 먼저 탐지하여 데이터 보호 구역으로 설정합니다.
    2. **Vertical Segmentation**: 표를 기준으로 페이지를 상(A), 중(B-Table), 하(C)로 나눕니다.
    3. **Contextual Merge**: 각 영역을 성격에 맞게(다단 또는 일반) 추출한 뒤 논리적 순서로 재조립합니다.

### 🔹 Case 2: 5페이지 통합 복합 보고서 (5-Page Integrated Report)
- **입력 (Input)**: `06_case2_복합보고서.pdf`
- **문제 (Problem)**: **"정보 밀도와 레이아웃 결합"**. 다단 편집, 테두리 없는 투명표, 이어지는 연속표, 사이드바, 필기체 메모가 집약되어 있으며 공백 없이 꽉 채워진 전문 보고서 형태입니다.
- **해결 (Solution)**: **Advanced Pipeline & Caching**.
    1. **Dynamic Zone Splitting**: 본문과 사이드바 영역을 좌표계 기반으로 분리합니다.
    2. **Grid/Table Reconstruction**: 선 없는 표를 텍스트 밀도 분석으로 복원합니다.
    3. **Header Caching**: 연속표에서 이전 페이지 헤더를 캐싱하여 데이터 의미를 유지합니다.

### 🔹 Case 3: 실전 정부 모집공고문 파싱 (Real Govt Announcement)
- **입력 (Input)**: `06_case3_복합_...pdf` (제도전성공패키지 공고문)
- **문제 (Problem)**: **"구조화된 표의 중첩"**. 지원 자격, 제외 대상, 지원 내역 등이 중첩된 격자 표 안에 담겨 있어 단순 추출 시 정보의 선후 관계가 완전히 파괴됩니다.
- **해결 (Solution)**: **Table-Text Isolation & Markdown Conversion**.
    1. **Find Tables**: `pdfplumber`를 이용해 표의 경계를 먼저 확정합니다.
    2. **BBox Filtering**: 표 내부 텍스트와 외보 텍스트를 엄격히 분리 추출합니다.
    3. **Pandas Bridge**: 표 데이터를 `Pandas`를 거쳐 `Markdown Table`로 변환하여 LLM이 명확히 행/열 관계를 이해하도록 유도합니다.

## 3. RAG 구축 전략 (RAG Strategy)

| 문제 상황 | RAG에 미치는 영향 (Risk) | 해결 전략 (Solution) |
| :--- | :--- | :--- |
| **다단 + 표** | 표 데이터가 본문 문장 사이에 끼어들어 문맥이 단절되고, LLM이 문장과 표를 구분하지 못함. | **영역 분할 (Zone Splitting)**: 표 좌표를 기준으로 페이지를 상/중/하로 나누어 처리. |
| **연속표 (Multi-page)** | 페이지가 넘어가면서 헤더가 소실되면 하단 데이터의 의미를 LLM이 유추하지 못함. | **헤더 캐싱 (Header Caching)**: 이전 페이지의 컬럼 정보를 유지하여 의미 부여. |
| **사이드바 노이즈** | 본문 중간에 사이드바 정보가 삽입되어 정보의 응집도가 떨어짐. | **기하학적 분리 (BBox Filtering)**: 좌표 기반으로 사이드바를 별도 섹션으로 격리. |

> [!TIP]
> **멘토의 한마디 (Mentor's Tip)**
> 복잡한 문서는 단일 도구로 해결하려 하지 마십시오. `pdfplumber`로 영역을 나누고, `pandas`로 표를 정제하며, 필요한 경우 `VLM`으로 시각 정보를 해석하는 **오케스트레이션(Orchestration)** 능력이 고성능 RAG의 핵심입니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 결과 요약 | RAG 성능 영향 |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `06_complex_report_성공.md` | 표-본문-사이드바 완벽 분리 | 정밀한 답변 생성 (LLM Context 보존) |
| **실패 (Fail)** | `06_case2_실패.md` | 텍스트가 뒤섞인 스파게티 상태 | 오답 발생 및 할루시네이션 유발 |
