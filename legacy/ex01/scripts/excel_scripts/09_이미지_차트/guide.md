# 📖 Case 09: 이미지/차트 (Images & Charts)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 최상 (Very Hard)
- **주요 라이브러리 (Key Library)**: `openpyxl` (Image Extraction), `Vision LLM` (Analysis)
- **핵심 개념 (Core Concept)**: 엑셀 시트에 붙여넣어진 차트나 이미지는 **텍스트 데이터가 아니므로** `pandas`가 읽을 수 없습니다. 이를 **이미지 파일로 추출**하여 별도로 처리해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 이미지 추출 및 설명 생성 (Image Extraction)
- **입력 (Input)**: `../data/09_case1_이미지추출.xlsx`
- **문제 (Problem)**: "2024년 1분기 매출 추이"가 텍스트 표가 아니라 **차트 이미지**로만 존재함. RAG 시스템은 이 정보를 전혀 볼 수 없음.
- **해결 (Solution)**:
    1. `openpyxl`로 시트 내의 이미지 객체(`ws._images`)를 탐색합니다.
    2. 발견된 이미지를 `.png` 파일로 디스크에 저장합니다.
    3. (추후 단계) 저장된 이미지를 GPT-4o 같은 **Vision LLM**에게 전송하여 "이 차트가 보여주는 트렌드를 텍스트로 설명해줘"라고 요청하고, 그 결과를 RAG 문맥에 포함시킵니다.
- **핵심 코드 (Key Code)**:
  ```python
  from openpyxl import load_workbook
  from PIL import Image
  
  wb = load_workbook(input_file)
  ws = wb.active
  
  if ws._images:
      for img in ws._images:
          # 이미지 객체에서 바이너리 데이터 추출
          img.ref.seek(0)
          pil_img = Image.open(img.ref)
          pil_img.save("extracted_chart.png")
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **멀티모달 RAG** | **Image Extraction** | **Markdown** | `![Chart](path/to/img.png)` 형태로 텍스트 문서 내에 이미지를 포함시켜, VLM이 문맥과 함께 이해하도록 함. |
| **순수 텍스트 RAG** | **Automatic Captioning** | **JSON/Valid Text** | Vision Model이 이미지를 "매출 상승 그래프"라는 텍스트로 변환하여 저장. |
| **아카이빙** | **File Linking** | **JSON** | 원본 파일 경로만 저장하고 필요시 다운로드 링크 제공. |

> **💡 본 실습의 선택**:
> - **Case 1 -> Markdown**: 추출된 이미지를 Markdown 문서 내에 직접 임베딩하여, 텍스트(설명)와 이미지(시각자료)가 하나의 문맥(Context)으로 연결되도록 구성합니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `09_case1_이미지추출_성공.md` | Markdown + Image | `![Chart](../images/chart.png)` <br> -> VLM이 이미지를 보고 **"1분기 매출이 우상향하고 있습니다"**라고 해석하여 답변. |
| **실패 (Fail)** | `09_case1_이미지추출_실패.md` | CSV/MD | `아래 차트는 이미지로...` (이미지 없음) <br> -> **"차트가 있다고 하는데 글자밖에 안 보여서 내용을 모르겠습니다."**라고 답변. |

