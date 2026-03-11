import requests
import json
import os
import fitz  # PyMuPDF
from datetime import datetime

def refine_pdf_to_md_with_ai(pdf_path, output_md, model="deepseek-r1"):
    """
    [2단계 파이프라인] 
    1. PDF에서 Raw Text를 직접 추출합니다.
    2. 추출된 텍스트를 AI(LLM)에게 전달하여 표준 마크다운으로 최종 정제합니다.
    """
    print(f"🚀 AI 지식 정제 파이프라인 가동: {pdf_path}")
    print("  Step 1: PDF에서 텍스트 추출 중...")

    if not os.path.exists(pdf_path):
        print(f"❌ 에러: PDF 파일을 찾을 수 없습니다. (경로: {pdf_path})")
        return

    # 1. PDF에서 Raw Text 추출
    try:
        doc = fitz.open(pdf_path)
        raw_text = ""
        for page in doc:
            raw_text += page.get_text() + "\n"
        doc.close()
    except Exception as e:
        print(f"❌ PDF 추출 실패: {str(e)}")
        return

    # 2. AI에게 보낼 상세 프롬프트 구성
    print("  Step 2: AI(LLM)를 통한 지능형 마크다운 정제 중 (시간이 소요될 수 있습니다)...")
    prompt = f"""
    당신은 전문 문서 편집가입니다. 아래의 PDF에서 추출된 지저분한 텍스트(Raw Text)를 
    가장 완벽한 'AI용 표준 마크다운'으로 변환해 주세요.

    [작업 지침]
    1. 문서 파일명({os.path.basename(pdf_path)})과 현재 날짜({datetime.now().strftime('%Y-%m-%d')})를 기반으로 YAML 메타데이터를 상단에 추가하세요.
    2. 제목 위계(#, ##, ###)를 논리적으로 구성하세요.
    3. 줄바꿈이 깨진 문장을 자연스럽게 연결하세요.
    4. 표(Table) 형태가 보인다면 마크다운 표 형식으로 복구하세요.
    5. 불필요한 페이지 번호나 특수문자는 제거하세요.

    [원본 데이터]
    {raw_text}
    
    [출력 형식]
    마크다운 코드만 출력해 주세요.
    """

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        refined_md = response.json().get("response", "")

        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(refined_md)

        print(f"✅ AI 표준화 완료: {output_md}")
        print("-" * 50)
        print(refined_md[:500] + "...") # 요약 출력
        print("-" * 50)

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")

if __name__ == "__main__":
    # PDF 파일을 입력으로 직접 사용합니다.
    input_pdf = "data/metacoding_사내_규정_및_정책.pdf"
    output_md = "parsed_data/ai_standard_policy.md"
    
    refine_pdf_to_md_with_ai(input_pdf, output_md)
