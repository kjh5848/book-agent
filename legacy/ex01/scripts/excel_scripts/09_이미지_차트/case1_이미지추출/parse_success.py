import pandas as pd
from openpyxl import load_workbook
import os
import io
from PIL import Image as PilImage

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "09_case1_이미지추출.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "09_case1_이미지추출_성공.json")
extracted_img_dir = os.path.join(output_dir, "images")
os.makedirs(extracted_img_dir, exist_ok=True)

print(f"Reading {input_file}...")

# 1. Pandas Load
df = pd.read_excel(input_file)
# ... standard pandas load code ...

# 2. Openpyxl Image Extraction
wb = load_workbook(input_file)
ws = wb.active

images_found = []
if hasattr(ws, '_images') and ws._images:
    print(f"Found {len(ws._images)} images.")
    for i, img in enumerate(ws._images):
        img_name = f"extracted_image_{i+1}.png"
        save_path = os.path.join(extracted_img_dir, img_name)
        
        try:
            # img.ref가 BytesIO인지, 파일 경로인지, PIL Image인지 확인
            # openpyxl 버전에 따라 다를 수 있음.
            # 가장 안전한 방법: img.ref가 바이트 스트림이면 PIL로 열어서 저장
            
            img_data = None
            if hasattr(img, 'ref'):
                if isinstance(img.ref, io.BytesIO):
                    img_data = img.ref
                elif hasattr(img.ref, 'read'): # file-like
                    img_data = img.ref
            
            if img_data:
                # 바이트 스트림을 PIL로 열어서 저장
                pil_image = PilImage.open(img_data)
                pil_image.save(save_path)
                print(f"  -> Saved image to {img_name}")
                
                # 메타데이터 기록
                # anchor (위치) 정보 추출 시 str() 변환 에러 방지
                # 간단히 좌표 추정 (TwoCellAnchor의 경우 _from 사용)
                anchor_info = "Unknown Location"
                try:
                    if hasattr(img.anchor, '_from'):
                         col = img.anchor._from.col
                         row = img.anchor._from.row
                         anchor_info = f"Col:{col}, Row:{row}"
                except:
                    pass
                
                images_found.append({
                    "path": save_path,
                    "location": anchor_info
                })
            else:
                print(f"  -> Skipping image {i+1}: No valid data ref found.")

        except Exception as e:
            print(f"  -> Error saving image {i+1}: {e}")
            images_found.append({"error": str(e)})
else:
    print("No images found.")

# Save to Markdown
md_output = os.path.join(output_dir, "09_case1_이미지추출_성공.md")
with open(md_output, "w", encoding="utf-8") as f:
    f.write("# [Document Success] 09_case1_이미지추출 - Image Extraction\n\n")
    f.write("### ✅ RAG 최적화 분석\n")
    f.write("- **전략**: 엑셀 내 이미지(차트)를 추출하여 `![Image](path)` 형태로 문서화.\n")
    f.write("- **효과**: 텍스트만으로는 알 수 없는 시각적 정보(추세, 패턴)를 Vision LLM이 해석할 수 있도록 함.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n\n")
    
    if images_found:
        f.write("**Extracted Images:**\n\n")
        for img in images_found:
            # Markdown Image Link: ![Alt](path)
            # path should be relative to the markdown file.
            # images are in "images/" subfolder relative to output_dir.
            rel_path = os.path.join("images", os.path.basename(img['path']))
            f.write(f"#### Image: {os.path.basename(img['path'])}\n")
            f.write(f"- **Location**: {img['location']}\n")
            f.write(f"![Chart]({rel_path})\n\n")
    else:
        f.write("(No images found)\n")

print(f"  -> Saved to {os.path.basename(md_output)}")
