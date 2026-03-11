import os
import re

file_path = "0_generate_mock_docs.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix create_hr_rules_pdf paths
hr_rules = """def create_hr_rules_pdf():
    html_path = os.path.join(BASE_DIR, 'hr', 'HR_취업규칙_v1.0.html')
    pdf_path = os.path.join(BASE_DIR, 'hr', 'HR_취업규칙_v1.0.pdf')
    
    template_path = '/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag/실습용/ex01/docs/html/HR_사내규정_다단.html'
    with open(template_path, 'r', encoding='utf-8') as tf:
        html_content = tf.read()
    
    html_content = html_content.replace('사내 인사 규정 (발췌)', '취업규칙 (다단 편집형)')
    html_content = html_content.replace('Metacoding Inc.', '이노베이션 주식회사')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    html_to_pdf_playwright(html_path, pdf_path)
    print(f"생성 완료: {pdf_path}")
"""
content = re.sub(r"def create_hr_rules_pdf\(\):.*?(?=def create_fin_sales_excel)", hr_rules, content, flags=re.DOTALL)

# Fix create_hr_security_scan_pdf paths
new_main = """def create_hr_security_scan_pdf():
    html_path = os.path.join(BASE_DIR, 'hr', 'HR_정보보안서약서.html')
    pdf_path = os.path.join(BASE_DIR, 'hr', 'HR_정보보안서약서.pdf')
    
    template_path = '/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag/실습용/ex01/docs/html/SEC_보안규정_스캔.html'
    with open(template_path, 'r', encoding='utf-8') as tf:
        html_content = tf.read()
    
    html_content = html_content.replace('보안 규정 지침서', '정보보안 서약서 (스캔본)')
    html_content = html_content.replace('2026-SEC-001', '2026-HR-SEC-002')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    html_to_pdf_playwright(html_path, pdf_path)
    print(f"생성 완료: {pdf_path}")

if __name__ == "__main__":
    print("--- 실무형 모의 문서 생성기 시작 ---")
    create_hr_rules_pdf()
    create_hr_security_scan_pdf()
    create_fin_sales_excel()
    create_fin_budget_excel()
    create_sec_rules_docx()
    create_ops_strategy_pdf()
    create_ops_image()
    print("--- 생성 완료 ---")
"""
content = re.sub(r"def create_hr_security_scan_pdf\(\):.*", new_main, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("File updated successfully.")
