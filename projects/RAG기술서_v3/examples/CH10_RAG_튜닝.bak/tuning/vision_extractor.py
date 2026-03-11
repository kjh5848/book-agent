"""Vision + OCR 하이브리드 이미지 텍스트 추출 모듈.

LLaVA를 활용한 이미지 캡션 생성과 EasyOCR을 활용한 텍스트 추출을
결합하는 하이브리드 방식을 구현합니다.
이미지가 포함된 PDF에서 텍스트를 최대한 추출합니다.
"""

import base64
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

console = Console()

# --- 상수 정의 ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
VISION_MODEL = "llava:13b"
VISION_MODEL_LIGHT = "llava:7b"


# ============================================================
# INPUT: 이미지 전처리
# ============================================================

def load_image_as_base64(image_path: Path) -> str:
    """이미지를 Base64 문자열로 인코딩합니다.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        Base64 인코딩된 이미지 문자열

    Raises:
        FileNotFoundError: 이미지 파일이 없는 경우
    """
    if not image_path.exists():
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        sys.exit(1)

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 200
) -> list[Path]:
    """PDF 파일의 각 페이지를 이미지로 변환합니다.

    Args:
        pdf_path: PDF 파일 경로
        output_dir: 이미지 저장 디렉토리
        dpi: 이미지 해상도 (DPI)

    Returns:
        생성된 이미지 파일 경로 리스트

    Raises:
        ImportError: pypdf 또는 pillow가 설치되지 않은 경우
    """
    try:
        import pypdf
        from PIL import Image

        output_dir.mkdir(parents=True, exist_ok=True)
        image_paths = []

        with pypdf.PdfReader(str(pdf_path)) as reader:
            for page_num, page in enumerate(reader.pages):
                # 이미지 추출 시도
                for image_idx, image_obj in enumerate(page.images):
                    img_path = output_dir / f"page_{page_num+1}_img_{image_idx+1}.png"

                    with open(img_path, "wb") as img_file:
                        img_file.write(image_obj.data)

                    image_paths.append(img_path)
                    console.print(f"  이미지 추출: {img_path.name}")

        return image_paths

    except ImportError as e:
        console.print(f"[red]필수 패키지 없음: {e}[/red]")
        console.print("pip install pypdf pillow 를 실행하십시오.")
        return []


# ============================================================
# PROCESS: LLaVA Vision 캡션 생성
# ============================================================

def generate_image_caption_llava(
    image_path: Path,
    prompt: str = "이 이미지에서 텍스트와 주요 내용을 한국어로 상세히 설명하십시오."
) -> str:
    """LLaVA를 사용하여 이미지 캡션을 생성합니다.

    Ollama를 통해 LLaVA 모델에 이미지를 전달하고 설명을 받습니다.

    Args:
        image_path: 이미지 파일 경로
        prompt: LLaVA에 전달할 프롬프트

    Returns:
        생성된 이미지 캡션

    Raises:
        ConnectionError: Ollama 서버 연결 실패 시
    """
    try:
        import ollama

        image_base64 = load_image_as_base64(image_path)

        console.print(f"  [dim]LLaVA로 이미지 분석 중: {image_path.name}[/dim]")
        start_time = time.time()

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ]
        )

        elapsed = time.time() - start_time
        caption = response["message"]["content"]
        console.print(f"  [green]LLaVA 캡션 생성 완료 ({elapsed:.1f}s)[/green]")
        return caption

    except ImportError:
        console.print("[red]ollama 패키지가 설치되지 않았습니다.[/red]")
        console.print("pip install ollama 를 실행하십시오.")
        return _generate_fallback_caption(image_path)

    except Exception as e:
        error_msg = str(e)
        if "ConnectionRefusedError" in error_msg or "connection" in error_msg.lower():
            console.print(
                "[red]Ollama 서버에 연결할 수 없습니다.[/red]"
            )
            console.print(
                "터미널에서 'ollama serve' 명령을 먼저 실행하십시오."
            )
        else:
            console.print(f"[yellow]LLaVA 분석 실패: {e}[/yellow]")

        return _generate_fallback_caption(image_path)


def _generate_fallback_caption(image_path: Path) -> str:
    """LLaVA 사용 불가 시 대체 캡션을 반환합니다.

    Args:
        image_path: 이미지 경로

    Returns:
        대체 캡션 문자열
    """
    return (
        f"[이미지: {image_path.name}] "
        "LLaVA 분석 불가 - Ollama 서버 실행 후 재시도하십시오."
    )


# ============================================================
# PROCESS: EasyOCR 텍스트 추출
# ============================================================

def extract_text_easyocr(
    image_path: Path,
    languages: list[str] = None
) -> str:
    """EasyOCR을 사용하여 이미지에서 텍스트를 추출합니다.

    Args:
        image_path: 이미지 파일 경로
        languages: OCR 언어 코드 리스트 (기본값: ["ko", "en"])

    Returns:
        추출된 텍스트 문자열
    """
    if languages is None:
        languages = ["ko", "en"]

    try:
        import easyocr

        console.print(f"  [dim]EasyOCR 텍스트 추출 중: {image_path.name}[/dim]")
        start_time = time.time()

        reader = easyocr.Reader(languages, gpu=False)
        results = reader.readtext(str(image_path))

        elapsed = time.time() - start_time

        # 신뢰도 0.5 이상 텍스트만 추출
        extracted_texts = [
            text
            for (bbox, text, confidence) in results
            if confidence >= 0.5
        ]

        combined_text = " ".join(extracted_texts)
        console.print(
            f"  [green]OCR 완료: {len(extracted_texts)}개 텍스트 블록 ({elapsed:.1f}s)[/green]"
        )
        return combined_text

    except ImportError:
        console.print("[red]easyocr 패키지가 설치되지 않았습니다.[/red]")
        console.print("pip install easyocr 를 실행하십시오.")
        return "[OCR 실패: easyocr 패키지 필요]"

    except Exception as e:
        console.print(f"[yellow]OCR 추출 실패: {e}[/yellow]")
        return f"[OCR 실패: {str(e)[:50]}]"


def extract_text_easyocr_from_pdf(
    pdf_path: Path,
    max_pages: int = 5
) -> list[dict]:
    """PDF에서 각 페이지의 텍스트를 OCR로 추출합니다.

    Args:
        pdf_path: PDF 파일 경로
        max_pages: 처리할 최대 페이지 수

    Returns:
        페이지별 OCR 결과 리스트
    """
    results = []

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        pages_to_process = min(len(doc), max_pages)

        for page_num in range(pages_to_process):
            page = doc[page_num]
            # 페이지를 이미지로 렌더링
            pix = page.get_pixmap(dpi=200)
            img_path = OUTPUTS_DIR / f"temp_page_{page_num+1}.png"
            img_path.parent.mkdir(parents=True, exist_ok=True)
            pix.save(str(img_path))

            # OCR 적용
            ocr_text = extract_text_easyocr(img_path)

            results.append({
                "page": page_num + 1,
                "ocr_text": ocr_text,
                "char_count": len(ocr_text)
            })

            # 임시 이미지 삭제
            img_path.unlink(missing_ok=True)

        doc.close()

    except ImportError:
        console.print("[yellow]PyMuPDF (fitz) 없음. 기본 pypdf로 대체합니다.[/yellow]")
        results.append({
            "page": 1,
            "ocr_text": "[PyMuPDF 없음: pip install pymupdf 를 실행하십시오]",
            "char_count": 0
        })

    return results


# ============================================================
# PROCESS: 하이브리드 추출 (Vision + OCR 결합)
# ============================================================

def hybrid_extract(
    image_path: Path,
    use_vision: bool = True,
    use_ocr: bool = True,
    min_ocr_confidence: float = 0.5
) -> dict[str, str]:
    """Vision 캡션과 OCR 텍스트를 결합하여 최적 추출 결과를 반환합니다.

    Args:
        image_path: 이미지 파일 경로
        use_vision: LLaVA Vision 사용 여부
        use_ocr: EasyOCR 사용 여부
        min_ocr_confidence: OCR 최소 신뢰도

    Returns:
        하이브리드 추출 결과 딕셔너리
    """
    result = {
        "image_path": str(image_path),
        "vision_caption": "",
        "ocr_text": "",
        "combined_text": "",
        "method": ""
    }

    # Vision 캡션 생성
    if use_vision:
        vision_text = generate_image_caption_llava(image_path)
        result["vision_caption"] = vision_text

    # OCR 텍스트 추출
    if use_ocr:
        ocr_text = extract_text_easyocr(image_path)
        result["ocr_text"] = ocr_text

    # 결합 전략 결정
    has_vision = bool(result["vision_caption"]) and "불가" not in result["vision_caption"]
    has_ocr = bool(result["ocr_text"]) and "실패" not in result["ocr_text"]

    if has_vision and has_ocr:
        result["combined_text"] = (
            f"[이미지 설명] {result['vision_caption']}\n"
            f"[추출 텍스트] {result['ocr_text']}"
        )
        result["method"] = "hybrid (Vision + OCR)"

    elif has_vision:
        result["combined_text"] = result["vision_caption"]
        result["method"] = "vision only"

    elif has_ocr:
        result["combined_text"] = result["ocr_text"]
        result["method"] = "ocr only"

    else:
        result["combined_text"] = "[이미지에서 텍스트 추출 불가]"
        result["method"] = "failed"

    return result


def process_pdf_with_hybrid(
    pdf_path: Path,
    extract_images: bool = True
) -> list[dict]:
    """PDF 파일을 하이브리드 방식으로 처리합니다.

    Args:
        pdf_path: PDF 파일 경로
        extract_images: 이미지 추출 여부

    Returns:
        페이지별 처리 결과 리스트
    """
    try:
        import pypdf

        results = []

        with pypdf.PdfReader(str(pdf_path)) as reader:
            total_pages = len(reader.pages)
            console.print(f"  PDF 총 {total_pages}페이지 처리 중...")

            for page_num, page in enumerate(reader.pages):
                # 텍스트 직접 추출 시도
                text = page.extract_text() or ""

                page_result = {
                    "page": page_num + 1,
                    "direct_text": text,
                    "image_count": len(page.images),
                    "image_results": []
                }

                # 이미지가 있으면 하이브리드 추출
                if extract_images and page.images:
                    img_dir = OUTPUTS_DIR / "extracted_images"
                    img_dir.mkdir(parents=True, exist_ok=True)

                    for img_idx, image_obj in enumerate(page.images):
                        img_path = img_dir / f"p{page_num+1}_img{img_idx+1}.png"

                        try:
                            with open(img_path, "wb") as f:
                                f.write(image_obj.data)

                            img_result = hybrid_extract(img_path)
                            page_result["image_results"].append(img_result)

                        except Exception as e:
                            console.print(f"  [yellow]이미지 처리 실패: {e}[/yellow]")

                results.append(page_result)

        return results

    except ImportError:
        console.print("[red]pypdf 패키지가 없습니다. pip install pypdf 를 실행하십시오.[/red]")
        return []


# ============================================================
# OUTPUT: 결과 출력 및 저장
# ============================================================

def print_extraction_results(results: list[dict]) -> None:
    """추출 결과를 테이블로 출력합니다.

    Args:
        results: 하이브리드 추출 결과 리스트
    """
    table = Table(title="하이브리드 추출 결과")
    table.add_column("페이지", style="cyan", justify="center")
    table.add_column("직접 추출 길이", style="yellow")
    table.add_column("이미지 수", style="blue")
    table.add_column("이미지 추출 방법", style="green")
    table.add_column("이미지 텍스트 미리보기", style="white")

    for result in results:
        img_methods = ", ".join([
            r.get("method", "none")
            for r in result.get("image_results", [])
        ]) or "없음"

        img_preview = ""
        if result.get("image_results"):
            first_img = result["image_results"][0]
            combined = first_img.get("combined_text", "")
            img_preview = combined[:40] + "..." if len(combined) > 40 else combined

        table.add_row(
            str(result["page"]),
            f"{len(result.get('direct_text', ''))}자",
            str(result.get("image_count", 0)),
            img_methods,
            img_preview
        )

    console.print(table)


def run_vision_extractor_demo() -> None:
    """Vision + OCR 하이브리드 추출 데모를 실행합니다."""
    console.rule("[bold blue]CH10 Vision + OCR 하이브리드 추출 데모[/bold blue]")

    # 데모: 샘플 PDF 탐색
    pdf_files = list(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        console.print(
            "[yellow]data/ 폴더에 PDF 파일이 없습니다.[/yellow]"
        )
        console.print("CH06 examples에서 PDF 파일을 data/ 폴더에 복사하십시오.")

        # 기능 설명만 출력
        console.print("\n[bold]하이브리드 추출 처리 흐름:[/bold]")

        flow_table = Table(title="Vision + OCR 하이브리드 처리 흐름")
        flow_table.add_column("단계", style="cyan", justify="center")
        flow_table.add_column("방법", style="white")
        flow_table.add_column("도구", style="yellow")
        flow_table.add_column("결과", style="green")

        flow_table.add_row("1", "PDF 텍스트 직접 추출", "pypdf", "텍스트 레이어가 있는 경우")
        flow_table.add_row("2", "이미지 추출", "pypdf + PIL", "페이지 내 이미지 파일")
        flow_table.add_row("3", "Vision 캡션", "LLaVA (Ollama)", "이미지 내용 설명")
        flow_table.add_row("4", "OCR 텍스트", "EasyOCR", "이미지 내 텍스트")
        flow_table.add_row("5", "결합", "하이브리드", "Vision + OCR 통합 텍스트")

        console.print(flow_table)

    else:
        # PDF가 있으면 실제 처리
        console.print(f"[green]PDF 파일 발견: {len(pdf_files)}개[/green]")

        for pdf_path in pdf_files[:2]:  # 최대 2개만 처리
            console.print(f"\n[bold cyan]처리 중: {pdf_path.name}[/bold cyan]")

            results = process_pdf_with_hybrid(pdf_path, extract_images=True)
            print_extraction_results(results)

    # --- OUTPUT: 사용 가이드 ---
    console.rule("[bold green]데모 완료[/bold green]")
    console.print(
        "\n[bold]Vision + OCR 하이브리드 추출 전략:[/bold]\n"
        "  1. pypdf로 텍스트 직접 추출 (가장 빠름)\n"
        "  2. 이미지/스캔 PDF는 EasyOCR로 텍스트 추출\n"
        "  3. 차트/다이어그램은 LLaVA로 내용 설명\n"
        "  4. 두 결과를 결합하여 ChromaDB에 저장\n"
        "\n  [yellow]주의:[/yellow] LLaVA 사용 시 Ollama 서버가 실행 중이어야 합니다.\n"
        "  ollama pull llava:13b 또는 ollama pull llava:7b"
    )


if __name__ == "__main__":
    run_vision_extractor_demo()
