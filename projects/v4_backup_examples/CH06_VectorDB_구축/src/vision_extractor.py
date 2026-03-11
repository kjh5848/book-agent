"""
Vision LLM(LLaVA)을 사용하여 PDF 문서를 이미지로 변환하고 분석하는 모듈.

PDF 각 페이지를 PNG 이미지로 변환한 뒤, Ollama의 LLaVA 모델에
base64로 인코딩하여 전달합니다. LLM은 이미지에서 텍스트, 메타데이터,
이미지 캡션을 추출합니다.

Vision LLM(Ollama)이 실행 중이지 않은 환경에서는 자동으로
Python 파싱 결과(extractor.py)로 폴백(fallback)합니다.
"""

import base64
import json
import sys
from pathlib import Path

import requests

from extractor import extract_from_pdf

# Vision LLM 설정 기본값
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_VISION_MODEL = "llava:13b"

# PDF 이미지 변환 DPI (해상도가 높을수록 정확도 향상, 속도는 저하)
PDF_RENDER_DPI = 150


# =====================================================================
# === INPUT ===
# pdf_path: PDF 파일 경로
# output_dir: 페이지 이미지 저장 디렉토리
# ollama_url: Ollama 서버 주소
# vision_model: 사용할 Vision LLM 모델명
# =====================================================================


def pdf_to_images(pdf_path: str | Path, output_dir: str | Path) -> list[Path]:
    """PDF 파일의 각 페이지를 PNG 이미지로 변환합니다.

    PyMuPDF(fitz)를 사용하여 PDF 페이지를 래스터 이미지로 렌더링합니다.
    생성된 이미지는 output_dir/{stem}_page_{N:03d}.png 형식으로 저장됩니다.

    Args:
        pdf_path: 변환할 PDF 파일 경로
        output_dir: 페이지 이미지를 저장할 디렉토리 경로

    Returns:
        생성된 PNG 이미지 파일 경로 리스트 (페이지 순서대로)

    Raises:
        ImportError: PyMuPDF(fitz) 패키지가 설치되지 않은 경우
        FileNotFoundError: PDF 파일이 존재하지 않는 경우
        RuntimeError: 이미지 변환 중 오류가 발생한 경우
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError(
            "PyMuPDF 패키지가 설치되지 않았습니다.\n"
            "다음 명령으로 설치하십시오: pip install pymupdf"
        )

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # === PROCESS ===
    image_paths = []
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            # DPI 기반 해상도 행렬 계산 (72dpi 기본에서 배율 적용)
            zoom = PDF_RENDER_DPI / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            image_filename = f"{pdf_path.stem}_page_{page_num + 1:03d}.png"
            image_path = output_dir / image_filename
            pix.save(str(image_path))
            image_paths.append(image_path)
        doc.close()
    except Exception as e:
        raise RuntimeError(
            f"PDF를 이미지로 변환하는 중 오류가 발생했습니다: {pdf_path.name}\n원인: {e}"
        ) from e

    # === OUTPUT ===
    return image_paths


def encode_image_to_base64(image_path: str | Path) -> str:
    """이미지 파일을 base64 문자열로 인코딩합니다.

    Ollama Vision API는 이미지를 base64 형식으로 전달받습니다.

    Args:
        image_path: 인코딩할 이미지 파일 경로

    Returns:
        base64로 인코딩된 이미지 문자열

    Raises:
        FileNotFoundError: 이미지 파일이 존재하지 않는 경우
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_image_with_llava(
    image_path: str | Path,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    vision_model: str = DEFAULT_VISION_MODEL,
) -> dict:
    """LLaVA Vision LLM으로 이미지 페이지를 분석하여 구조화된 정보를 추출합니다.

    Ollama의 /api/generate 엔드포인트에 이미지를 base64로 전달하고,
    텍스트 내용, 문서 메타데이터, 이미지/표 설명을 JSON 형식으로 반환받습니다.

    LLM 연결에 실패하거나 응답이 유효하지 않으면 None을 반환합니다.

    Args:
        image_path: 분석할 이미지 파일 경로
        ollama_url: Ollama 서버 URL (기본값: http://localhost:11434)
        vision_model: 사용할 Vision LLM 모델명 (기본값: llava:13b)

    Returns:
        {
            "text": 추출된 텍스트 (str),
            "title": 문서 제목 추론값 (str),
            "department": 부서명 추론값 (str),
            "caption": 이미지/표/차트 설명 (str),
            "has_image": 이미지 포함 여부 (bool)
        }
        연결 실패 시 None 반환

    Raises:
        없음 (오류 발생 시 None 반환하여 폴백 처리)
    """
    # === INPUT ===
    try:
        image_b64 = encode_image_to_base64(image_path)
    except FileNotFoundError as e:
        print(f"    이미지 인코딩 실패: {e}")
        return None

    prompt = """이 문서 페이지를 분석하여 아래 형식의 JSON만 반환하십시오. 다른 텍스트는 포함하지 마십시오.

{
  "text": "페이지의 모든 텍스트 내용 (줄바꿈 포함)",
  "title": "문서 제목 (추론 불가 시 빈 문자열)",
  "department": "담당 부서 (추론 불가 시 빈 문자열)",
  "caption": "이미지, 표, 차트에 대한 상세 설명 (없으면 빈 문자열)",
  "has_image": true 또는 false
}"""

    # === PROCESS ===
    payload = {
        "model": vision_model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
    }

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        raw_response = response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        print(
            "\n    Vision LLM에 연결할 수 없습니다. "
            "Ollama가 실행 중인지 확인하십시오: ollama serve"
        )
        return None
    except requests.exceptions.Timeout:
        print(f"\n    Vision LLM 응답 시간 초과 (이미지: {Path(image_path).name})")
        return None
    except Exception as e:
        print(f"\n    Vision LLM 호출 중 오류: {e}")
        return None

    # JSON 파싱 시도 (LLM이 코드 블록으로 감쌀 수 있으므로 정리)
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 텍스트 전체를 text 필드에 담아 반환
        result = {
            "text": raw_response,
            "title": "",
            "department": "",
            "caption": "",
            "has_image": False,
        }

    # === OUTPUT ===
    return result


def extract_with_vision(
    pdf_path: str | Path,
    pages_output_dir: str | Path,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    vision_model: str = DEFAULT_VISION_MODEL,
) -> dict:
    """PDF를 Vision LLM으로 분석하여 구조화된 추출 결과를 반환합니다.

    PDF 각 페이지를 이미지로 변환한 뒤 LLaVA로 분석합니다.
    Vision LLM 연결 실패 시 Python 파싱(extractor.py) 결과로
    자동 폴백하여 파이프라인이 항상 결과를 반환합니다.

    Args:
        pdf_path: 분석할 PDF 파일 경로
        pages_output_dir: 페이지 이미지를 저장할 디렉토리 경로
        ollama_url: Ollama 서버 URL
        vision_model: 사용할 Vision LLM 모델명

    Returns:
        {
            "source_path": 파일 절대 경로 (str),
            "file_name": 파일명 (str),
            "file_type": "pdf",
            "parse_method": "vision" 또는 "python_fallback",
            "pages": [
                {
                    "page": 페이지 번호,
                    "image_path": PNG 파일 경로 (str) 또는 None,
                    "text": 추출 텍스트,
                    "title": 제목,
                    "department": 부서명,
                    "caption": 이미지/표 설명,
                    "has_image": 이미지 포함 여부
                }, ...
            ],
            "full_text": 전체 텍스트 연결 문자열 (str)
        }
    """
    pdf_path = Path(pdf_path)
    pages_output_dir = Path(pages_output_dir)

    print(f"  Vision LLM 분석 시작: {pdf_path.name}")

    # === PROCESS: Step 1 — PDF를 페이지 이미지로 변환 ===
    try:
        image_paths = pdf_to_images(pdf_path, pages_output_dir)
        print(f"    {len(image_paths)}개 페이지 이미지 생성 완료")
    except Exception as e:
        print(f"    이미지 변환 실패: {e}")
        print("    Python 파싱으로 폴백합니다.")
        return _fallback_to_python_parsing(pdf_path)

    # === PROCESS: Step 2 — 각 페이지를 LLaVA로 분석 ===
    pages_data = []
    llm_failed = False

    for idx, image_path in enumerate(image_paths, start=1):
        print(f"    페이지 {idx}/{len(image_paths)} 분석 중...", end=" ", flush=True)
        llm_result = analyze_image_with_llava(image_path, ollama_url, vision_model)

        if llm_result is None:
            llm_failed = True
            print("LLM 연결 실패 — 폴백 모드로 전환")
            break

        pages_data.append(
            {
                "page": idx,
                "image_path": str(image_path),
                "text": llm_result.get("text", ""),
                "title": llm_result.get("title", ""),
                "department": llm_result.get("department", ""),
                "caption": llm_result.get("caption", ""),
                "has_image": llm_result.get("has_image", False),
            }
        )
        print("완료")

    # Vision LLM 실패 시 Python 파싱으로 폴백
    if llm_failed:
        return _fallback_to_python_parsing(pdf_path)

    full_text = "\n\n".join(p["text"] for p in pages_data if p["text"])

    # === OUTPUT ===
    return {
        "source_path": str(pdf_path.resolve()),
        "file_name": pdf_path.name,
        "file_type": "pdf",
        "parse_method": "vision",
        "pages": pages_data,
        "full_text": full_text,
    }


def _fallback_to_python_parsing(pdf_path: str | Path) -> dict:
    """Vision LLM 사용 불가 시 Python pypdf 파싱으로 폴백합니다.

    폴백 결과에는 parse_method="python_fallback"이 기록되며,
    이미지 관련 필드(image_path, caption, has_image)는 기본값으로 채워집니다.

    Args:
        pdf_path: 파싱할 PDF 파일 경로

    Returns:
        Vision LLM 결과와 동일한 구조의 딕셔너리
    """
    print(f"  Python 파싱으로 폴백: {Path(pdf_path).name}")
    python_result = extract_from_pdf(pdf_path)

    pages_data = [
        {
            "page": p["page"],
            "image_path": None,
            "text": p["text"],
            "title": "",
            "department": "",
            "caption": "",
            "has_image": False,
        }
        for p in python_result["pages"]
    ]

    return {
        "source_path": python_result["source_path"],
        "file_name": python_result["file_name"],
        "file_type": "pdf",
        "parse_method": "python_fallback",
        "pages": pages_data,
        "full_text": python_result["full_text"],
    }
