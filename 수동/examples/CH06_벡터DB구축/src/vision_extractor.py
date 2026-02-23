"""
Vision LLM 기반 PDF 추출 모듈.

PDF 페이지를 이미지로 변환한 후 Vision LLM에 전달하여
구조화된 Markdown 텍스트로 변환합니다.

지원 LLM Provider:
    - ollama: Ollama 로컬 서버 (llava:7b, llava:13b 등)
    - openai: OpenAI API (gpt-4o, gpt-4o-mini 등)

환경 변수:
    LLM_PROVIDER:    ollama 또는 openai
    LLM_MODEL_NAME:  사용할 모델명
    OLLAMA_BASE_URL: Ollama 서버 주소 (기본: http://localhost:11434)
    OPENAI_API_KEY:  OpenAI API 키 (openai 선택 시 필수)
"""

import base64
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
_LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llava:7b")
_OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_VISION_PROMPT = (
    "이 PDF 페이지를 Markdown으로 변환하세요. "
    "표는 Markdown 표로, 제목은 #으로 표현하세요. "
    "모든 텍스트 내용을 빠짐없이 포함하고, "
    "이미지나 그래프는 '[이미지: 간략한 설명]' 형식으로 표기하세요."
)


def pdf_page_to_image(pdf_path: str, page_num: int, dpi: int = 150) -> bytes:
    """PDF의 특정 페이지를 PNG 이미지 바이트로 변환합니다.

    PyMuPDF(fitz)를 사용하여 페이지를 래스터 이미지로 렌더링합니다.
    dpi 값이 높을수록 이미지 품질이 좋아지지만 처리 시간과 메모리가 증가합니다.

    Args:
        pdf_path: 변환할 PDF 파일의 경로.
        page_num: 변환할 페이지 번호 (0부터 시작하는 인덱스).
        dpi: 렌더링 해상도. 기본값은 150 DPI.

    Returns:
        PNG 형식의 이미지 데이터 바이트.

    Raises:
        FileNotFoundError: pdf_path에 파일이 존재하지 않을 때.
        IndexError: page_num이 PDF 페이지 수를 초과할 때.
        RuntimeError: PyMuPDF 미설치 또는 렌더링 오류 발생 시.
    """
    # --- Input ---
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}"
        )

    # --- Process ---
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError(
            "PyMuPDF가 설치되지 않았습니다. 'pip install pymupdf'를 실행하십시오."
        )

    try:
        doc = fitz.open(pdf_path)

        if page_num >= len(doc):
            raise IndexError(
                f"페이지 번호 {page_num}이 유효하지 않습니다. "
                f"이 PDF의 페이지 수: {len(doc)}"
            )

        page = doc[page_num]
        # DPI에 맞춰 확대 행렬 계산 (기본 72 DPI 기준)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        image_bytes = pixmap.tobytes("png")
        doc.close()

    except (IndexError, RuntimeError):
        raise
    except Exception as e:
        raise RuntimeError(
            f"PDF 페이지를 이미지로 변환하는 중 오류가 발생했습니다: {e}"
        )

    # --- Output ---
    return image_bytes


def image_to_base64(image_bytes: bytes) -> str:
    """이미지 바이트를 base64 인코딩 문자열로 변환합니다.

    Vision LLM API에 이미지를 전달할 때 사용합니다.

    Args:
        image_bytes: PNG 등 이미지 형식의 바이트 데이터.

    Returns:
        base64 인코딩된 문자열.

    Raises:
        ValueError: image_bytes가 비어 있을 때.
    """
    # --- Input ---
    if not image_bytes:
        raise ValueError("이미지 바이트 데이터가 비어 있습니다.")

    # --- Process ---
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    # --- Output ---
    return encoded


def call_vision_llm(image_base64: str, page_num: int) -> str:
    """Vision LLM에 이미지를 전달하여 Markdown 텍스트로 변환합니다.

    LLM_PROVIDER 환경변수에 따라 Ollama 또는 OpenAI API를 사용합니다.

    Ollama 방식:
        POST {OLLAMA_BASE_URL}/api/generate
        payload: {"model": str, "prompt": str, "images": [base64], "stream": false}

    OpenAI 방식:
        OpenAI Chat Completions API
        model: LLM_MODEL_NAME, image는 base64 data URL로 전달

    Args:
        image_base64: base64 인코딩된 이미지 문자열.
        page_num: 처리 중인 페이지 번호 (로그 출력용, 1부터 시작).

    Returns:
        LLM이 생성한 Markdown 형식 텍스트.

    Raises:
        ValueError: image_base64가 비어 있을 때.
        ValueError: LLM_PROVIDER가 ollama 또는 openai가 아닐 때.
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: LLM API 호출 중 오류 발생 시.
    """
    # --- Input ---
    if not image_base64:
        raise ValueError("이미지 base64 데이터가 비어 있습니다.")

    provider = _LLM_PROVIDER.lower().strip()
    if provider not in ("ollama", "openai"):
        raise ValueError(
            f"지원하지 않는 LLM_PROVIDER 값입니다: '{provider}'. "
            "ollama 또는 openai 중 하나를 설정하십시오."
        )

    print(f"    [Vision LLM] 페이지 {page_num} 처리 중... (provider={provider}, model={_LLM_MODEL_NAME})")

    # --- Process ---
    if provider == "ollama":
        markdown_text = _call_ollama_vision(image_base64)
    else:
        markdown_text = _call_openai_vision(image_base64)

    # --- Output ---
    return markdown_text


def extract_pdf_to_markdown(pdf_path: str, output_dir: str = "./outputs/markdown") -> str:
    """PDF 전체를 Vision LLM으로 처리하여 Markdown 파일로 저장합니다.

    각 페이지를 이미지로 변환한 후 Vision LLM에 전달하여 Markdown으로 변환하고,
    모든 페이지 결과를 하나의 .md 파일로 합쳐 저장합니다.

    출력 파일명: PDF 파일명의 확장자를 .md로 변경
    예: HR_취업규칙_v1.0.pdf → HR_취업규칙_v1.0.md

    Args:
        pdf_path: 처리할 PDF 파일의 경로.
        output_dir: Markdown 파일을 저장할 디렉토리. 기본값은 "./outputs/markdown".

    Returns:
        저장된 .md 파일의 절대 경로.

    Raises:
        FileNotFoundError: pdf_path에 파일이 존재하지 않을 때.
        RuntimeError: PDF 처리 또는 LLM 호출 중 오류 발생 시.
    """
    # --- Input ---
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}"
        )

    pdf_stem = Path(pdf_path).stem
    md_filename = f"{pdf_stem}.md"
    os.makedirs(output_dir, exist_ok=True)
    md_output_path = os.path.join(output_dir, md_filename)

    # --- Process ---
    try:
        import fitz
    except ImportError:
        raise RuntimeError(
            "PyMuPDF가 설치되지 않았습니다. 'pip install pymupdf'를 실행하십시오."
        )

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    print(f"  Vision LLM 추출 시작: {Path(pdf_path).name} ({total_pages}페이지)")

    all_markdown_parts: list[str] = []

    for page_idx in range(total_pages):
        page_num = page_idx + 1
        print(f"  페이지 {page_num}/{total_pages} 처리 중...")

        # 페이지를 이미지로 변환
        image_bytes = pdf_page_to_image(pdf_path, page_num=page_idx, dpi=150)
        image_base64 = image_to_base64(image_bytes)

        # Vision LLM 호출
        page_markdown = call_vision_llm(image_base64, page_num=page_num)

        # 페이지 구분자 추가
        page_header = f"\n\n---\n<!-- 페이지 {page_num} -->\n\n"
        all_markdown_parts.append(page_header + page_markdown)

    # 전체 Markdown 합치기
    full_markdown = f"# {pdf_stem}\n\n" + "".join(all_markdown_parts)

    # 파일 저장
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    # --- Output ---
    abs_output_path = os.path.abspath(md_output_path)
    print(f"  Markdown 저장 완료: {abs_output_path}")
    return abs_output_path


def _call_ollama_vision(image_base64: str) -> str:
    """Ollama Vision API를 호출하여 이미지를 Markdown으로 변환합니다.

    POST {OLLAMA_BASE_URL}/api/generate 엔드포인트를 사용합니다.
    stream=false로 설정하여 단일 응답을 받습니다.

    Args:
        image_base64: base64 인코딩된 이미지 문자열.

    Returns:
        LLM이 생성한 Markdown 텍스트.

    Raises:
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: API 호출 실패 또는 응답 오류 시.
    """
    # --- Input ---
    import requests

    url = f"{_OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": _LLM_MODEL_NAME,
        "prompt": _VISION_PROMPT,
        "images": [image_base64],
        "stream": False,
    }

    # --- Process ---
    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Ollama 서버({_OLLAMA_BASE_URL})에 연결할 수 없습니다. "
            "'ollama serve' 명령으로 서버를 먼저 실행하십시오."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama Vision API 응답 시간이 초과되었습니다. "
            "이미지 크기를 줄이거나 타임아웃 값을 늘려보십시오."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama API 오류 (상태 코드: {response.status_code}): {response.text}"
        )

    result = response.json()
    markdown_text = result.get("response", "")

    if not markdown_text:
        raise RuntimeError(
            "Ollama API 응답에 'response' 필드가 비어 있습니다. "
            f"응답 내용: {result}"
        )

    # --- Output ---
    return markdown_text.strip()


def _call_openai_vision(image_base64: str) -> str:
    """OpenAI Vision API를 호출하여 이미지를 Markdown으로 변환합니다.

    Chat Completions API를 사용하며, 이미지는 base64 data URL 형식으로 전달합니다.
    OPENAI_API_KEY 환경변수가 설정되어 있어야 합니다.

    Args:
        image_base64: base64 인코딩된 이미지 문자열.

    Returns:
        LLM이 생성한 Markdown 텍스트.

    Raises:
        RuntimeError: openai 패키지 미설치 시.
        RuntimeError: OPENAI_API_KEY 미설정 시.
        RuntimeError: API 호출 실패 시.
    """
    # --- Input ---
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일에 OPENAI_API_KEY=sk-proj-... 를 추가하십시오."
        )

    # --- Process ---
    try:
        from openai import OpenAI
    except ImportError:
        print(
            "[안내] OpenAI 패키지가 설치되지 않았습니다. "
            "'pip install openai'를 실행한 후 다시 시도하십시오."
        )
        raise RuntimeError(
            "openai 패키지가 설치되지 않았습니다. "
            "'pip install openai'를 실행하십시오."
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=_LLM_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": _VISION_PROMPT,
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )
    except Exception as e:
        raise RuntimeError(
            f"OpenAI Vision API 호출 중 오류가 발생했습니다: {e}"
        )

    markdown_text = response.choices[0].message.content
    if not markdown_text:
        raise RuntimeError(
            "OpenAI API 응답이 비어 있습니다. 모델과 API 키를 확인하십시오."
        )

    # --- Output ---
    return markdown_text.strip()
