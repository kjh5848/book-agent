# 엑셀 RAG 데이터 처리 실습 (Excel RAG Handling)

이 프로젝트는 엑셀 데이터를 RAG(Retrieval-Augmented Generation) 시스템에 통합할 때 발생하는 **다양한 실패 케이스**와 그 **해결 전략**을 실습하는 공간입니다.

## 📂 실습 케이스 목록 (Overview)

| ID | 케이스명 (Case Name) | 난이도 | 상태 | 핵심 문제 (RAG Failure) | 해결 전략 (Key Strategy) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | 기본 읽기 (Basic Read) | Easy | ✅ 완료 | 단순 표 데이터 읽기 | `pandas.read_excel()` |
| **02** | 다중 시트 (Multiple Sheets) | Easy | ✅ 완료 | 여러 시트에 분산된 데이터 | `pd.ExcelFile()`, 시트 순회 |
| **03** | 복잡한 헤더 (Complex Header) | Medium | ✅ 완료 | 병합된 헤더, 멀티 인덱스 | `header=[0,1]`, `index_col` |
| **04** | 비정형 데이터 (Unstructured) | Hard | ✅ 완료 | 텍스트(메타데이터)와 표가 섞임 | 좌표 기반 추출 (`iloc`), `openpyxl` |
| **05** | 시각적 속성 (Visual Attributes) | Medium | 🚧 예정 | "빨간색 셀" 등 시각적 정보 소실 | `openpyxl` 스타일 추출 (Color/Font) |
| **06** | 다중 테이블 (Multiple Tables) | Hard | 🚧 예정 | 한 시트에 물리적으로 떨어진 여러 표 존재 | 클러스터링(Clustering) 및 영역 분리 |
| **07** | 수식 및 참조 (Formulas) | Medium | 🚧 예정 | 계산되지 않은 수식 문자열(`=A1*B1`) 반환 | `data_only=True` (값으로 계산하여 읽기) |
| **08** | 숨겨진 데이터 (Hidden Data) | Easy | 🚧 예정 | 숨겨진 행/열이 검색 결과에 노출됨 | `hidden` 속성 확인 후 로드 제외 |
| **09** | 이미지/차트 (Images & Charts) | Very Hard | 🚧 예정 | 이미지 내 텍스트 인식 불가능 | OCR / VLM (Vision Model) 활용 |
| **10** | 피벗 테이블 (Pivot Tables) | Hard | 🚧 예정 | 원본 데이터 부재 (요약본만 존재) | 피벗 캐시 접근 또는 Unpivot |

---

## 🔍 상세 가이드 (Case Details)

### 1단계: 기본기 다지기 (Fundamentals)

#### **01. 기본 읽기 (Basic Read)**
*   **목표**: 가장 일반적인 형태의 엑셀 "표" 데이터 처리.
*   **실습 내용**: 단순 차트 및 날짜 데이터 포맷팅 처리.

#### **02. 다중 시트 (Multiple Sheets)**
*   **목표**: 여러 시트에 나뉠 데이터를 통합하거나 선별적으로 추출.
*   **실습 내용**: 특정 시트 필터링 및 전체 시트 일괄 처리(Batch Processing).

#### **03. 복잡한 헤더 (Complex Header)**
*   **목표**: "병합된 셀(Merged Cells)"로 인해 깨지는 데이터 구조 복원.
*   **실습 내용**: 다중 헤더(Multi-level Header) 및 다중 인덱스(Multi-Index) 평탄화(Flattening).

#### **04. 비정형 데이터 (Unstructured)**
*   **목표**: "문서"처럼 쓰인 엑셀 파일에서 메타데이터와 본문 표 분리.
*   **실습 내용**: 좌표 기반(`iloc`)으로 제목, 작성일 등 메타데이터 추출 후 테이블 파싱.

---

### 2단계: 실무 필수 실패 케이스 (Essential Failures)

#### **05. 시각적 속성 (Visual Attributes)**
> *"중요한 건 빨간색으로 표시했습니다."*
*   **RAG 실패 원인**: `pandas`는 텍스트 값만 읽고, 셀의 배경색(Color)이나 폰트 스타일(Bold/Strikethrough) 정보를 무시함. 이로 인해 "중요한 데이터"를 식별 불가.
*   **해결책**: `openpyxl` 엔진을 사용하여 셀 스타일 속성을 추출하고, 이를 별도 컬럼(`is_important`, `color_code`)으로 매핑.

#### **06. 다중 테이블 (Multiple Tables)**
> *"1월 매출표 밑에 2월 매출표가 있어요."*
*   **RAG 실패 원인**: 엑셀 전체를 하나의 DataFrame으로 읽으려 시도함. 중간의 빈 행(`NaN`)과 서로 다른 헤더 구조 때문에 데이터가 뒤섞임.
*   **해결책**: 데이터가 존재하는 셀 영역(Cluster)을 감지하고, 좌표 범위(Range)를 나누어 개별 테이블로 추출(Slicing).

#### **07. 수식 및 참조 (Formulas)**
> *"가격은 환율에 따라 자동 계산됩니다."*
*   **RAG 실패 원인**: 엑셀 파일에 저장된 값이 아닌 수식 문자열(`=A1*1300`)을 그대로 가져와, LLM이 계산 불가능하거나 잘못된 값을 참조(Hallucination).
*   **해결책**: 엑셀 로드 시 `data_only=True` 옵션을 사용하여 수식이 계산된 최종 값(Evaluated Value)만 읽도록 강제.

#### **08. 숨겨진 데이터 (Hidden Data)**
> *"이건 옛날 자료라 숨겨놨어요."*
*   **RAG 실패 원인**: 사용자는 "삭제했다"고 생각하지만, 실제로는 "숨김(Hidden)" 처리만 된 데이터가 검색 결과에 포함되어 최신 정보와 충돌.
*   **해결책**: 행/열의 속성(`hidden`)을 검사하여 숨겨진 데이터는 로드 과정에서 필터링.

---

### 3단계: 심화 케이스 (Advanced)

#### **09. 이미지/차트 (Images & Charts)**
*   **문제**: 엑셀 내부에 삽입된 이미지나 차트는 텍스트 파서가 인식하지 못해 정보 공백 발생.
*   **해결**: 이미지 추출 후 OCR 또는 VLM(Vision Language Model) 사용.

#### **10. 피벗 테이블 (Pivot Tables)**
*   **문제**: 원본 데이터 없이 요약된 결과만 존재하거나, 레이아웃이 복잡하여 정형화 어려움.
*   **해결**: Unpivot(Melting) 과정을 통해 분석 가능한 형태로 재구조화.
