# 엑셀 처리 라이브러리 및 스크립트 가이드 (ex01)

이 문서는 `실습용/ex01/scripts/excel_scripts` 디렉토리에 포함된 엑셀 처리 스크립트들이 사용하는 라이브러리와 주요 기법을 설명합니다.

## 1. 사용된 핵심 라이브러리

### `pandas`
- **용도**: 엑셀 데이터 읽기/쓰기, 데이터 프레임(DataFrame) 변환, 필터링 및 전처리.
- **특징**: 데이터 분석의 표준 라이브러리로, 엑셀의 표 데이터를 가장 효율적으로 다룹니다.
- **주요 메서드**:
  - `read_excel()`: 엑셀 파일을 읽어 DataFrame으로 반환.
  - `to_csv()`: DataFrame을 CSV 파일로 저장.
  - `to_json()`: DataFrame을 JSON 파일로 저장.
  - `iloc[]`: 행/열의 위치(Index) 기반으로 데이터 선택.

### `openpyxl`
- **용도**: 엑셀 파일의 엔진(Engine) 역할. `pandas`가 엑셀 파일을 읽을 때 내부적으로 사용됩니다.
- **특징**: 최신 엑셀 파일(`.xlsx`)을 처리하는 데 최적화되어 있습니다.
- **직접 사용 시점**:
    - `pandas`만으로 해결되지 않는 **시각적 속성(색상, 폰트)**을 읽거나,
    - **이미지**를 추출하거나,
    - **숨겨진 시트**를 제어해야 할 때 직접 호출하여 사용합니다.

---

## 2. 주요 스크립트별 기법 분석

### A. 기본 읽기 (Basic Read)
- **파일**: `01_기본읽기/case1_단순차트/parse_success.py`
- **핵심 코드**:
  ```python
  # 가장 기본적인 형태의 읽기
  df = pd.read_excel(input_path)
  ```
  - **작동 원리**: 엑셀의 첫 번째 시트를 찾아 `A1` 셀부터 데이터가 있는 끝까지 자동으로 읽어옵니다.

### B. 시트 필터링 (Sheet Filtering)
- **파일**: `02_multiple_sheets/case1_시트필터/parse_success.py`
- **핵심 코드**:
  ```python
  # 엑셀 파일 객체를 생성하여 메타데이터(시트 목록 등)만 먼저 로드
  xls = pd.ExcelFile(input_path)
  
  # 시트 이름 목록을 순회하며 조건에 맞는 시트만 읽기
  for sheet_name in xls.sheet_names:
      if "Sheet" not in sheet_name:
          df = pd.read_excel(xls, sheet_name=sheet_name)
  ```
  - **사용 시점**: 파일 하나에 성격이 다른 여러 시트가 섞여 있을 때, 필요한 시트만 골라내기 위해 사용합니다.

### C. 복잡한 헤더 처리 (Complex Header)
- **파일**: `03_complex_header/case1_병합헤더/parse_success.py`
- **핵심 코드**:
  ```python
  # header=[0, 1]: 첫 2줄을 모두 헤더로 인식 (MultiIndex Column)
  df = pd.read_excel(input_path, header=[0, 1])
  
  # index_col=[0, 1]: 첫 2열을 모두 행 인덱스로 인식 (MultiIndex Row)
  df = pd.read_excel(input_path, index_col=[0, 1])
  ```
  - **사용 시점**: 셀 병합(Merged Cells)으로 인해 헤더가 두 줄 이상이거나, 행(Row) 분류가 계층적일 때 구조를 유지하기 위해 사용합니다.

### D. 비정형 데이터 추출 (Unstructured / Coordinate-Based)
- **파일**: `04_unstructured/case1_메타데이터/parse_success.py`
- **핵심 코드**:
  ```python
  # header=None으로 전체를 Raw 데이터로 읽음
  df = pd.read_excel(input_path, header=None)
  
  # 좌표(iloc)를 사용하여 특정 위치의 메타데이터 추출 (예: A1, B2)
  title = df.iloc[0, 0]
  date = df.iloc[1, 1]
  
  # 실제 표가 시작되는 5행부터 슬라이싱하여 테이블 생성
  table_df = df.iloc[5:].copy()
  ```
  - **사용 시점**: 엑셀이 "문서(Document)"처럼 작성되어, 표 위에 제목이나 결재란 등 다른 정보가 섞여 있을 때 위치 기반으로 데이터를 발라내기 위해 사용합니다.

---

## 3. 요약: 언제 무엇을 써야 할까?

| 상황 | 추천 도구/옵션 | 이유 |
| :--- | :--- | :--- |
| **단순한 표** | `pd.read_excel()` | 가장 빠르고 코드가 간결함. |
| **시트가 여러 개** | `pd.ExcelFile()` | 시트 목록을 먼저 확인하고 반복문 처리가 가능. |
| **병합된 헤더** | `header=[0, 1]` | 병합된 정보를 다중 인덱스로 구조화하여 보존. |
| **문서형 엑셀** | `header=None` + `iloc` | 데이터 위치가 고정되어 있을 때 좌표로 찍어서 추출. |
| **색상/스타일** | `openpyxl` (엔진 직접 사용) | Pandas는 색상을 볼 수 없음. (Case 05에서 다룸) |
