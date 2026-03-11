"""
CH08 문서 인제스트 스크립트.

PDF 페이지를 이미지로 캡처 → Vision LLM이 Markdown으로 파싱 →
헤더 기반 청킹 → Ollama 임베딩 → ChromaDB 저장.
페이지 이미지(data/pages/)와 Markdown(data/markdown/)을 저장하여
채팅 UI에서 답변 근거를 이미지+MD로 표시할 수 있습니다.

CH07 ingest.py와 동일 구조:
    parse_filename_metadata(filename) -> dict
    pdf_page_to_base64(pdf_path, page_num, save_dir) -> (str, str|None)
    parse_page_with_vision(base64_image, llm_base_url, vision_model) -> str
    save_markdown(markdown_text, pdf_path, save_dir) -> str
    chunk_text(text, source, department, version, page_image_map,
               chunk_size=500, overlap=50) -> list[dict]
      메타데이터: source, department, version, section_title, chunk_index, page_num, page_image
    ingest(target_file=None, reset=False) -> None
      [1/5] PDF 탐색 → [2/5] 페이지 캡처+이미지 저장 → [3/5] Vision 파싱+MD 저장
      → [4/5] 청킹(page_num/page_image 메타데이터 포함) → [5/5] 임베딩+저장

실행:
    python scripts/ingest.py                              # 전체
    python scripts/ingest.py --file HR_취업규칙_v1.0.pdf  # 파일 지정
    python scripts/ingest.py --reset                      # DB 초기화 후 재인제스트

사전 준비:
    ollama pull nomic-embed-text
    ollama pull llava   # Vision 지원 모델
    PDF 파일을 data/docs/ 디렉토리에 복사
"""

import argparse
import base64
import glob
import os
import re
import sys

import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings

# 프로젝트 루트를 Python 경로에 추가
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

# --- 설정 상수 ---
DOCS_DIR: str = os.path.join(_PROJECT_ROOT, "data", "docs")
PAGES_DIR: str = os.path.join(_PROJECT_ROOT, "data", "pages")
MARKDOWN_DIR: str = os.path.join(_PROJECT_ROOT, "data", "markdown")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
VISION_MODEL: str = os.getenv("VISION_MODEL", "llava")
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_docs")


def parse_filename_metadata(filename: str) -> dict[str, str]:
    """파일명에서 부서, 문서명, 버전 정보를 추출합니다.

    언더스코어(_)로 구분된 파일명 패턴 [부서]_[문서명]_[버전].pdf 을 파싱합니다.
    버전은 v\\d+\\.\\d+ 패턴으로 감지합니다.

    Args:
        filename: 파싱할 PDF 파일명 (예: HR_취업규칙_v1.0.pdf)

    Returns:
        department, doc_name, version 키를 포함하는 딕셔너리.
        파싱 실패 시 department="General", version="unknown" 으로 대체.

    Examples:
        >>> parse_filename_metadata("HR_취업규칙_v1.0.pdf")
        {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}
    """
    # --- Input ---
    stem = os.path.splitext(filename)[0]
    version_pattern = re.compile(r"v\d+\.\d+")

    # --- Process ---
    parts = stem.split("_")
    version = "unknown"
    non_version_parts: list[str] = []

    for part in parts:
        if version_pattern.fullmatch(part):
            version = part
        else:
            non_version_parts.append(part)

    if len(non_version_parts) >= 2:
        department = non_version_parts[0]
        doc_name = "_".join(non_version_parts[1:])
    elif len(non_version_parts) == 1:
        department = "General"
        doc_name = non_version_parts[0]
    else:
        department = "General"
        doc_name = stem

    # --- Output ---
    return {"department": department, "doc_name": doc_name, "version": version}


def pdf_page_to_base64(
    pdf_path: str,
    page_num: int,
    save_dir: str | None = None,
) -> tuple[str, str | None]:
    """PDF 특정 페이지를 PNG로 렌더링하여 base64 문자열과 저장 경로를 반환합니다.

    fitz(PyMuPDF)를 사용하여 지정된 페이지를 DPI 150으로 래스터화합니다.
    save_dir를 지정하면 data/pages/{stem}/page_{page_num+1}.png 경로에 파일로 저장합니다.

    Args:
        pdf_path: PDF 파일의 절대 경로.
        page_num: 렌더링할 페이지 번호 (0부터 시작).
        save_dir: 이미지를 저장할 기본 디렉토리 (None이면 저장하지 않음).

    Returns:
        (base64_str, image_path) 튜플.
        image_path는 save_dir 미지정 시 None.

    Raises:
        FileNotFoundError: PDF 파일이 존재하지 않을 경우.
        IndexError: page_num이 유효한 범위를 벗어날 경우.
    """
    # --- Input ---
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    # --- Process ---
    pdf_document = fitz.open(pdf_path)

    if page_num >= len(pdf_document):
        raise IndexError(
            f"페이지 번호가 범위를 초과했습니다. "
            f"요청: {page_num}, 전체 페이지 수: {len(pdf_document)}"
        )

    page = pdf_document[page_num]
    pixmap = page.get_pixmap(dpi=150)
    png_bytes = pixmap.tobytes("png")
    pdf_document.close()

    b64_str = base64.b64encode(png_bytes).decode("utf-8")

    # save_dir 지정 시 파일로 저장
    image_path: str | None = None
    if save_dir is not None:
        stem = os.path.splitext(os.path.basename(pdf_path))[0]
        page_dir = os.path.join(save_dir, stem)
        os.makedirs(page_dir, exist_ok=True)
        image_filename = f"page_{page_num + 1}.png"
        image_path = os.path.join(page_dir, image_filename)
        with open(image_path, "wb") as f:
            f.write(png_bytes)

    # --- Output ---
    return b64_str, image_path


def parse_page_with_vision(
    base64_image: str,
    llm_base_url: str,
    vision_model: str,
) -> str:
    """Vision LLM에 페이지 이미지를 전달하여 Markdown 텍스트를 반환합니다.

    ChatOllama를 사용하여 base64 인코딩된 이미지를 Vision LLM에 전달하고,
    페이지 내용을 Markdown 형식으로 변환한 결과를 반환합니다.
    오류 발생 시 예외 메시지를 출력하고 빈 문자열을 반환합니다.

    Args:
        base64_image: base64로 인코딩된 PNG 이미지 문자열.
        llm_base_url: Ollama 서버 기본 URL (예: http://localhost:11434).
        vision_model: 사용할 Vision LLM 모델명 (예: llava).

    Returns:
        Vision LLM이 변환한 Markdown 텍스트.
        오류 발생 시 빈 문자열 반환.
    """
    # --- Input ---
    prompt_text = (
        "이 문서 페이지를 Markdown 형식으로 변환하세요. "
        "제목은 ##, 소제목은 ###을 사용하고, 표는 Markdown 표로 변환하세요."
    )

    # --- Process ---
    try:
        llm = ChatOllama(base_url=llm_base_url, model=vision_model)
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
                {"type": "text", "text": prompt_text},
            ]
        )
        response = llm.invoke([message])
        result = response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        print(f"    [경고] Vision 파싱 실패: {exc}")
        result = ""

    # --- Output ---
    return result


def save_markdown(
    markdown_text: str,
    pdf_path: str,
    save_dir: str,
) -> str:
    """Markdown 텍스트를 파일로 저장하고 저장 경로를 반환합니다.

    data/markdown/{stem}.md 경로에 저장합니다.

    Args:
        markdown_text: 저장할 Markdown 텍스트.
        pdf_path: 원본 PDF 파일 경로 (파일명 추출용).
        save_dir: Markdown 파일을 저장할 디렉토리.

    Returns:
        저장된 Markdown 파일의 절대 경로.
    """
    # --- Input ---
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs(save_dir, exist_ok=True)
    md_path = os.path.join(save_dir, f"{stem}.md")

    # --- Process ---
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    # --- Output ---
    return md_path


def chunk_text(
    text: str,
    source: str,
    department: str,
    version: str,
    page_image_map: dict[int, str],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """Markdown 텍스트를 헤더 기반으로 청킹합니다.

    ## 헤더를 기준으로 섹션을 분리한 후, chunk_size를 초과하는 섹션은
    슬라이딩 윈도우 방식으로 추가 분할합니다.
    헤더가 없는 텍스트는 고정 크기 슬라이딩 분할(fallback)을 적용합니다.
    각 청크 메타데이터에 page_num, page_image를 포함합니다.

    Args:
        text: 청킹할 Markdown 텍스트.
        source: 원본 파일명 (메타데이터용).
        department: 부서명 (메타데이터용).
        version: 문서 버전 (메타데이터용).
        page_image_map: {page_num: image_path} 형태의 페이지 이미지 경로 맵.
        chunk_size: 청크 최대 문자 수 (기본값: 500).
        overlap: 슬라이딩 분할 시 겹치는 문자 수 (기본값: 50).

    Returns:
        text와 metadata 키를 포함하는 청크 딕셔너리 리스트.
        각 metadata에는 source, department, version, section_title,
        chunk_index, page_num, page_image가 포함됩니다.
    """
    # --- Input ---
    header_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    chunks: list[dict] = []
    chunk_index: int = 0
    step: int = chunk_size - overlap

    # page_image_map에서 첫 번째 이미지를 기본값으로 설정
    default_page_num = 0
    default_page_image = page_image_map.get(0, "")

    # --- Process ---
    header_matches = list(header_pattern.finditer(text))

    if not header_matches:
        # fallback: 헤더 없음 → 고정 크기 슬라이딩 분할
        section_title = "본문"
        start = 0
        while start < len(text):
            segment = text[start : start + chunk_size]
            if segment.strip():
                chunks.append(
                    {
                        "text": segment,
                        "metadata": {
                            "source": source,
                            "department": department,
                            "version": version,
                            "section_title": section_title,
                            "chunk_index": chunk_index,
                            "page_num": default_page_num,
                            "page_image": default_page_image,
                        },
                    }
                )
                chunk_index += 1
            start += step
        return chunks

    # 헤더 있음: 섹션별 분할
    # 첫 번째 헤더 이전 텍스트를 "도입부"로 처리
    sections: list[tuple[str, str]] = []
    intro_text = text[: header_matches[0].start()].strip()
    if intro_text:
        sections.append(("도입부", intro_text))

    for idx, match in enumerate(header_matches):
        section_title = match.group(2).strip()
        content_start = match.end()
        content_end = (
            header_matches[idx + 1].start()
            if idx + 1 < len(header_matches)
            else len(text)
        )
        section_content = text[content_start:content_end].strip()
        full_section = f"{match.group(0)}\n{section_content}".strip()
        sections.append((section_title, full_section))

    for section_idx, (section_title, section_body) in enumerate(sections):
        # 섹션 위치를 기반으로 page_num 추정 (섹션 순서 / 전체 섹션 수 * 전체 페이지 수)
        estimated_page = min(
            int(section_idx / max(len(sections), 1) * len(page_image_map)),
            max(len(page_image_map) - 1, 0),
        )
        page_num = estimated_page
        page_image = page_image_map.get(page_num, default_page_image)

        if len(section_body) <= chunk_size:
            # 섹션 전체를 하나의 청크로
            chunks.append(
                {
                    "text": section_body,
                    "metadata": {
                        "source": source,
                        "department": department,
                        "version": version,
                        "section_title": section_title,
                        "chunk_index": chunk_index,
                        "page_num": page_num,
                        "page_image": page_image,
                    },
                }
            )
            chunk_index += 1
        else:
            # 섹션 > chunk_size: 슬라이딩 윈도우 분할
            start = 0
            while start < len(section_body):
                segment = section_body[start : start + chunk_size]
                if segment.strip():
                    chunks.append(
                        {
                            "text": segment,
                            "metadata": {
                                "source": source,
                                "department": department,
                                "version": version,
                                "section_title": section_title,
                                "chunk_index": chunk_index,
                                "page_num": page_num,
                                "page_image": page_image,
                            },
                        }
                    )
                    chunk_index += 1
                start += step

    # --- Output ---
    return chunks


def ingest(target_file: str | None = None, reset: bool = False) -> None:
    """PDF 문서를 Vision LLM으로 파싱하여 ChromaDB에 저장합니다.

    5단계 파이프라인을 순서대로 실행합니다:
        [1/5] PDF 탐색  — data/docs/ 하위 *.pdf 탐색 (recursive)
        [2/5] 페이지 캡처+저장 — fitz로 각 페이지를 base64 PNG로 변환, data/pages/ 저장
        [3/5] Vision 파싱+MD 저장 — Vision LLM으로 Markdown 변환, data/markdown/ 저장
        [4/5] 청킹       — chunk_text()로 page_num/page_image 메타데이터 포함
        [5/5] 임베딩+저장 — OllamaEmbeddings(nomic-embed-text) → Chroma → data/chroma_db/

    Args:
        target_file: 처리할 단일 PDF 파일명 (None이면 전체 처리).
        reset: True이면 ChromaDB를 초기화 후 재인제스트.

    Raises:
        SystemExit: data/docs/ 하위에 PDF 파일이 없을 경우.
    """
    print("=" * 60)
    print("  CH08 문서 인제스트 (Vision LLM + 이미지 저장 방식)")
    print("=" * 60)

    # =========================================================
    # [1/5] PDF 탐색
    # =========================================================

    # --- Input ---
    if target_file:
        # 특정 파일만 처리
        target_path = os.path.join(DOCS_DIR, target_file)
        if not os.path.exists(target_path):
            print(f"\n[오류] 지정된 파일을 찾을 수 없습니다: {target_path}")
            sys.exit(1)
        pdf_files = [target_path]
    else:
        pdf_files = sorted(
            glob.glob(os.path.join(DOCS_DIR, "**", "*.pdf"), recursive=True)
        )

    # --- Process ---
    if not pdf_files:
        print(f"\n[오류] data/docs/ 하위에 PDF 파일이 없습니다. ({DOCS_DIR})")
        sys.exit(1)

    print(f"\n[1/5] PDF 파일 탐색... {len(pdf_files)}개 발견")
    for pdf_path in pdf_files:
        print(f"  - {os.path.relpath(pdf_path, DOCS_DIR)}")

    # =========================================================
    # [2/5] 페이지 캡처 + 이미지 저장 / [3/5] Vision 파싱 + MD 저장
    # =========================================================
    print(f"\n[2/5] 페이지 캡처+저장 + [3/5] Vision 파싱+MD 저장 중... (모델: {VISION_MODEL})")

    # 저장 디렉토리 생성
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    # --- Input ---
    all_chunks: list[dict] = []

    # --- Process ---
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        metadata = parse_filename_metadata(filename)
        print(f"\n  처리 중: {filename}")
        print(f"    부서: {metadata['department']}, 버전: {metadata['version']}")

        try:
            pdf_document = fitz.open(pdf_path)
            total_pages = len(pdf_document)
            pdf_document.close()
        except Exception as exc:
            print(f"    [경고] PDF 열기 실패, 건너뜁니다: {exc}")
            continue

        # 페이지별 캡처 → 이미지 저장 → Vision 파싱 → 페이지 합본
        page_markdowns: list[str] = []
        page_image_map: dict[int, str] = {}  # {page_num: image_path}

        for page_num in range(total_pages):
            print(f"    페이지 {page_num + 1}/{total_pages} 처리 중...", end="\r")

            try:
                # [2/5] 이미지 캡처 + data/pages/ 저장
                b64_image, image_path = pdf_page_to_base64(
                    pdf_path, page_num, save_dir=PAGES_DIR
                )
                if image_path:
                    page_image_map[page_num] = image_path

                # [3/5] Vision LLM 파싱
                markdown_text = parse_page_with_vision(
                    b64_image, OLLAMA_BASE_URL, VISION_MODEL
                )
            except Exception as exc:
                print(f"\n    [경고] 페이지 {page_num + 1} 처리 실패: {exc}")
                markdown_text = ""

            if markdown_text.strip():
                page_markdowns.append(markdown_text)

        print(f"    {total_pages}페이지 Vision 파싱 완료.          ")

        # [3/5] 전체 Markdown을 data/markdown/ 에 저장
        full_document_text = "\n\n".join(page_markdowns)
        if full_document_text.strip():
            md_path = save_markdown(full_document_text, pdf_path, MARKDOWN_DIR)
            print(f"    Markdown 저장: {os.path.relpath(md_path, _PROJECT_ROOT)}")

        # =========================================================
        # [4/5] 청킹 (page_num, page_image 메타데이터 포함)
        # =========================================================
        doc_chunks = chunk_text(
            text=full_document_text,
            source=filename,
            department=metadata["department"],
            version=metadata["version"],
            page_image_map=page_image_map,
        )
        all_chunks.extend(doc_chunks)
        print(f"    청크 생성: {len(doc_chunks)}개")

    print(f"\n[4/5] 전체 청킹 완료: {len(all_chunks)}개 청크")

    if not all_chunks:
        print("\n[오류] 생성된 청크가 없습니다. Vision 파싱 결과를 확인하십시오.")
        sys.exit(1)

    # =========================================================
    # [5/5] 임베딩 + ChromaDB 저장
    # =========================================================
    print(f"\n[5/5] 임베딩 생성 및 ChromaDB 저장 중... (임베딩 모델: {EMBED_MODEL})")

    # --- Input ---
    texts = [chunk["text"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]

    # 상대 경로를 프로젝트 루트 기준 절대 경로로 변환
    if not os.path.isabs(CHROMA_PERSIST_DIR):
        chroma_dir_abs = os.path.join(
            _PROJECT_ROOT, CHROMA_PERSIST_DIR.lstrip("./")
        )
    else:
        chroma_dir_abs = CHROMA_PERSIST_DIR

    os.makedirs(chroma_dir_abs, exist_ok=True)

    # --- Process ---
    try:
        from langchain_chroma import Chroma
    except ImportError:
        from langchain_community.vectorstores import Chroma  # type: ignore[no-redef]

    embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=EMBED_MODEL)

    if reset:
        # ChromaDB 초기화 후 재생성
        print("  [초기화] 기존 ChromaDB 컬렉션을 삭제합니다...")
        try:
            existing = Chroma(
                embedding_function=embeddings,
                persist_directory=chroma_dir_abs,
                collection_name=COLLECTION_NAME,
            )
            existing.delete_collection()
            print("  [초기화] 컬렉션 삭제 완료.")
        except Exception as exc:
            print(f"  [초기화] 삭제 중 오류 (무시하고 계속): {exc}")

    Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=chroma_dir_abs,
        collection_name=COLLECTION_NAME,
    )

    # --- Output ---
    print("\n" + "=" * 60)
    print(f"  인제스트 완료: {len(all_chunks)}개 청크 → {chroma_dir_abs}")
    print(f"  페이지 이미지: {PAGES_DIR}")
    print(f"  Markdown 저장: {MARKDOWN_DIR}")
    print("  서버 실행: python -m app.main")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CH08 문서 인제스트 — PDF → ChromaDB (Vision LLM + 이미지 저장)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        metavar="FILENAME",
        help="처리할 단일 PDF 파일명 (예: HR_취업규칙_v1.0.pdf). 미지정 시 전체 처리.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        default=False,
        help="ChromaDB 컬렉션을 초기화하고 재인제스트합니다.",
    )
    args = parser.parse_args()

    ingest(target_file=args.file, reset=args.reset)
