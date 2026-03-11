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
    
    model_name = os.getenv("LLM_MODEL_NAME", "gpt-4o")
    print(f"🚀 [VLM DEBUG] Using model: {model_name}")
    
    response = client.chat.completions.create(
        model=model_name,
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
    res_content = response.choices[0].message.content
    if not res_content:
        print("⚠️ [VLM DEBUG] Empty response received. Retrying with gpt-4o...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
            max_completion_tokens=3000,
        )
        res_content = response.choices[0].message.content
    return res_content

def main():
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case1_차트.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case1_차트_성공.md")
    
    print(f"🚀 [VLM API] 차트 시각 자료 분석 요청 중...")
    
    prompt = """이 이미지는 데이터 시각화 차트입니다.
다음 항목에 따라 정밀 분석해주세요:
1. **차트 개요**: 차트의 제목과 목적
2. **데이터 구조화**: 주요 수치를 Markdown Table 형식으로 변환 (X축, Y축, 값)
3. **인사이트**: 데이터에서 읽어낼 수 있는 핵심 트렌드 및 제언

반드시 마크다운 형식을 준수하여 작성해 주세요."""

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 05_case1_차트 - Visual Data Extraction\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: `GPT-4o Vision`을 활용하여 '이미지(Chart)'를 '구조화된 테이블(Table)'과 '해석(Insight)'으로 변환.\n")
            f.write("- **효과**: 검색 엔진이 수치 데이터(Table)와 의미적 맥락(Text)을 동시에 인덱싱하여, 분석적 질의에 답변 가능.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ 차트 분석 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
