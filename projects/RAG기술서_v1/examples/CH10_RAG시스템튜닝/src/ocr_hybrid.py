"""OCR 및 LLaVA 기반 스캔 PDF 처리 모듈입니다.

EasyOCR로 이미지에서 텍스트를 추출하고, LLaVA 비전 모델로 이미지 내용을
설명합니다. 스캔 PDF를 페이지별 이미지로 변환하여 텍스트와 이미지 설명을
함께 추출합니다.
"""

import os
import base64
import logging
from pathlib import Path

import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- 상수 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
VISION_MODEL_NAME: str = os.getenv("VISION_MODEL_NAME", "llava:7b")
OCR_LANGUAGE: list[str] = ["ko", "en"]
PDF_DPI: int = 150  # 페이지 이미지 변환 해상도


def extract_with_ocr(image_path: str) -> str:
    """EasyOCR로 이미지에서 텍스트를 추출합니다.

    EasyOCR을 사용하여 한국어와 영어 텍스트를 인식하고,
    신뢰도 0.3 이상의 결과만 줄바꿈으로 연결하여 반환합니다.

    Args:
        image_path: OCR을 적용할 이미지 파일의 절대 경로

    Returns:
        인식된 텍스트 문자열. 텍스트가 없으면 빈 문자열 반환.

    Raises:
        FileNotFoundError: 이미지 파일이 존재하지 않는 경우
        ImportError: easyocr 패키지가 설치되지 않은 경우
        RuntimeError: OCR 처리 중 예기치 않은 오류 발생 시
    """
    # --- Input ---
    if not Path(image_path).exists():
        raise FileNotFoundError(
            f"이미지 파일을 찾을 수 없습니다: {image_path}\n"
            "경로가 올바른지 확인하십시오."
        )

    try:
        import easyocr
    except ImportError as exc:
        raise ImportError(
            "easyocr 패키지가 설치되지 않았습니다. "
            "'pip install easyocr' 명령어로 설치하십시오."
        ) from exc

    # --- Process ---
    try:
        reader = easyocr.Reader(OCR_LANGUAGE, gpu=False, verbose=False)
        results = reader.readtext(image_path)
    except Exception as exc:
        raise RuntimeError(
            f"OCR 처리 중 오류가 발생했습니다: {exc}\n"
            f"이미지 파일 형식을 확인하십시오: {image_path}"
        ) from exc

    # 신뢰도 0.3 이상인 텍스트만 수집
    extracted_lines: list[str] = []
    for _bbox, text, confidence in results:
        if confidence >= 0.3 and text.strip():
            extracted_lines.append(text.strip())

    # --- Output ---
    return "\n".join(extracted_lines)


def describe_image_with_llava(image_path: str) -> str:
    """LLaVA로 이미지 내용 설명을 생성합니다. Ollama /api/generate 호출.

    이미지를 base64로 인코딩하여 Ollama LLaVA 모델에 전달하고,
    이미지에 포함된 텍스트, 도표, 그래프 등의 내용을 한국어로 설명합니다.

    Args:
        image_path: 설명을 생성할 이미지 파일의 절대 경로

    Returns:
        LLaVA가 생성한 이미지 내용 설명 문자열

    Raises:
        FileNotFoundError: 이미지 파일이 존재하지 않는 경우
        RuntimeError: Ollama LLaVA 서버 연결 실패 또는 응답 오류 시
    """
    # --- Input ---
    if not Path(image_path).exists():
        raise FileNotFoundError(
            f"이미지 파일을 찾을 수 없습니다: {image_path}\n"
            "경로가 올바른지 확인하십시오."
        )

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": VISION_MODEL_NAME,
        "prompt": (
            "이 이미지에 포함된 모든 내용을 한국어로 상세히 설명하십시오. "
            "텍스트가 있으면 그대로 추출하고, 도표나 그래프가 있으면 "
            "그 내용도 설명하십시오."
        ),
        "images": [image_b64],
        "stream": False,
    }

    # --- Process ---
    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        description: str = data.get("response", "").strip()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Ollama 서버({OLLAMA_BASE_URL})에 연결할 수 없습니다.\n"
            "Ollama가 실행 중인지 확인하십시오: 'ollama serve'"
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"LLaVA API 호출 중 HTTP 오류가 발생했습니다: {exc}\n"
            f"모델 '{VISION_MODEL_NAME}'이 설치됐는지 확인하십시오: "
            f"'ollama pull {VISION_MODEL_NAME}'"
        ) from exc
    except (KeyError, ValueError) as exc:
        raise RuntimeError(
            f"LLaVA 응답 파싱 중 오류가 발생했습니다: {exc}"
        ) from exc

    # --- Output ---
    return description


def _pdf_page_to_image(
    pdf_document: fitz.Document,
    page_number: int,
    output_dir: str,
    dpi: int = PDF_DPI,
) -> str:
    """PDF 페이지를 PNG 이미지로 변환하여 저장합니다.

    Args:
        pdf_document: 열려 있는 PyMuPDF Document 객체
        page_number: 변환할 페이지 번호 (0부터 시작)
        output_dir: 변환된 이미지를 저장할 디렉토리 경로
        dpi: 이미지 해상도 (기본값: 150)

    Returns:
        저장된 PNG 이미지 파일의 절대 경로

    Raises:
        RuntimeError: 페이지 렌더링 실패 시
    """
    # --- Input ---
    page = pdf_document[page_number]
    mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 DPI 기준 스케일 계산

    # --- Process ---
    try:
        pix = page.get_pixmap(matrix=mat)
        image_path = os.path.join(output_dir, f"page_{page_number + 1:04d}.png")
        pix.save(image_path)
    except Exception as exc:
        raise RuntimeError(
            f"PDF 페이지 {page_number + 1} 렌더링에 실패했습니다: {exc}"
        ) from exc

    # --- Output ---
    return image_path


def process_scanned_pdf(pdf_path: str) -> list[dict]:
    """스캔 PDF를 페이지별 이미지로 변환 후 OCR + LLaVA 처리합니다.

    PDF의 각 페이지를 PNG 이미지로 변환하고, EasyOCR로 텍스트를 추출하며
    LLaVA로 이미지 내용을 설명합니다. 두 결과를 결합하여 페이지별
    딕셔너리 리스트로 반환합니다.

    Args:
        pdf_path: 처리할 스캔 PDF 파일의 절대 경로

    Returns:
        페이지별 처리 결과 딕셔너리 리스트::

            [
                {
                    "page": int,           # 페이지 번호 (1부터 시작)
                    "image_path": str,     # 저장된 이미지 경로
                    "ocr_text": str,       # OCR로 추출한 텍스트
                    "llava_description": str,  # LLaVA 이미지 설명
                    "combined_text": str,  # OCR + LLaVA 결합 텍스트
                    "status": str,         # "success" 또는 "error"
                }
            ]

    Raises:
        FileNotFoundError: PDF 파일이 존재하지 않는 경우
        RuntimeError: PDF 열기 실패 시
    """
    # --- Input ---
    if not Path(pdf_path).exists():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}\n"
            "경로가 올바른지 확인하십시오."
        )

    pdf_stem = Path(pdf_path).stem
    output_dir = os.path.join("outputs", "ocr_pages", pdf_stem)
    os.makedirs(output_dir, exist_ok=True)

    try:
        pdf_doc = fitz.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(
            f"PDF 파일을 열 수 없습니다: {exc}\n"
            f"파일이 손상됐거나 PDF 형식이 아닐 수 있습니다: {pdf_path}"
        ) from exc

    total_pages = len(pdf_doc)
    print(f"\n[스캔 PDF 처리] {Path(pdf_path).name} ({total_pages}페이지)")
    print("=" * 60)

    results: list[dict] = []

    # --- Process ---
    for page_idx in range(total_pages):
        page_num = page_idx + 1
        print(f"\n  [페이지 {page_num}/{total_pages}] 처리 중...")

        page_result: dict = {
            "page": page_num,
            "image_path": "",
            "ocr_text": "",
            "llava_description": "",
            "combined_text": "",
            "status": "error",
        }

        # 1단계: PDF 페이지 → 이미지 변환
        try:
            image_path = _pdf_page_to_image(pdf_doc, page_idx, output_dir)
            page_result["image_path"] = image_path
            print(f"    이미지 변환 완료: {Path(image_path).name}")
        except RuntimeError as exc:
            logger.error("페이지 %d 이미지 변환 실패: %s", page_num, exc)
            results.append(page_result)
            continue

        # 2단계: EasyOCR 텍스트 추출
        try:
            ocr_text = extract_with_ocr(image_path)
            page_result["ocr_text"] = ocr_text
            print(f"    OCR 완료: {len(ocr_text)}자 추출")
        except (FileNotFoundError, ImportError, RuntimeError) as exc:
            logger.warning("페이지 %d OCR 실패: %s", page_num, exc)
            page_result["ocr_text"] = ""

        # 3단계: LLaVA 이미지 설명 생성
        try:
            llava_desc = describe_image_with_llava(image_path)
            page_result["llava_description"] = llava_desc
            print(f"    LLaVA 설명 완료: {len(llava_desc)}자")
        except (FileNotFoundError, RuntimeError) as exc:
            logger.warning("페이지 %d LLaVA 처리 실패: %s", page_num, exc)
            page_result["llava_description"] = ""

        # 4단계: OCR + LLaVA 결합 텍스트 생성
        ocr_part = page_result["ocr_text"]
        llava_part = page_result["llava_description"]

        combined_parts: list[str] = []
        if ocr_part:
            combined_parts.append(f"[OCR 추출 텍스트]\n{ocr_part}")
        if llava_part:
            combined_parts.append(f"[이미지 설명]\n{llava_part}")

        page_result["combined_text"] = "\n\n".join(combined_parts)
        page_result["status"] = "success"
        results.append(page_result)

    pdf_doc.close()

    # --- Output ---
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n처리 완료: {success_count}/{total_pages} 페이지 성공")
    print(f"이미지 저장 경로: {output_dir}")
    return results
