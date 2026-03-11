"""ChromaDB 저장 및 검색 모듈.

ChromaDB 로컬 파일 기반으로 벡터와 메타데이터를 저장하고 유사도 검색을 수행합니다.
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from chunker import Chunk


# 환경 변수에서 ChromaDB 저장 경로 로드
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")


class ChromaStore:
    """ChromaDB 로컬 저장소 클래스.

    ChromaDB 컬렉션의 생성, 문서 추가, 유사도 검색, 통계 조회를 담당합니다.

    Attributes:
        persist_dir: ChromaDB 파일이 저장되는 로컬 디렉토리 경로
        client: ChromaDB 클라이언트 인스턴스
        collection: 현재 활성화된 컬렉션
        collection_name: 현재 컬렉션 이름
    """

    def __init__(self, persist_dir: Optional[str] = None) -> None:
        """ChromaStore를 초기화합니다.

        Args:
            persist_dir: ChromaDB 저장 디렉토리 경로.
                None이면 환경 변수 CHROMA_PERSIST_DIR 값을 사용합니다.

        Raises:
            RuntimeError: chromadb 패키지가 설치되지 않은 경우
            OSError: 저장 디렉토리를 생성할 수 없는 경우
        """

        # --- Input ---
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.collection = None
        self.collection_name = ""

        # --- Process ---
        # 저장 디렉토리 생성
        dir_path = Path(self.persist_dir)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(
                f"ChromaDB 저장 디렉토리를 생성할 수 없습니다: {self.persist_dir}\n"
                f"디렉토리 권한을 확인하십시오. 오류: {e}"
            ) from e

        # ChromaDB 클라이언트 초기화
        try:
            import chromadb

            self.client = chromadb.PersistentClient(path=str(dir_path))
        except ImportError:
            raise RuntimeError(
                "chromadb가 설치되지 않았습니다.\n"
                "다음 명령어로 설치하십시오: pip install chromadb"
            )

        print(f"  ChromaDB 초기화 완료: {self.persist_dir}")

    def create_collection(self, name: str) -> None:
        """컬렉션을 생성하거나 기존 컬렉션을 로드합니다.

        동일한 이름의 컬렉션이 이미 존재하면 기존 컬렉션을 로드합니다.
        임베딩 함수는 사용하지 않습니다 (외부에서 임베딩을 주입하는 방식).

        Args:
            name: 컬렉션 이름. 영문, 숫자, 하이픈, 언더스코어만 허용됩니다.

        Raises:
            ValueError: 컬렉션 이름이 비어있는 경우
        """

        # --- Input ---
        if not name or not name.strip():
            raise ValueError(
                "컬렉션 이름이 비어있습니다.\n"
                "유효한 이름을 입력하십시오. 예: 'connecthr_docs'"
            )

        # --- Process ---
        try:
            # get_or_create_collection: 없으면 생성, 있으면 기존 컬렉션 반환
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},  # 코사인 유사도 사용
            )
            self.collection_name = name

            existing_count = self.collection.count()
            if existing_count > 0:
                print(f"  기존 컬렉션 로드: '{name}' ({existing_count}개 문서)")
            else:
                print(f"  새 컬렉션 생성: '{name}'")

        except Exception as e:
            raise RuntimeError(
                f"컬렉션 생성/로드 실패: '{name}'\n오류: {e}"
            ) from e

        # --- Output ---
        # self.collection에 컬렉션 인스턴스가 설정됨

    def add_documents(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        metadatas: Optional[list[dict]] = None,
    ) -> int:
        """청크와 임베딩 벡터를 ChromaDB에 저장합니다.

        Args:
            chunks: 저장할 Chunk 객체 리스트
            embeddings: 각 청크에 대응하는 임베딩 벡터 리스트
            metadatas: 추가 메타데이터 딕셔너리 리스트 (None이면 기본 메타데이터만 사용)

        Returns:
            성공적으로 저장된 문서 수

        Raises:
            RuntimeError: 컬렉션이 생성되지 않은 경우
            ValueError: chunks와 embeddings의 수가 맞지 않는 경우
        """

        # --- Input ---
        if self.collection is None:
            raise RuntimeError(
                "컬렉션이 없습니다. add_documents() 전에 create_collection()을 호출하십시오."
            )
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"청크 수({len(chunks)})와 임베딩 수({len(embeddings)})가 일치하지 않습니다."
            )
        if not chunks:
            print("  [경고] 저장할 청크가 없습니다.")
            return 0

        # --- Process ---
        ids: list[str] = []
        documents: list[str] = []
        meta_list: list[dict] = []

        for i, chunk in enumerate(chunks):
            # 고유 ID 생성: source + index 기반
            doc_id = f"{chunk.source}_{chunk.index}_{uuid.uuid4().hex[:8]}"
            ids.append(doc_id)
            documents.append(chunk.text)

            # 기본 메타데이터 구성
            meta = {
                "source": chunk.source,
                "chunk_index": chunk.index,
                "strategy": chunk.strategy,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
                "char_count": len(chunk.text),
            }
            # 추가 메타데이터 병합
            if metadatas and i < len(metadatas):
                meta.update(metadatas[i])
            meta_list.append(meta)

        # ChromaDB에 배치 저장 (한 번에 최대 5,000개)
        batch_size = 5000
        saved_count = 0

        for batch_start in range(0, len(ids), batch_size):
            batch_end = min(batch_start + batch_size, len(ids))
            try:
                self.collection.add(
                    ids=ids[batch_start:batch_end],
                    embeddings=embeddings[batch_start:batch_end],
                    documents=documents[batch_start:batch_end],
                    metadatas=meta_list[batch_start:batch_end],
                )
                saved_count += batch_end - batch_start
            except Exception as e:
                raise RuntimeError(
                    f"ChromaDB 저장 실패 (배치 {batch_start}~{batch_end})\n오류: {e}"
                ) from e

        # --- Output ---
        print(f"  저장 완료: {saved_count}개 청크 → '{self.collection_name}'")
        return saved_count

    def search(
        self,
        query: str,
        query_embedding: list[float],
        n_results: int = 3,
    ) -> list[dict]:
        """쿼리 임베딩으로 유사한 청크를 검색합니다.

        Args:
            query: 원본 쿼리 텍스트 (표시용)
            query_embedding: 쿼리 텍스트의 임베딩 벡터
            n_results: 반환할 결과 수 (기본값: 3)

        Returns:
            검색 결과 딕셔너리 리스트.
            각 원소는 {"text": str, "source": str, "distance": float, "metadata": dict}를 포함합니다.

        Raises:
            RuntimeError: 컬렉션이 생성되지 않은 경우
        """

        # --- Input ---
        if self.collection is None:
            raise RuntimeError(
                "컬렉션이 없습니다. 검색 전에 create_collection()을 호출하십시오."
            )
        if not query_embedding:
            raise ValueError("쿼리 임베딩이 비어있습니다.")

        # 저장된 문서 수보다 많이 요청하지 않도록 제한
        actual_n = min(n_results, self.collection.count())
        if actual_n == 0:
            print("  [경고] 컬렉션에 저장된 문서가 없습니다.")
            return []

        # --- Process ---
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB 검색 실패\n쿼리: '{query}'\n오류: {e}"
            ) from e

        # 결과 정리
        formatted_results: list[dict] = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            formatted_results.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "distance": dist,
                "similarity": 1 - dist,  # 코사인 거리 → 유사도
                "metadata": meta,
            })

        # --- Output ---
        return formatted_results

    def get_collection_stats(self) -> dict:
        """현재 컬렉션의 통계 정보를 반환합니다.

        Returns:
            통계 딕셔너리:
            - name: 컬렉션 이름
            - total_docs: 저장된 문서(청크) 수
            - persist_dir: 저장 경로

        Raises:
            RuntimeError: 컬렉션이 생성되지 않은 경우
        """

        # --- Input ---
        if self.collection is None:
            raise RuntimeError(
                "컬렉션이 없습니다. create_collection()을 먼저 호출하십시오."
            )

        # --- Process ---
        total_docs = self.collection.count()

        stats = {
            "name": self.collection_name,
            "total_docs": total_docs,
            "persist_dir": self.persist_dir,
        }

        # --- Output ---
        print(f"\n{'=' * 40}")
        print(f"컬렉션 통계: '{self.collection_name}'")
        print(f"{'=' * 40}")
        print(f"저장된 청크 수 : {total_docs:,}개")
        print(f"저장 경로       : {self.persist_dir}")
        print(f"{'=' * 40}")

        return stats

    def delete_collection(self, name: str) -> None:
        """지정한 이름의 컬렉션을 삭제합니다.

        Args:
            name: 삭제할 컬렉션 이름

        Raises:
            RuntimeError: 컬렉션이 존재하지 않거나 삭제 실패 시
        """

        # --- Input / Process ---
        try:
            self.client.delete_collection(name=name)
            if self.collection_name == name:
                self.collection = None
                self.collection_name = ""
            print(f"  컬렉션 삭제 완료: '{name}'")
        except Exception as e:
            raise RuntimeError(
                f"컬렉션 삭제 실패: '{name}'\n오류: {e}"
            ) from e

        # --- Output ---
        # 컬렉션이 삭제됨


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 간단한 저장/검색 동작 확인
    print("=== ChromaStore 동작 확인 ===")
    base_dir = Path(__file__).parent.parent

    store = ChromaStore(persist_dir=str(base_dir / "outputs" / "chroma_test"))
    store.create_collection("test_collection")

    # 더미 청크와 임베딩으로 테스트
    from chunker import Chunk

    test_chunk = Chunk(
        text="연차 휴가는 근로기준법 제60조에 따라 발생합니다.",
        index=0,
        source="test.txt",
        strategy="fixed",
    )
    dummy_embedding = [0.1] * 384  # 더미 벡터

    saved = store.add_documents([test_chunk], [dummy_embedding])
    print(f"저장된 청크 수: {saved}")
    store.get_collection_stats()

    # 정리
    store.delete_collection("test_collection")
