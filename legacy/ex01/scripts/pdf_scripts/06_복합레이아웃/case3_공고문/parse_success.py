import pdfplumber
import os
import pandas as pd
import glob

def parse_government_announcement(pdf_path, output_path):
    print(f"🧐 [Government] 공고문 정밀 파싱 시작: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return

    all_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_content = [f"## Page {i+1}\n"]
                
                # [Strategy] 공고문은 표 안에 중요 내용(지원 자격, 지원 내역)이 많음.
                # 텍스트와 표를 분리하여 추출하되, 표의 레이아웃을 최대한 보존.
                
                # 1. 텍스트 추출 로직 (표 제외)
                # find_tables로 표 영역 확보
                tables = page.find_tables()
                table_bboxes = [t.bbox for t in tables]
                
                def is_not_in_table(obj):
                    # 표 경계(bbox) 외부에 있는 것만 추출
                    x = obj.get("x0", 0)
                    y = obj.get("top", 0)
                    for bbox in table_bboxes:
                        if (bbox[0]-2 <= x <= bbox[2]+2) and (bbox[1]-2 <= y <= bbox[3]+2):
                            return False
                    return True

                # 본문 정렬 추출
                main_text = page.filter(is_not_in_table).extract_text()
                
                # 2. 표 추출 및 마크다운 변환
                if tables:
                    # 공고문은 표 선이 굵고 명확하므로 lines 설정
                    extracted_tables = page.extract_tables({
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                    })
                    
                    for table_idx, table_data in enumerate(extracted_tables):
                        if not table_data: continue
                        
                        # 데이터프레임 변환 및 정제
                        df = pd.DataFrame(table_data)
                        df = df.dropna(how='all').fillna("")
                        
                        # 공고문 표는 첫 줄이 헤더인 경우가 많음
                        if not df.empty and len(df) > 1:
                            df.columns = df.iloc[0]
                            df = df[1:]
                        
                        try:
                            md_table = df.to_markdown(index=False)
                        except:
                            md_table = df.to_string(index=False)
                            
                        page_content.append(f"\n### [Table {table_idx+1}]\n")
                        page_content.append(md_table + "\n")
                
                # 3. 본문 텍스트 추가
                if main_text:
                    page_content.append("\n### [General Text]\n")
                    page_content.append(main_text + "\n")
                
                all_content.append("".join(page_content))

        # 결과 저장
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# [Success] 2026 제도전성공패키지 모집공고 RAG 정제 결과\n\n")
            f.write("> **전략**: 공공기관 공고문의 특성에 따라 표(Table)와 본문 텍스트를 명확히 격리 추출하여 LLM 검색 효율을 극대화함.\n\n")
            f.write("\n\n---\n\n".join(all_content))
        
        print(f"✅ 공고문 파싱 완료: {output_path}")

    except Exception as e:
        print(f"❌ 파싱 중 오류 발생: {e}")

if __name__ == "__main__":
    import glob
    project_root = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag"
    pdf_dir = os.path.join(project_root, "실습용/ex01/data/docs/ex_pdf")
    
    # 공고문 파일명에 특수문자/인코딩 문제가 있을 수 있으므로 패턴으로 찾기
    search_pattern = os.path.join(pdf_dir, "06_case3_복합*.pdf")
    found_files = glob.glob(search_pattern)
    
    if not found_files:
        print(f"❌ PDF 파일을 찾을 수 없습니다: {search_pattern}")
    else:
        input_pdf = found_files[0]
        output_md = os.path.join(project_root, "실습용/ex01/data/processed/06_case3_공고문_성공.md")
        parse_government_announcement(input_pdf, output_md)
