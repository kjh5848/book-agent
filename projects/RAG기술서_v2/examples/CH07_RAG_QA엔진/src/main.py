"""CH07 RAG Q&A 엔진 메인 진입점.

커넥트HR 사내 문서 기반 Q&A 시스템을 초기화하고 실행합니다.
ChromaDB가 비어있으면 샘플 문서로 자동 초기화합니다.

실행 방법:
    python src/main.py           # 채팅 인터페이스 실행
    python src/main.py --demo    # 5개 샘플 Q&A 자동 실행
"""

import argparse
import os
import sys
import time
from pathlib import Path

# 환경 변수 로드 (.env 파일 지원)
try:
    from dotenv import load_dotenv
    # main.py 기준 상위 디렉토리의 .env 파일 로드
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=str(env_path))
except ImportError:
    pass  # python-dotenv 없으면 환경 변수만 사용

# 현재 파일 위치를 sys.path에 추가 (같은 패키지 내 모듈 임포트용)
sys.path.insert(0, str(Path(__file__).parent))

from retriever import ChromaRetriever, _embed_query
from rag_chain import RAGChain
from chat_interface import run_chat_loop

# 환경 변수
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "connecthr_docs")

# 샘플 Q&A 목록 (--demo 모드)
DEMO_QUESTIONS: list[str] = [
    "연차 휴가는 몇 일 발생하나요?",
    "특별휴가 조건이 무엇인가요?",
    "재택근무 신청 방법을 알려주세요",
    "퇴직금 지급 기준은 어떻게 되나요?",
    "사내 보안 정책에서 금지하는 행위는 무엇인가요?",
]

# 샘플 문서 데이터 (ChromaDB가 비어있을 때 자동으로 로드)
SAMPLE_DOCUMENTS: list[dict] = [
    {
        "content": (
            "제3조 (연차 유급휴가) 1년 이상 근속한 직원에게는 연간 15일의 유급휴가를 부여합니다. "
            "3년 이상 근속 시 매 2년마다 1일씩 추가되어 최대 25일까지 적립됩니다. "
            "연차 휴가는 근로기준법 제60조를 따릅니다."
        ),
        "source": "HR_취업규칙_v1.0",
        "chunk_index": 3,
    },
    {
        "content": (
            "제4조 (특별 휴가) 다음 각 호에 해당하는 경우 특별 유급휴가를 부여합니다. "
            "1. 본인 결혼: 5일 2. 자녀 결혼: 2일 3. 배우자 출산: 10일 "
            "4. 부모 또는 배우자의 직계 가족 사망: 5일 5. 본인 회갑: 1일. "
            "특별 휴가는 사유 발생일로부터 30일 이내에 사용하여야 합니다."
        ),
        "source": "HR_취업규칙_v1.0",
        "chunk_index": 4,
    },
    {
        "content": (
            "제12조 (재택근무) 재택근무 신청은 팀장의 사전 승인이 필요합니다. "
            "신청 방법: 사내 HR 포털에서 '근무형태 변경 신청서'를 작성하고, "
            "최소 3영업일 전에 제출하십시오. "
            "재택근무 허용 직종: 개발, 기획, 디자인, 마케팅. "
            "현장 업무 직종(영업, 고객지원)은 대면 근무를 원칙으로 합니다."
        ),
        "source": "HR_취업규칙_v1.0",
        "chunk_index": 12,
    },
    {
        "content": (
            "제8조 (퇴직금) 1년 이상 근속한 직원이 퇴직할 경우, "
            "계속근로연수 1년에 대하여 30일분의 평균임금을 퇴직금으로 지급합니다. "
            "평균임금은 퇴직 전 3개월간의 임금 총액을 해당 기간의 총 일수로 나누어 산정합니다. "
            "퇴직금은 퇴직일로부터 14일 이내에 지급합니다."
        ),
        "source": "HR_취업규칙_v1.0",
        "chunk_index": 8,
    },
    {
        "content": (
            "제3조 (금지 행위) 임직원은 다음 행위를 하여서는 아니 됩니다. "
            "1. 업무 목적 이외의 사내 시스템 접속 및 정보 열람 "
            "2. 개인 단말기를 통한 사내망 무단 접속 "
            "3. 회사 기밀 정보의 외부 유출 또는 SNS 게시 "
            "4. 인가받지 않은 소프트웨어 설치 "
            "5. 타인의 계정 정보를 사용한 시스템 접근. "
            "위반 시 취업규칙에 따라 징계 처분될 수 있습니다."
        ),
        "source": "IT_정보보안_지침서",
        "chunk_index": 3,
    },
    {
        "content": (
            "제2조 (업무 시스템 사용 원칙) 업무용 시스템은 반드시 회사 지급 단말기를 사용하십시오. "
            "외부망에서 사내 시스템에 접속 시 반드시 VPN을 사용하여야 합니다. "
            "패스워드는 최소 8자 이상, 영문·숫자·특수문자를 조합하여 설정하고 "
            "90일마다 변경하여야 합니다."
        ),
        "source": "IT_정보보안_지침서",
        "chunk_index": 2,
    },
    {
        "content": (
            "제5조 (병가 및 의료비 지원) 업무상 질병 또는 부상으로 인한 병가는 최대 30일까지 유급으로 처리합니다. "
            "개인 질병의 경우 최초 3일은 유급, 이후 무급으로 처리됩니다. "
            "단, 의사의 진단서 제출이 필요합니다. "
            "의료비 지원: 연간 100만원 한도 내에서 실비 청구가 가능합니다."
        ),
        "source": "HR_복리후생_안내서",
        "chunk_index": 5,
    },
    {
        "content": (
            "신규 서비스 런칭 전략 (OPS_런칭전략_2025) "
            "1단계: 알파 테스트 (내부 팀 20명, 2주) "
            "2단계: 베타 테스트 (주요 고객사 5개, 1개월) "
            "3단계: 정식 출시 (전체 고객사 대상). "
            "각 단계별 성공 기준: 오류율 1% 이하, 응답 시간 2초 이하, 고객 만족도 4.0 이상."
        ),
        "source": "OPS_런칭전략_2025",
        "chunk_index": 1,
    },
]


def _initialize_sample_db(persist_dir: str, collection_name: str) -> bool:
    """ChromaDB에 샘플 문서를 초기화합니다.

    실습용 ChromaDB가 없을 때 자동으로 샘플 사내 문서를 임베딩하여 저장합니다.
    retriever._embed_query와 동일한 임베딩 전략(Ollama 우선, fallback: sentence-transformers)을
    사용하여 검색 시 차원 불일치를 방지합니다.

    Args:
        persist_dir: ChromaDB 저장 디렉토리 경로
        collection_name: 생성할 컬렉션 이름

    Returns:
        초기화 성공 시 True, 실패 시 False
    """

    # --- Input ---
    print("\n  [초기화] ChromaDB에 샘플 문서를 로드합니다...")
    print(f"  저장 경로: {persist_dir}")
    print(f"  컬렉션: {collection_name}")
    print(f"  문서 수: {len(SAMPLE_DOCUMENTS)}개")

    # --- Process ---
    try:
        import chromadb
    except ImportError:
        print("  [오류] chromadb 패키지가 없습니다. pip install chromadb")
        return False

    try:
        # ChromaDB 클라이언트 생성
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=persist_dir)

        # 기존 컬렉션 삭제 후 재생성
        try:
            client.delete_collection(name=collection_name)
            print(f"  기존 컬렉션 삭제: '{collection_name}'")
        except Exception:
            pass  # 컬렉션이 없어도 계속 진행

        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # retriever와 동일한 _embed_query 함수로 임베딩 생성
        # (Ollama 우선 → 실패 시 sentence-transformers, 차원 일관성 보장)
        print("  임베딩 생성 중 (retriever와 동일한 전략 사용)...")

        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict] = []

        for i, doc in enumerate(SAMPLE_DOCUMENTS):
            content = doc["content"]
            vector, engine = _embed_query(content)

            if i == 0:
                # 첫 번째 문서에서 사용된 엔진과 차원을 출력
                print(f"  임베딩 엔진: {engine}, 차원: {len(vector)}")

            ids.append(f"sample_{i:03d}")
            documents.append(content)
            embeddings.append(vector)
            metadatas.append({
                "source": doc["source"],
                "chunk_index": doc["chunk_index"],
                "char_count": len(content),
            })

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"  샘플 문서 {len(ids)}개 저장 완료.")

    except Exception as e:
        print(f"  [오류] ChromaDB 초기화 실패: {e}")
        return False

    # --- Output ---
    return True


def _check_or_initialize_db(persist_dir: str, collection_name: str) -> bool:
    """ChromaDB 컬렉션 존재 여부를 확인하고, 없으면 샘플 데이터로 초기화합니다.

    Args:
        persist_dir: ChromaDB 저장 디렉토리 경로
        collection_name: 확인할 컬렉션 이름

    Returns:
        사용 가능한 컬렉션이 있으면 True, 초기화 실패 시 False
    """

    # --- Input ---
    try:
        import chromadb
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_collection(name=collection_name)
        doc_count = collection.count()

        if doc_count > 0:
            print(f"  기존 ChromaDB 발견: '{collection_name}' ({doc_count}개 문서)")
            return True
        else:
            print("  컬렉션이 비어있습니다. 샘플 데이터로 초기화합니다.")
            return _initialize_sample_db(persist_dir, collection_name)

    except Exception:
        # 컬렉션이 없거나 DB가 없는 경우
        print("  ChromaDB 컬렉션을 찾을 수 없습니다. 샘플 데이터로 초기화합니다.")
        return _initialize_sample_db(persist_dir, collection_name)

    # --- Output ---
    # bool 반환


def run_demo_mode(rag_chain: RAGChain) -> None:
    """데모 모드: 5개 샘플 질문에 대한 자동 Q&A를 실행합니다.

    Args:
        rag_chain: 초기화된 RAGChain 인스턴스
    """

    # --- Input ---
    print("\n" + "=" * 60)
    print("  [데모 모드] 샘플 Q&A 자동 실행")
    print("=" * 60)

    # --- Process ---
    for i, question in enumerate(DEMO_QUESTIONS, start=1):
        print(f"\n[질문 {i}/{len(DEMO_QUESTIONS)}] {question}")
        print("-" * 60)

        start_time = time.time()
        result = rag_chain.invoke(question=question)
        elapsed = time.time() - start_time

        print(result["answer"])
        print(f"\n  응답 시간: {elapsed:.1f}초")
        print("=" * 60)

    # --- Output ---
    print("\n  데모 완료. 총 5개 질문 처리.")


def main() -> None:
    """메인 함수: 인자를 파싱하고 적절한 모드로 실행합니다."""

    # --- Input ---
    parser = argparse.ArgumentParser(
        description="커넥트HR 사내 문서 기반 RAG Q&A 엔진",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "실행 예시:\n"
            "  python src/main.py           # 채팅 인터페이스\n"
            "  python src/main.py --demo    # 샘플 Q&A 자동 실행\n"
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="5개 샘플 질문 자동 실행 후 종료",
    )
    args = parser.parse_args()

    # --- Process ---
    print("\n커넥트HR RAG Q&A 엔진 시작...")
    print(f"  ChromaDB 경로: {CHROMA_PERSIST_DIR}")
    print(f"  컬렉션: {CHROMA_COLLECTION}")

    # 1단계: ChromaDB 확인 및 초기화
    db_ready = _check_or_initialize_db(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION,
    )

    if not db_ready:
        print("\n  [오류] ChromaDB를 초기화할 수 없습니다.")
        print("  requirements.txt의 패키지가 모두 설치되었는지 확인하십시오.")
        sys.exit(1)

    # 2단계: ChromaRetriever 초기화
    try:
        retriever = ChromaRetriever(
            persist_dir=CHROMA_PERSIST_DIR,
            collection_name=CHROMA_COLLECTION,
        )
    except RuntimeError as e:
        print(f"\n  [오류] ChromaRetriever 초기화 실패:\n  {e}")
        sys.exit(1)

    # 3단계: RAG 체인 빌드
    rag_chain = RAGChain(retriever=retriever)

    # 4단계: 실행 모드 결정
    if args.demo:
        run_demo_mode(rag_chain=rag_chain)
    else:
        run_chat_loop(rag_chain=rag_chain)

    # --- Output ---
    # 프로그램 종료


if __name__ == "__main__":
    main()
