"""CH10 RAG 시스템 튜닝 메인 진입점입니다.

argparse로 세 가지 실행 모드를 지원합니다:
  - eval : 테스트셋을 로드하여 RAG 평가를 실행하고 보고서를 저장합니다.
  - ocr  : 스캔 PDF를 OCR + LLaVA로 처리하여 텍스트를 추출합니다.
  - tune : 청크 크기·k값·전략 실험을 실행하고 최적 설정을 찾습니다.

사용 예:
  python src/main.py --mode eval
  python src/main.py --mode ocr --pdf data/docs/scan.pdf
  python src/main.py --mode tune
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --- 상수 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_docs")
EVAL_OUTPUT_DIR: str = "./outputs/eval_results"


def _build_rag_chain_and_retriever() -> tuple:
    """ChromaDB와 Ollama를 연결한 RAG 체인과 리트리버를 생성합니다.

    환경 변수에서 설정을 읽어 ChromaDB 컬렉션에 연결하고 LangChain
    RetrievalQA 체인을 구성합니다.

    Returns:
        (chain, retriever) 튜플::

            chain: LangChain RetrievalQA 객체
            retriever: ChromaDB 기반 LangChain 리트리버

    Raises:
        RuntimeError: ChromaDB 연결 또는 체인 빌드 실패 시
        ImportError: langchain 관련 패키지 미설치 시
    """
    # --- Input ---
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        from langchain_community.vectorstores import Chroma
        from langchain_ollama import OllamaLLM
        from langchain.chains import RetrievalQA
        from langchain_community.embeddings import OllamaEmbeddings
    except ImportError as exc:
        raise ImportError(
            f"필수 패키지가 설치되지 않았습니다: {exc}\n"
            "pip install -r requirements.txt 명령어로 설치하십시오."
        ) from exc

    # --- Process ---
    try:
        embeddings = OllamaEmbeddings(
            model=EMBED_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = OllamaLLM(model=LLM_MODEL_NAME, base_url=OLLAMA_BASE_URL)
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
        )
    except Exception as exc:
        raise RuntimeError(
            f"RAG 체인 구성 중 오류가 발생했습니다: {exc}\n"
            "Ollama 서버가 실행 중이고 ChromaDB 경로가 올바른지 확인하십시오.\n"
            f"  OLLAMA_BASE_URL: {OLLAMA_BASE_URL}\n"
            f"  CHROMA_PERSIST_DIR: {CHROMA_PERSIST_DIR}"
        ) from exc

    # --- Output ---
    return chain, retriever


def run_eval_mode(testset_path: str) -> None:
    """평가 모드를 실행합니다.

    testset.json을 로드하여 RAG 체인으로 각 질문에 답변을 생성하고
    검색 정확도, 키워드 포함률, 할루시네이션 발생률을 측정합니다.
    결과는 outputs/eval_results/ 디렉토리에 저장됩니다.

    Args:
        testset_path: testset.json 파일 경로

    Raises:
        FileNotFoundError: testset.json 파일이 없는 경우
        RuntimeError: RAG 체인 구성 또는 평가 실패 시
    """
    # --- Input ---
    from evaluator import load_testset, run_evaluation, save_report

    print("\n[평가 모드] 테스트셋 로드 중...")
    testset = load_testset(testset_path)

    print("[평가 모드] RAG 체인 구성 중...")
    chain, retriever = _build_rag_chain_and_retriever()

    # --- Process ---
    eval_result = run_evaluation(testset, chain, retriever)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(EVAL_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(EVAL_OUTPUT_DIR, f"eval_report_{timestamp}.json")

    # --- Output ---
    save_report(eval_result, output_path)
    print(f"\n[평가 완료] 보고서 저장: {output_path}")


def run_ocr_mode(pdf_path: str) -> None:
    """OCR 모드를 실행합니다.

    지정된 스캔 PDF를 페이지별 이미지로 변환한 뒤 EasyOCR과 LLaVA로
    텍스트를 추출합니다. 결과는 콘솔에 출력되고 outputs/ocr_pages/ 에 저장됩니다.

    Args:
        pdf_path: 처리할 스캔 PDF 파일 경로

    Raises:
        FileNotFoundError: PDF 파일이 없는 경우
        RuntimeError: OCR 또는 LLaVA 처리 실패 시
    """
    # --- Input ---
    from ocr_hybrid import process_scanned_pdf

    if not Path(pdf_path).exists():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}\n"
            "--pdf 옵션에 올바른 경로를 입력하십시오."
        )

    print(f"\n[OCR 모드] PDF 처리 시작: {pdf_path}")

    # --- Process ---
    results = process_scanned_pdf(pdf_path)

    # --- Output ---
    total_text_chars = sum(len(r.get("combined_text", "")) for r in results)
    print(f"\n[OCR 완료] {len(results)}페이지 처리, 총 {total_text_chars}자 추출")
    for r in results:
        if r["status"] == "success":
            print(f"  페이지 {r['page']}: {len(r['combined_text'])}자")


def run_tune_mode() -> None:
    """튜닝 모드를 실행합니다.

    청크 크기, 오버랩, k값, 청킹 전략의 5가지 조합 실험을 순차 실행하고
    Precision@K와 응답 시간을 측정합니다. 결과는 outputs/tuning_logs/ 에 저장됩니다.

    Raises:
        RuntimeError: ChromaDB 또는 Ollama 연결 실패 시
    """
    # --- Input ---
    from tuning.chunker_tuning import run_all_experiments

    print("\n[튜닝 모드] 청크 튜닝 실험 시작...")

    # --- Process ---
    results = run_all_experiments()

    # --- Output ---
    print(f"\n[튜닝 완료] {len(results)}개 실험 완료")
    print("결과 파일: outputs/tuning_logs/")


def parse_args() -> argparse.Namespace:
    """커맨드라인 인수를 파싱합니다.

    Returns:
        파싱된 인수 네임스페이스 객체

    Raises:
        SystemExit: 필수 인수 누락 또는 --help 플래그 사용 시
    """
    # --- Input ---
    parser = argparse.ArgumentParser(
        description="CH10 RAG 시스템 튜닝 실습 예제",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "실행 예시:\n"
            "  python src/main.py --mode eval\n"
            "  python src/main.py --mode ocr --pdf data/docs/scan.pdf\n"
            "  python src/main.py --mode tune\n"
        ),
    )

    # --- Process ---
    parser.add_argument(
        "--mode",
        type=str,
        choices=["eval", "ocr", "tune"],
        required=True,
        help=(
            "실행 모드 선택:\n"
            "  eval  - 테스트셋 기반 RAG 시스템 평가\n"
            "  ocr   - 스캔 PDF OCR + LLaVA 처리\n"
            "  tune  - 청크 크기·k값 튜닝 실험"
        ),
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default="",
        help="OCR 모드에서 처리할 PDF 파일 경로 (--mode ocr 필수)",
    )
    parser.add_argument(
        "--testset",
        type=str,
        default=os.getenv("TESTSET_PATH", "./data/testset.json"),
        help="평가 모드에서 사용할 테스트셋 경로 (기본값: ./data/testset.json)",
    )

    # --- Output ---
    return parser.parse_args()


def main() -> None:
    """메인 진입점 함수입니다.

    커맨드라인 인수를 파싱하여 eval, ocr, tune 모드 중 하나를 실행합니다.
    오류 발생 시 메시지를 출력하고 비정상 종료합니다.

    Raises:
        SystemExit: 오류 발생 시 코드 1로 종료
    """
    # --- Input ---
    args = parse_args()

    print("=" * 60)
    print("CH10 RAG 시스템 튜닝")
    print(f"모드: {args.mode.upper()}")
    print(f"LLM: {LLM_MODEL_NAME}  |  임베딩: {EMBED_MODEL}")
    print("=" * 60)

    # --- Process ---
    try:
        if args.mode == "eval":
            run_eval_mode(args.testset)
        elif args.mode == "ocr":
            if not args.pdf:
                print("[오류] OCR 모드에서는 --pdf 옵션이 필요합니다.")
                print("  예시: python src/main.py --mode ocr --pdf data/docs/scan.pdf")
                sys.exit(1)
            run_ocr_mode(args.pdf)
        elif args.mode == "tune":
            run_tune_mode()
    except FileNotFoundError as exc:
        print(f"\n[파일 오류] {exc}")
        sys.exit(1)
    except (ImportError, RuntimeError) as exc:
        print(f"\n[실행 오류] {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[중단] 사용자가 실행을 중단했습니다.")
        sys.exit(0)

    # --- Output ---
    print("\n[완료] 모든 작업이 정상적으로 완료되었습니다.")


if __name__ == "__main__":
    main()
