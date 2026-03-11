import pdfplumber
import os
import pandas as pd

def parse_complex_pdf(pdf_path, output_path):
    print(f"🧐 [Premium] 복합 레이아웃 파싱 시작: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return

    all_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            cached_header = None
            
            for i, page in enumerate(pdf.pages):
                page_content = [f"## Page {i+1}\n"]
                
                width = page.width
                # 프리미엄 디자인에 맞춰 영역 조정 (본문 약 70%, 사이드바 30%)
                main_region = (0, 0, width * 0.72, page.height)
                sidebar_region = (width * 0.72, 0, width, page.height)
                
                main_text = page.within_bbox(main_region).extract_text()
                sidebar_text = page.within_bbox(sidebar_region).extract_text()
                
                tables = page.extract_tables({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 5,
                    "join_tolerance": 5
                })
                
                if tables:
                    for table in tables:
                        df = pd.DataFrame(table)
                        df = df.dropna(how='all').fillna("")
                        
                        if i > 0 and cached_header and len(df.columns) == len(cached_header):
                            # 연속표 헤더 복구
                            if not any(str(cached_header[0]) in str(cell) for cell in df.iloc[0]):
                                df.columns = cached_header
                        else:
                            if not df.empty:
                                cached_header = df.iloc[0].tolist()
                                df.columns = cached_header
                                df = df[1:]
                        
                        md_table = df.to_markdown(index=False)
                        page_content.append("\n### [Data Table]\n")
                        page_content.append(md_table + "\n")
                
                if main_text:
                    page_content.append("\n### [Narrative Content]\n")
                    page_content.append(main_text + "\n")
                
                if sidebar_text and sidebar_text.strip():
                    page_content.append("\n> [Contextual Note]\n")
                    page_content.append(sidebar_text.replace("\n", " ") + "\n")
                    
                all_content.append("".join(page_content))

        # 결과 저장
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# FUTURE WORKSPACE 2026: INNOVATION REPORT (Extracted)\n\n")
            f.write("\n\n---\n\n".join(all_content))
        
        print(f"✅ 프리미엄 파싱 완료: {output_path}")

    except Exception as e:
        print(f"❌ 파싱 중 오류 발생: {e}")

if __name__ == "__main__":
    # 고정된 절대 경로 사용
    project_root = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag"
    input_pdf = os.path.join(project_root, "실습용/ex01/data/docs/ex_pdf/06_case2_복합보고서.pdf")
    output_md = os.path.join(project_root, "실습용/ex01/data/processed/06_case2_복합보고서_성공.md")
    
    parse_complex_pdf(input_pdf, output_md)
