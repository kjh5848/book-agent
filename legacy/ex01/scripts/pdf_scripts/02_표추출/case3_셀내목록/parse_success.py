import pdfplumber
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/02_case3_셀내목록.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case3_셀내목록_성공.md")
    
    full_md = "# [문서 처리 성공] 02_case3_셀내목록 - 줄바꿈(Line Break) 치환 결과\n\n"
    full_md += "### RAG 최적화 분석\n"
    full_md += "- **전략**: 셀 내부 줄바꿈(`\n`)을 HTML 태그 `<br>`로 치환.\n"
    full_md += "- **효과**: 마크다운 테이블 형식이 깨지지 않고, LLM이 셀 내부의 다중 항목을 온전히 인식함.\n\n"
    full_md += "---\n"
    full_md += "### 정제된 텍스트 결과 (Markdown)\n\n"
    
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                md_table = "| " + " | ".join([str(c) for c in table[0]]) + " |\n"
                md_table += "| " + " | ".join(["---" for _ in table[0]]) + " |\n"
                for row in table[1:]:
                    # 셀 내부의 줄바꿈(\n)을 <br> 태그로 변환하여 마크다운 테이블 깨짐 방지
                    row_data = [str(c).replace('\n', '<br>') if c else "" for c in row]
                    md_table += "| " + " | ".join(row_data) + " |\n"
                full_md += md_table + "\n\n"
            
    with open(output_md, "w") as f:
        f.write(full_md)
    print(f"성공 결과 생성 완료: {output_md}")

if __name__ == "__main__":
    main()
