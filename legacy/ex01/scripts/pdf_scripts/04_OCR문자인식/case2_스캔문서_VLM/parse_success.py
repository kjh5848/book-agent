import os
import fitz
import base64
import io
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# .env 로드 (프로젝트 루트의 .env 참조)
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
    
    # PDF 1페이지를 이미지로 변환
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
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case2_스캔문서_VLM.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case2_스캔문서_VLM_성공.md")
    
    print(f"🚀 [VLM API] 왜곡 문서 분석 요청 중...")
    
    prompt = """이 문서는 심하게 왜곡되고 구겨진 계약서 스캔본입니다. 
다음 정보를 문서에서 찾아 상세히 분석해주세요:
1. 문서의 공식 제목
2. 파트너십을 체결하는 두 회사의 이름
3. 계약서에 명시된 주요 조항 3가지 요약
4. 하단에 서명한 사람의 이름과 날짜

결과는 마크다운 형식을 사용하여 구조적으로 작성해주세요."""

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 04_case2_스캔문서_VLM - Why VLM?\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: `GPT-4o Vision` 모델에 이미지를 직접 주입하여 OCR 단계를 건너뛰고 의미(Context)를 바로 추출.\n")
            f.write("- **효과**: 구겨지거나 회전된 텍스트도 문맥적으로 완벽하게 복원하여 구조화된 데이터(Markdown)로 변환.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ VLM 분석 완료 및 저장: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
