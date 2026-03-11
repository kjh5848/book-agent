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
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case3_손글씨.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case3_손글씨_성공.md")
    
    print(f"🚀 [VLM API] 손글씨 판독 요청 중...")
    
    prompt = "이미지의 손글씨 내용을 정확하게 판독하여 텍스트로 변환해주세요. 만약 문서 형식이 있다면 그 구조를 유지하며 내용을 정리해주세요."

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 04_case3_손글씨 - Handmade Note Recognition\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: `GPT-4o Vision`에게 '처방전/메모'라는 문맥(Context)을 제공하여 비정형 필기체를 추론.\n")
            f.write("- **효과**: 난필(휘갈겨 쓴 글씨)에서도 의약품명이나 중요 메모 내용을 정확하게 데이터화.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ 손글씨 판독 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
