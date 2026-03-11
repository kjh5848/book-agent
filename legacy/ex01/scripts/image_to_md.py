import requests
import json
import base64
import os
from datetime import datetime

def generate_image_markdown(image_path, output_md, model="llava"):
    """
    이미지를 분석하여 마크다운 파일로 저장합니다.
    """
    print(f"🖼️ 이미지 마크다운 생성 시작: {image_path}")

    if not os.path.exists(image_path):
        print("❌ 에러: 이미지를 찾을 수 없습니다.")
        return

    # 1. Base64 인코딩
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # 2. Ollama LLaVA 호출
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": """You are an expert data analyst specializing in Multimodal AI.
        Analyze the provided image (chart/diagram) with extreme precision and generate a technical report in Markdown.
        
        ### [Analysis Requirements]
        1. **Identity**: Identify the chart title, type (e.g., bar, line, pie), and overall purpose.
        2. **Axis & Legends**: Detail the X-axis (time/categories), Y-axis (units/values), and any legends/colors.
        3. **Data Extraction**: Extract specific numerical values for each category or time point.
        4. **Trend Analysis**: Describe the growth, decline, or key findings (e.g., peak performance, anomalies).
        
        ### [Strict Output Format]
        Your response MUST follow this Markdown structure:
        
        ### 🇰🇷 [Korean]
        - **이미지 제목 및 유형**: (제목 및 차트 종류 설명)
        - **데이터 요약**:
            * (핵심 수치 1): **값**
            * (핵심 수치 2): **값**
        - **트렌드 분석**: (전체적인 경향성 설명)
        
        ### 🇺🇸 [English]
        - **Title & Type**: (Description of title and chart type)
        - **Data Summary**:
            * (Key Point 1): **Value**
            * (Key Point 2): **Value**
        - **Trend & Insight**: (Detailed analysis and findings)
        
        Do not use conversational fillers. Output only the Markdown content.""",
        "images": [encoded_string],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        description = response.json().get("response", "")

        # 3. 마크다운 내용 구성 (메타데이터 포함)
        file_name = os.path.basename(image_path)
        
        # 이미지 파일의 상대 경로 계산 (parsed_data에서 data로 이동)
        # 보통 output_md는 parsed_data/ 폴더 안에 있으므로 ../data/ 형식이 필요함
        rel_image_path = os.path.join("..", image_path)

        markdown_content = f"""---
title: Image Description - {file_name}
type: multi-modal-caption
source_image: {image_path}
date: {datetime.now().strftime("%Y-%m-%d")}
---

# 이미지 분석 결과: {file_name}

![원본 이미지]({rel_image_path})

## 🔍 AI 분석 내용
{description}

> **Note**: 이 문서는 LLaVA 모델을 통해 생성된 시각 자료의 텍스트 설명본입니다.
"""

        # 4. 저장
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"✅ 이미지 지식화 완료: {output_md}")
        print("-" * 50)
        print(markdown_content)
        print("-" * 50)

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")

if __name__ == "__main__":
    sample_image = "data/metacoding_sales_statement.png"
    output_path = "parsed_data/chart_description.md"
    
    generate_image_markdown(sample_image, output_path)
