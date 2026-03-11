import pdfplumber
import os
import pandas as pd

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/06_case1_복합문서.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/06_case1_복합문서_성공.md")
    
    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
        return
        
    full_md = "# [Document Success] 06_case1_복합문서 - Zone Analysis\n\n"
    full_md += "### ✅ RAG 최적화 분석\n"
    full_md += "- **전략**: 문서의 기하학적 구조(Geometry)를 분석하여 '다단 - 표 - 본문' 영역을 분리(Zone Splitting).\n"
    full_md += "- **효과**: 표 데이터는 Markdown Table로 보존하고, 본문의 흐름은 논리적으로 재조립하여 문맥 파괴 방지.\n\n"
    full_md += "---\n"
    full_md += "### 📄 정제된 텍스트 결과\n\n"
    
    try:
        with pdfplumber.open(input_pdf) as pdf:
            for i, page in enumerate(pdf.pages):
                width = page.width
                height = page.height
                
                # 1. Header/Footer 좌표 (절대 좌표)
                # Header: 0 ~ 50
                # Footer: height-50 ~ height
                # Main Body: 50 ~ height-50
                
                main_bbox = (0, 50, width, height - 50)
                main_area = page.crop(main_bbox)
                
                # 2. Table Extraction
                # find_tables는 main_area 내부에서의 좌표를 리턴하는가? 
                # 아니다. pdfplumber는 보통 절대 좌표(page 기준)를 씀.
                tables = main_area.find_tables()
                table_bboxes = [t.bbox for t in tables]
                
                table_texts = []
                if tables:
                    extracted = main_area.extract_tables()
                    for table_data in extracted:
                        if table_data:
                            df = pd.DataFrame(table_data[1:], columns=table_data[0])
                            df = df.fillna("")
                            table_texts.append(df.to_markdown(index=False))
                
                # 3. Text Filtering
                def not_inside_tables(obj):
                    x = obj["x0"]
                    # obj["top"]은 절대 좌표임.
                    y = obj["top"]
                    for bbox in table_bboxes:
                        if (bbox[0]-5 <= x <= bbox[2]+5) and (bbox[1]-5 <= y <= bbox[3]+5):
                            return False
                    return True
                
                # 4. Layout Analysis (Zone 나누기 - 절대 좌표 기준)
                if table_bboxes:
                    # 첫 번째 표의 상단/하단 좌표 (절대 좌표)
                    table_top = table_bboxes[0][1]
                    table_bottom = table_bboxes[0][3]
                else:
                    table_top = height - 50
                    table_bottom = 50
                
                # Zone A: Top (본문 상단)
                # 범위: (0, 50) ~ (width, table_top)
                # 단, table_top이 50보다 작으면 에러나므로 체크
                if table_top > 50:
                    zone_a_bbox = (0, 50, width, table_top)
                    zone_a = page.crop(zone_a_bbox)
                    
                    # 다단 분리
                    mid = width / 2
                    col_left_bbox = (0, 50, mid, table_top)
                    col_right_bbox = (mid, 50, width, table_top)
                    
                    # page.crop을 써야 함 (main_area.crop 아님)
                    col_left = page.crop(col_left_bbox).filter(not_inside_tables).extract_text() or ""
                    col_right = page.crop(col_right_bbox).filter(not_inside_tables).extract_text() or ""
                    
                    full_md += "## [Section 1] Intro & Columns\n"
                    full_md += col_left + "\n\n" + col_right + "\n\n"
                
                # Zone B: Table (이미 추출함)
                if table_texts:
                    full_md += "## [Section 2] Strategic Roadmap (Table)\n"
                    for t_md in table_texts:
                        full_md += t_md + "\n\n"
                
                # Zone C: Bottom (본문 하단)
                # 범위: (0, table_bottom) ~ (width, height - 50)
                if table_bottom < height - 50:
                    zone_c_bbox = (0, table_bottom, width, height - 50)
                    zone_c = page.crop(zone_c_bbox)
                    bottom_text = zone_c.filter(not_inside_tables).extract_text() or ""
                    
                    full_md += "## [Section 3] Analysis & Architecture\n"
                    full_md += bottom_text + "\n\n"
                
        with open(output_md, "w") as f:
            f.write(full_md)
        print(f"✅ 성공 결과 생성: {output_md}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
