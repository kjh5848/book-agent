import pdfplumber
import os
import numpy as np

def parse_only_table():
    """
    특정 좌표 하드코딩 없이, 텍스트의 분포를 분석하여 
    열(Column)의 경계를 자동으로 찾아내는 범용 표 파서입니다.
    """
    input_pdf = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag/실습용/ex01/data/docs/ex_pdf/02_case1_투명표.pdf"
    output_md = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag/실습용/ex01/data/processed/02_case1_투명표_성공.md"
    
    print(f"🚀 범용 표 파싱 시작(Success): {input_pdf}")
    
    if not os.path.exists(input_pdf):
        print(f"❌ PDF 파일이 존재하지 않습니다: {input_pdf}")
        return

    with pdfplumber.open(input_pdf) as pdf:
        full_markdown = ""
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words: continue

            # 1. 동적 열 경계선 감지 (Dynamic Column Detection)
            x_min = int(min(w['x0'] for w in words))
            x_max = int(max(w['x1'] for w in words))
            
            shadow = np.zeros(x_max + 1)
            for w in words:
                shadow[int(w['x0']):int(w['x1'])] = 1
            
            gutters = []
            in_gutter = False
            gutter_start = 0
            for x in range(x_min, x_max + 1):
                if shadow[x] == 0 and not in_gutter:
                    gutter_start = x
                    in_gutter = True
                elif shadow[x] == 1 and in_gutter:
                    if x - gutter_start > 5:
                        gutters.append((gutter_start + x) / 2)
                    in_gutter = False
            
            print(f"📊 감지된 열 구분선 좌표: {gutters}")

            # 2. 행(Row) 그룹화 (Y-Clustering)
            words.sort(key=lambda w: w['top'])
            rows_words = []
            if words:
                current_row = [words[0]]
                for i in range(1, len(words)):
                    if words[i]['top'] - current_row[0]['top'] <= 8:
                        current_row.append(words[i])
                    else:
                        rows_words.append(current_row)
                        current_row = [words[i]]
                rows_words.append(current_row)

            # 3. 데이터 배치
            grid_table = []
            num_cols = len(gutters) + 1
            
            for row_words in rows_words:
                row_data = [[] for _ in range(num_cols)]
                for w in row_words:
                    mid_x = (w['x0'] + w['x1']) / 2
                    col_idx = 0
                    for g in gutters:
                        if mid_x > g:
                            col_idx += 1
                        else:
                            break
                    row_data[col_idx].append(w['text'])
                
                grid_table.append([" ".join(cell) for cell in row_data])

            # 4. 마크다운 표 생성
            if not grid_table: continue
            
            headers = grid_table[0]
            separator = ["---"] * len(headers)
            
            md_table = f"| {' | '.join(headers)} |\n"
            md_table += f"| {' | '.join(separator)} |\n"
            
            for row in grid_table[1:]:
                if any(row):
                    md_table += f"| {' | '.join(row)} |\n"
            
            full_markdown += md_table + "\n\n"

    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [범용 표 추출 결과] 02_case1_투명표\n\n")
        f.write("> [!NOTE]\n> 본 결과는 텍스트 분포 분석을 통해 동적으로 추출되었습니다.\n\n")
        f.write(full_markdown.strip())
    
    print(f"✅ 파싱 완료: {output_md}")

if __name__ == "__main__":
    parse_only_table()
