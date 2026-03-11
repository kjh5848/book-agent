import os
import fitz
import base64
import io
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# .env 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../../../.env")
load_dotenv(env_path)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_vlm(pdf_path, prompt):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OLLAMA_BASE_URL") if os.getenv("LLM_PROVIDER") == "ollama" else None
    )
    
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_bytes = pix.tobytes("png")
    doc.close()
    
    base64_image = encode_image(img_bytes)
    
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL_NAME", "gpt-4o"),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_completion_tokens=3000,
    )
    return response.choices[0].message.content

def main():
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case3_복합범례.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case3_복합범례_성공.md")
    
    print(f"🚀 [VLM API] 복합 범례 차트 분석 요청 중 (Tech Market Forecast)...")
    
    prompt = """이 차트는 12개 주요 테크 기업의 2024-2030년 시장 점유율 예측치입니다.
다음 시각적 특징을 활용하여 데이터를 정확히 매핑해주세요:
1. **범례 매핑(Legend Matching)**: (색상/선모양) - (기업명)을 정확히 연결
2. **트렌드 분석**: 2030년 예상 점유율 Top 3 기업과 그 이유
3. **데이터 추출**: 각 기업의 연도별 추정치를 Markdown Table로 정리

반드시 색상과 범례를 교차 검증(Cross-Referencing)하여 데이터를 작성해주세요."""

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 05_case3_복합범례 - Visual Cross-Referencing\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: `GPT-4o Vision`에게 색상-범례-그래프 선을 상호 참조하여 데이터를 추출하도록 지시.\n")
            f.write("- **효과**: 10개 이상의 복잡한 데이터가 겹쳐 있어도, 시각적 차이를 인지하여 정확한 데이터 매핑 가능.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ 차트 분석 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
