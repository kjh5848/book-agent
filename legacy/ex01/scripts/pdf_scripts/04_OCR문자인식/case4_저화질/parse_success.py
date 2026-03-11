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
    
    if not res_content or len(res_content.strip()) == 0:
        print("⚠️ [VLM DEBUG] Empty response. Retrying with gpt-4o...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
            max_completion_tokens=3000,
        )
        res_content = response.choices[0].message.content
        
    return res_content

def main():
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case4_저화질.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case4_저화질_성공.md")
    
    print(f"🚀 [VLM API] 저화질/노이즈 문서 분석 요청 중...")
    
    prompt = "이 문서는 화질이 낮고 노이즈가 많습니다. 문맥을 고려하여 문서에 적힌 내용을 최대한 정확하게 판독하고 요약해주세요."

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 04_case4_저화질 - Generative Correction 결과\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: 뭉개진 픽셀(Low Res)을 AI가 문맥적으로 '다시 그리기(Re-generation)'하여 텍스트 복원.\n")
            f.write("- **효과**: 팩스나 구형 스캐너로 이미지화된 문서에서도 오타 없는 깨끗한 텍스트 확보.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ 저화질 문서 분석 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
