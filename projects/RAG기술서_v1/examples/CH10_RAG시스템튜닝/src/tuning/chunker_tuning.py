"""청크 크기 및 k값 튜닝 실험 모듈입니다.

다양한 청킹 설정으로 ChromaDB를 재구축하고 검색 정확도를 비교합니다.
"""

import os
import time
import json
import logging
from dataclasses import dataclass, asdict
from typing import Any

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- 상수 ---
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TUNING_LOGS_DIR: str = "./outputs/tuning_logs"

# 실험에 사용할 샘플 문서 (ChromaDB가 비어 있을 때 자동 삽입)
SAMPLE_DOCUMENTS: list[str] = [
    "연차 신청은 전월 말일까지 팀장에게 제출해야 합니다. 긴급한 경우 3일 전 구두 보고 후 사후 제출이 가능합니다.",
    "병가 사용 시 의사 진단서를 3일 이내에 인사팀에 제출해야 합니다. 연속 5일 이상은 병원 입원 확인서가 필요합니다.",
    "재택근무는 주 2회까지 허용됩니다. 팀장 사전 승인이 필요하며 코어 타임(10시~16시)은 온라인 상태를 유지해야 합니다.",
    "신규 입사자는 수습 기간 3개월 동안 연차를 사용할 수 없습니다. 수습 종료 후 잔여 연차가 부여됩니다.",
    "육아휴직은 자녀 만 8세 또는 초등학교 2학년 이하인 경우 최대 1년 사용 가능합니다. 배우자 출산 휴가는 10일입니다.",
    "성과 평가는 연 2회(6월, 12월) 진행되며 S/A/B/C/D 5등급으로 평가합니다. S등급은 전체 10% 이내입니다.",
    "교육 지원 제도로 연간 100만원 한도 내에서 직무 관련 강의, 자격증 취득 비용을 지원합니다.",
    "사내 복지몰은 매월 10만 포인트가 지급되며 미사용 포인트는 다음 달로 이월되지 않습니다.",
    "출장비 정산은 출장 완료 후 7일 이내에 법인카드 영수증과 함께 경리팀에 제출해야 합니다.",
    "보안 규정에 따라 업무용 노트북을 외부로 반출할 때는 보안팀 사전 승인이 필요합니다.",
    "신규 서비스 런칭 전 최소 2주 전에 운영팀에 런칭 계획서를 제출해야 합니다.",
    "인프라 변경 사항은 변경 관리 위원회(CAB) 승인 후 적용합니다. 긴급 변경은 사후 승인도 가능합니다.",
    "장애 발생 시 15분 이내에 NOC에 보고하고, 1시간 이내에 원인 분석 보고서를 제출합니다.",
    "개인정보 처리 시스템 접근 권한은 6개월마다 재검토하며 불필요한 권한은 즉시 회수합니다.",
    "재무 보고서는 분기 마감 후 15영업일 이내에 이사회에 제출해야 합니다.",
]


@dataclass
class ChunkExperiment:
    """청킹 실험 설정 데이터 클래스입니다.

    Attributes:
        chunk_size: 각 청크의 최대 문자 수
        overlap: 인접 청크 간 중복 문자 수
        k: 검색 시 반환할 상위 문서 수
        strategy: 청킹 전략 ("fixed" 또는 "semantic")
    """

    chunk_size: int
    overlap: int
    k: int
    strategy: str


# 실험 목록 정의
EXPERIMENTS: list[ChunkExperiment] = [
    ChunkExperiment(chunk_size=200, overlap=20, k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50, k=3, strategy="fixed"),   # 기본값
    ChunkExperiment(chunk_size=800, overlap=100, k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50, k=5, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50, k=3, strategy="semantic"),
]


def _split_fixed_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """고정 크기로 텍스트를 청크로 분할합니다.

    Args:
        text: 분할할 원본 텍스트
        chunk_size: 각 청크의 최대 문자 수
        overlap: 인접 청크 간 중복 문자 수

    Returns:
        분할된 텍스트 청크 리스트
    """
    # --- Input ---
    if not text:
        return []

    # --- Process ---
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    # --- Output ---
    return chunks


def _split_semantic_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """문장 경계를 기준으로 의미 단위 청크를 생성합니다.

    Args:
        text: 분할할 원본 텍스트
        chunk_size: 각 청크의 최대 문자 수
        overlap: 인접 청크 간 중복 문자 수

    Returns:
        의미 단위로 분할된 텍스트 청크 리스트
    """
    # --- Input ---
    if not text:
        return []

    # --- Process ---
    sentences = [s.strip() for s in text.replace("。", ".").split(".") if s.strip()]
    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        candidate = current_chunk + (" " if current_chunk else "") + sentence + "."
        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "."

    if current_chunk:
        chunks.append(current_chunk.strip())

    # overlap 적용: 앞 청크 마지막 overlap 글자를 다음 청크 앞에 붙임
    if overlap > 0 and len(chunks) > 1:
        overlapped_chunks: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prefix = chunks[i - 1][-overlap:]
            overlapped_chunks.append(prefix + " " + chunks[i])
        return overlapped_chunks

    # --- Output ---
    return chunks


def _build_collection(
    experiment: ChunkExperiment,
    documents: list[str],
    collection_name: str = "tuning_exp",
) -> chromadb.Collection:
    """실험 설정으로 ChromaDB 컬렉션을 구축합니다.

    Args:
        experiment: 청킹 실험 설정
        documents: 인덱싱할 원본 문서 리스트
        collection_name: ChromaDB 컬렉션 이름

    Returns:
        구축된 ChromaDB 컬렉션 객체

    Raises:
        RuntimeError: ChromaDB 초기화 또는 문서 삽입 실패 시
    """
    # --- Input ---
    all_chunks: list[str] = []
    for doc in documents:
        if experiment.strategy == "semantic":
            chunks = _split_semantic_chunks(doc, experiment.chunk_size, experiment.overlap)
        else:
            chunks = _split_fixed_chunks(doc, experiment.chunk_size, experiment.overlap)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise RuntimeError("청크 분할 결과가 비어 있습니다. 입력 문서를 확인하십시오.")

    # --- Process ---
    try:
        ef = embedding_functions.OllamaEmbeddingFunction(
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
            model_name=EMBED_MODEL,
        )
        client = chromadb.EphemeralClient()
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef,
        )
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]
        collection.add(documents=all_chunks, ids=ids)
    except Exception as exc:
        raise RuntimeError(
            f"ChromaDB 컬렉션 구축 중 오류가 발생했습니다: {exc}\n"
            "Ollama 서버가 실행 중인지 확인하고 nomic-embed-text 모델이 설치됐는지 확인하십시오."
        ) from exc

    # --- Output ---
    return collection


def _compute_precision_at_k(
    collection: chromadb.Collection,
    questions: list[str],
    ground_truth_docs: list[str],
    k: int,
) -> float:
    """Precision@K 지표를 계산합니다.

    Args:
        collection: 검색 대상 ChromaDB 컬렉션
        questions: 테스트 질문 리스트
        ground_truth_docs: 각 질문에 대한 정답 문서 텍스트 리스트
        k: 검색 상위 k개 문서

    Returns:
        Precision@K 값 (0.0 ~ 1.0)

    Raises:
        ValueError: questions와 ground_truth_docs 길이가 다를 경우
    """
    # --- Input ---
    if len(questions) != len(ground_truth_docs):
        raise ValueError(
            f"질문 수({len(questions)})와 정답 문서 수({len(ground_truth_docs)})가 일치해야 합니다."
        )

    # --- Process ---
    correct = 0
    for question, ground_truth in zip(questions, ground_truth_docs):
        try:
            results = collection.query(query_texts=[question], n_results=min(k, collection.count()))
            retrieved = results.get("documents", [[]])[0]
            # 정답 문서의 핵심 키워드가 검색된 문서 중 하나에 포함되면 정답
            keywords = ground_truth.split()[:5]
            for doc in retrieved:
                if any(kw in doc for kw in keywords):
                    correct += 1
                    break
        except Exception as exc:
            logger.warning("질문 검색 중 오류 발생 (건너뜀): %s", exc)

    # --- Output ---
    return correct / len(questions) if questions else 0.0


def run_chunk_experiment(
    experiment: ChunkExperiment,
    test_questions: list[str],
    ground_truth_docs: list[str],
) -> dict[str, Any]:
    """청킹 설정을 변경하여 검색 정확도를 측정합니다.

    ChromaDB를 해당 설정으로 재구축한 뒤 테스트 질문으로 검색을 실행하고
    정답 문서 포함 여부로 Precision@K를 계산합니다.

    Args:
        experiment: 청킹 실험 설정 (크기, 오버랩, k값, 전략)
        test_questions: 검색 테스트에 사용할 질문 리스트
        ground_truth_docs: 각 질문에 대한 정답 문서 텍스트 리스트

    Returns:
        실험 결과 딕셔너리::

            {
                "experiment": dict,        # ChunkExperiment 설정값
                "precision_at_k": float,   # 상위 k개 중 정답 포함 비율
                "avg_response_ms": float   # 평균 검색 응답 시간(ms)
            }

    Raises:
        RuntimeError: ChromaDB 컬렉션 구축 실패 시
    """
    # --- Input ---
    print(
        f"\n[실험] chunk_size={experiment.chunk_size}, overlap={experiment.overlap}, "
        f"k={experiment.k}, strategy={experiment.strategy}"
    )

    # --- Process ---
    collection = _build_collection(experiment, SAMPLE_DOCUMENTS)

    response_times: list[float] = []
    for question in test_questions:
        start_ms = time.perf_counter()
        try:
            collection.query(
                query_texts=[question],
                n_results=min(experiment.k, collection.count()),
            )
        except Exception as exc:
            logger.warning("검색 응답 시간 측정 중 오류 (건너뜀): %s", exc)
        elapsed_ms = (time.perf_counter() - start_ms) * 1000
        response_times.append(elapsed_ms)

    precision = _compute_precision_at_k(
        collection, test_questions, ground_truth_docs, experiment.k
    )
    avg_ms = sum(response_times) / len(response_times) if response_times else 0.0

    # --- Output ---
    result = {
        "experiment": asdict(experiment),
        "precision_at_k": round(precision, 4),
        "avg_response_ms": round(avg_ms, 2),
    }
    print(f"  Precision@{experiment.k}: {precision:.1%}  |  평균 응답: {avg_ms:.1f}ms")
    return result


def run_all_experiments() -> list[dict[str, Any]]:
    """모든 청킹 실험을 순차 실행하고 결과를 저장합니다.

    EXPERIMENTS 목록의 모든 설정에 대해 run_chunk_experiment를 실행하고
    결과를 outputs/tuning_logs 디렉토리에 JSON 파일로 저장합니다.

    Returns:
        각 실험의 결과 딕셔너리 리스트
    """
    # --- Input ---
    test_questions = [
        "연차 신청은 며칠 전에 해야 합니까?",
        "재택근무는 몇 회까지 가능합니까?",
        "병가 사용 시 필요한 서류는 무엇입니까?",
        "성과 평가는 몇 등급입니까?",
        "출장비 정산 기한은 언제입니까?",
    ]
    ground_truth_docs = [
        "연차 신청은 전월 말일까지 팀장에게 제출해야 합니다.",
        "재택근무는 주 2회까지 허용됩니다.",
        "병가 사용 시 의사 진단서를 3일 이내에 인사팀에 제출해야 합니다.",
        "성과 평가는 연 2회 진행되며 S/A/B/C/D 5등급으로 평가합니다.",
        "출장비 정산은 출장 완료 후 7일 이내에 법인카드 영수증과 함께 제출해야 합니다.",
    ]

    # --- Process ---
    print("=" * 60)
    print("청크 튜닝 실험 시작")
    print("=" * 60)

    all_results: list[dict[str, Any]] = []
    for experiment in EXPERIMENTS:
        try:
            result = run_chunk_experiment(experiment, test_questions, ground_truth_docs)
            all_results.append(result)
        except RuntimeError as exc:
            logger.error("실험 실패: %s", exc)
            all_results.append({
                "experiment": asdict(experiment),
                "error": str(exc),
                "precision_at_k": 0.0,
                "avg_response_ms": 0.0,
            })

    # 결과 저장
    os.makedirs(TUNING_LOGS_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(TUNING_LOGS_DIR, f"chunk_tuning_{timestamp}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # --- Output ---
    print("\n" + "=" * 60)
    print("실험 결과 요약")
    print("=" * 60)
    best = max(all_results, key=lambda r: r.get("precision_at_k", 0.0))
    best_exp = best["experiment"]
    print(
        f"최고 설정: chunk_size={best_exp['chunk_size']}, "
        f"overlap={best_exp['overlap']}, k={best_exp['k']}, "
        f"strategy={best_exp['strategy']}"
    )
    print(f"Precision@K: {best['precision_at_k']:.1%}")
    print(f"결과 저장: {output_path}")
    return all_results
