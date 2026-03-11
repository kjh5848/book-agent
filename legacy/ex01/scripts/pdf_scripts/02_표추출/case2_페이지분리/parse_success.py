import pdfplumber
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/02_case2_페이지분리.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case2_페이지분리_성공.md")
    
    headers = None
    full_text = "# [문서 처리 성공] 02_case2_페이지분리 - 헤더 병합(Header Merge) 결과\n\n"
    full_text += "### RAG 최적화 분석\n"
    full_text += "- **전략**: 첫 페이지의 헤더를 캐싱(Caching)하여 헤더가 없는 다음 페이지 표에 강제 주입.\n"
    full_text += "- **효과**: 모든 페이지의 데이터가 정확한 컬럼(Key)과 매핑되어 검색 정확도 향상.\n\n"
    full_text += "---\n"
    full_text += "### 정제된 텍스트 결과 (Markdown)\n\n"
    
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                # 첫 페이지에서 헤더 발견 시 저장
                if page.page_number == 1:
                    headers = table[0]
                    content_rows = table[1:]
                else:
                    # 두 번째 페이지부터는 헤더가 없으면 저장된 헤더 사용
                    content_rows = table
                
                # 마크다운 변환 (헤더가 있으면 사용)
                if headers:
                    md_table = f"### Page {page.page_number}\n"
                    md_table += "| " + " | ".join([str(c) for c in headers]) + " |\n"
                    md_table += "| " + " | ".join(["---" for _ in headers]) + " |\n"
                    for row in content_rows:
                        # None 값 처리
                        row_data = [str(c).replace('\n', ' ') if c else "" for c in row]
                        # 열 개수가 맞는지 확인 (헤더 개수만큼)
                        if len(row_data) < len(headers):
                             row_data += [""] * (len(headers) - len(row_data))
                        md_table += "| " + " | ".join(row_data) + " |\n"
                    full_text += md_table + "\n\n"
            
    with open(output_md, "w") as f:
        f.write(full_text)
    print(f"성공 결과 생성 완료: {output_md}")

if __name__ == "__main__":
    main()
