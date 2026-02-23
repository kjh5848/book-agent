"""
ChromaDB 벡터 저장소 모듈.

PersistentClient를 사용하여 임베딩 벡터와 문서 메타데이터를
디스크에 영속적으로 저장하고, 코사인 유사도 기반 벡터 검색을 수행합니다.
인메모리(EphemeralClient) 방식이 아니므로 프로그램 재시작 후에도
저장된 데이터를 재사용할 수 있습니다.

부서 필터 기능:
    search()의 filter_dept 인수로 특정 부서의 문서만 검색할 수 있습니다.
    이 기능은 청크 메타데이터의 "department" 필드를 기준으로 동작합니다.
"""

import os
from collections import Counter

import chromadb
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
_DEFAULT_COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_docs")


def create_collection(
    persist_dir: str = _DEFAULT_PERSIST_DIR,
    name: str = _DEFAULT_COLLECTION_NAME,
) -> chromadb.Collection:
    """ChromaDB PersistentClient를 초기화하고 컬렉션을 반환합니다.

    지정된 디렉토리에 데이터를 영속 저장하는 클라이언트를 생성한 뒤,
    동일한 이름의 컬렉션이 있으면 재사용하고 없으면 새로 생성합니다.
    거리 함수는 코사인 유사도(cosine)를 사용합니다.

    Args:
        persist_dir: ChromaDB 데이터를 저장할 디렉토리 경로.
                     기본값은 환경 변수 CHROMA_PERSIST_DIR 값입니다.
        name: 컬렉션 이름. 기본값은 환경 변수 COLLECTION_NAME 값입니다.

    Returns:
        ChromaDB Collection 인스턴스.

    Raises:
        ValueError: name이 비어 있을 때.
        RuntimeError: ChromaDB 초기화 또는 컬렉션 생성 실패 시.
    """
    # --- Input ---
    collection_name = name.strip()
    if not collection_name:
        raise ValueError("컬렉션 이름이 비어 있습니다.")

    abs_persist_dir = os.path.abspath(persist_dir)
    os.makedirs(abs_persist_dir, exist_ok=True)

    # --- Process ---
    try:
        client = chromadb.PersistentClient(path=abs_persist_dir)
    except Exception as e:
        raise RuntimeError(
            f"ChromaDB 클라이언트 초기화에 실패했습니다 (경로: {abs_persist_dir}): {e}"
        )

    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as e:
        raise RuntimeError(
            f"ChromaDB 컬렉션 '{collection_name}' 생성/접근에 실패했습니다: {e}"
        )

    # --- Output ---
    print(f"  ChromaDB 초기화 완료: 경로={abs_persist_dir}")
    print(f"  컬렉션 '{collection_name}' 준비 완료 (현재 문서 수: {collection.count()})")
    return collection


def add_documents(
    collection: chromadb.Collection,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> int:
    """청크와 임베딩 벡터를 ChromaDB 컬렉션에 저장합니다.

    chunks와 embeddings는 동일한 인덱스 순서로 대응해야 합니다.
    chunk_id를 ChromaDB 문서 ID로 사용하며, 동일한 ID가 이미 존재하면 덮어씁니다(upsert).
    ChromaDB가 허용하는 메타데이터 타입(str, int, float, bool)으로 자동 변환합니다.

    Args:
        collection: create_collection()으로 생성한 ChromaDB Collection 인스턴스.
        chunks: chunker 모듈이 반환한 청크 딕셔너리 리스트.
                각 요소는 {"chunk_id": str, "text": str, "metadata": dict} 형태여야 합니다.
        embeddings: embedder 모듈이 반환한 임베딩 벡터 리스트.
                    chunks와 동일한 길이여야 합니다.

    Returns:
        저장 후 컬렉션의 총 문서 수 (int).

    Raises:
        ValueError: chunks 또는 embeddings가 비어 있을 때.
        ValueError: chunks와 embeddings의 길이가 다를 때.
        RuntimeError: ChromaDB에 문서 저장 중 오류 발생 시.
    """
    # --- Input ---
    if not chunks:
        raise ValueError("저장할 청크가 없습니다.")
    if not embeddings:
        raise ValueError("저장할 임베딩이 없습니다.")
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"청크 수({len(chunks)})와 임베딩 수({len(embeddings)})가 일치하지 않습니다."
        )

    # --- Process ---
    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # ChromaDB 허용 타입(str, int, float, bool)으로 변환
    safe_metadatas: list[dict] = []
    for meta in metadatas:
        safe_meta = {
            k: str(v) if not isinstance(v, (str, int, float, bool)) else v
            for k, v in meta.items()
        }
        safe_metadatas.append(safe_meta)

    try:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=safe_metadatas,
        )
    except Exception as e:
        raise RuntimeError(
            f"ChromaDB에 문서를 저장하는 중 오류가 발생했습니다: {e}"
        )

    total_count = collection.count()

    # --- Output ---
    print(f"  {len(chunks)}개 청크 저장 완료. 컬렉션 총 문서 수: {total_count}")
    return total_count


def search(
    collection: chromadb.Collection,
    query_embedding: list[float],
    k: int = 3,
    filter_dept: str | None = None,
) -> list[dict]:
    """쿼리 임베딩과 가장 유사한 문서를 벡터 검색합니다.

    ChromaDB의 코사인 유사도 기반 최근접 이웃 검색을 수행합니다.
    filter_dept를 지정하면 metadata.department 필드로 부서 필터를 적용합니다.

    Args:
        collection: 검색할 ChromaDB Collection 인스턴스.
        query_embedding: 검색 쿼리의 임베딩 벡터 (float 리스트).
        k: 반환할 최대 결과 수. 기본값은 3.
        filter_dept: 검색을 특정 부서로 제한할 때 사용합니다.
                     None이면 전체 컬렉션을 검색합니다.
                     예: "HR" → metadata.department == "HR" 인 문서만 검색.

    Returns:
        검색 결과 딕셔너리의 리스트. 유사도 높은 순(거리 낮은 순)으로 정렬됩니다.
        각 딕셔너리 구조:
            {
                "text": str,      # 매칭된 청크 텍스트
                "metadata": dict, # 문서 메타데이터
                "distance": float # 코사인 거리 (낮을수록 유사도 높음)
            }

    Raises:
        ValueError: query_embedding이 비어 있을 때.
        ValueError: k가 1보다 작을 때.
        RuntimeError: ChromaDB 검색 중 오류 발생 시.
    """
    # --- Input ---
    if not query_embedding:
        raise ValueError("쿼리 임베딩 벡터가 비어 있습니다.")
    if k < 1:
        raise ValueError(f"반환 결과 수 k는 1 이상이어야 합니다. 현재 값: {k}")

    # --- Process ---
    # 부서 필터 설정 (metadata.department 기준)
    where_filter = None
    if filter_dept is not None:
        where_filter = {"department": filter_dept}

    try:
        total_docs = collection.count()
        if total_docs == 0:
            return []

        query_params: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(k, total_docs),
            "include": ["documents", "metadatas", "distances"],
        }
        if where_filter:
            query_params["where"] = where_filter

        result = collection.query(**query_params)
    except Exception as e:
        raise RuntimeError(f"ChromaDB 검색 중 오류가 발생했습니다: {e}")

    # 응답 구조 파싱
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    search_results: list[dict] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        search_results.append(
            {
                "text": doc,
                "metadata": meta,
                "distance": round(dist, 6),
            }
        )

    # --- Output ---
    return search_results


def get_collection_stats(collection: chromadb.Collection) -> dict:
    """컬렉션의 통계 정보를 반환합니다.

    저장된 총 문서 수와 부서별 문서 분포를 계산하여 반환합니다.
    부서별 분포는 metadata.department 필드를 기준으로 집계합니다.

    Args:
        collection: 통계를 확인할 ChromaDB Collection 인스턴스.

    Returns:
        통계 딕셔너리:
            {
                "total_documents": int,        # 총 문서(청크) 수
                "department_distribution": dict # 부서별 문서 수 {department: count}
            }

    Raises:
        RuntimeError: 컬렉션 데이터를 읽는 중 오류 발생 시.
    """
    # --- Input ---
    total = collection.count()

    # --- Process ---
    department_distribution: dict[str, int] = {}

    if total > 0:
        try:
            all_docs = collection.get(include=["metadatas"])
            metadatas = all_docs.get("metadatas", [])
            departments = [m.get("department", "unknown") for m in metadatas]
            department_distribution = dict(Counter(departments))
        except Exception as e:
            raise RuntimeError(
                f"컬렉션 통계를 읽는 중 오류가 발생했습니다: {e}"
            )

    stats = {
        "total_documents": total,
        "department_distribution": department_distribution,
    }

    # --- Output ---
    return stats
