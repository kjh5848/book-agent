"""
[실습 4 - AI 기반 지능형 정제 (Vision/LLM)]
규칙 기반으로 추출하기 어려운 슬라이드형 PDF나 이미지 문서를 
로컬 LLM (Ollama/DeepSeek-R1 등) API를 호출하여 마크다운으로 완벽히 정제합니다.

* 주의: 본 스크립트는 로컬에 Ollama API가 실행 중임을 가정합니다.
"""
import os
import requests
import json
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDF = os.path.join(BASE_DIR, '../../data/docs/ops/OPS_운영보고서_v1.0.pdf')
INPUT_IMG = os.path.join(BASE_DIR, '../../data/docs/ops/OPS_매출추이_v1.0.png')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/success_results/04_OPS_복합파싱_success.md')

def refine_with_llm(raw_text, model="deepseek-r1"):
    print(f"🤖 LLM에게 정제 요청 중... (모델: {model})")
    prompt = f"""당신은 전문 문서 편집가입니다. 아래의 거친 텍스트를 논리적인 마크다운으로 깔끔하게 정제하세요.
    
    [원본 텍스트]
    {raw_text}
    """
    
    # Ollama Local API 호출 (타임아웃 및 에러 처리 생략된 간략화 버전)
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "응답 없음")
    except Exception as e:
        return f"> ⚠️ LLM 호출 실패 (Ollama가 실행 중인지 확인하세요): {e}\n\n[원본 임시 텍스트]\n{raw_text}"

def process_complex_docs():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    md_content = ["# 운영(Ops) 부서 AI 정제 결과\n"]
    
    # 1. 프레젠테이션 PDF (텍스트 박스가 뒤섞인 형태)
    if os.path.exists(INPUT_PDF):
        import pdfplumber
        print(f"\n📄 복합 PDF 로드: {os.path.basename(INPUT_PDF)}")
        raw_text = ""
        with pdfplumber.open(INPUT_PDF) as pdf:
            for page in pdf.pages:
                raw_text += page.extract_text() + "\n"
        
        # LLM에게 서식 붕괴 텍스트 복원을 요청
        refined_md = refine_with_llm(raw_text)
        md_content.append("## 신규서비스 런칭전략 (PDF -> 마크다운 복원)\n")
        md_content.append(refined_md + "\n")

    # 2. 이미지 차트 (VLM 활용 가정)
    if os.path.exists(INPUT_IMG):
         md_content.append("\n## 매출현황 차트 설명 (이미지 -> 텍스트)\n")
         md_content.append("> 💡 [실습 팁] 실제 환경에서는 이 부분에 Vision LLM (예: llava) 모델을 사용하여\n> 이미지를 base64로 인코딩한 뒤 분석을 요청하여 매출 막대그래프의 수치를 마크다운 표로 받아옵니다.\n")
         
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"✅ 마크다운 변환 완료: {os.path.basename(OUTPUT_FILE)}")

if __name__ == "__main__":
    process_complex_docs()
