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
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case2_플로우차트.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case2_플로우차트_성공.md")
    
    print(f"🚀 [VLM API] 플로우차트 분석 요청 중 (Enterprise AI Workflow)...")
    
    prompt = """이 이미지는 'Enterprise AI Governance Workflow'를 나타내는 플로우차트입니다.
다음 항목에 따라 논리적 흐름을 재구성해주세요:
1. **프로세스 개요**: 워크플로우의 시작과 끝, 그리고 전체 목적
2. **논리적 경로(Path Tracing)**: 데이터 입력부터 최종 승인까지의 단계를 순서대로 서술 (1. -> 2. -> 3.)
3. **분기점 분석**: 'Quality Check'나 'Feedback Loop' 등 조건부 분기가 일어나는 지점의 역할 설명

반드시 마크다운 리스트 형식을 사용하여 프로세스를 선형화해 주세요."""

    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_pdf}")
            
        analysis_result = analyze_vlm(input_pdf, prompt)
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# [Document Success] 05_case2_플로우차트 - Logic Reconstruction\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: `GPT-4o Vision`에게 복잡한 화살표와 다이어그램을 '선형적인 텍스트(Sequence)'로 변환 요청.\n")
            f.write("- **효과**: 비선형적인 차트 구조를 논리적 텍스트로 풀어내어, '단계별 프로세스'에 대한 질의응답(Q&A) 가능.\n\n")
            f.write("---\n")
            f.write(f"### 📄 정제된 텍스트 결과 (Markdown)\n\n")
            f.write(analysis_result)
            
        print(f"✅ 플로우차트 분석 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ VLM 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
