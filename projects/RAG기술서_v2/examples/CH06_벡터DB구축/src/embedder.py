"""임베딩 생성 모듈.

텍스트 청크를 고차원 벡터로 변환합니다.
Ollama의 nomic-embed-text 모델을 1차 시도하고,
연결 실패 시 sentence-transformers(paraphrase-multilingual-MiniLM-L12-v2)로 대체합니다.
"""

import os
import time
from typing import Optional

from chunker import Chunk


# 환경 변수에서 Ollama 설정 로드
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# sentence-transformers fallback 모델
FALLBACK_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def _embed_with_ollama(texts: list[str]) -> Optional[list[list[float]]]:
    """Ollama API를 사용하여 텍스트 리스트를 임베딩합니다.

    Args:
        texts: 임베딩할 텍스트 문자열 리스트

    Returns:
        임베딩 벡터 리스트. Ollama 연결 실패 시 None을 반환합니다.
    """

    # --- Input ---
    try:
        import requests
    except ImportError:
        print("  [경고] requests 라이브러리가 없습니다. pip install requests")
        return None

    embeddings: list[list[float]] = []
    api_url = f"{OLLAMA_BASE_URL}/api/embeddings"

    # --- Process ---
    # 연결 가능 여부 사전 확인
    try:
        health_resp = requests.get(OLLAMA_BASE_URL, timeout=3)
        if health_resp.status_code != 200:
            print(f"  [경고] Ollama 서버 응답 이상: {health_resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"  [정보] Ollama 서버에 연결할 수 없습니다: {OLLAMA_BASE_URL}")
        print("  Ollama가 실행 중인지 확인하거나 sentence-transformers로 대체됩니다.")
        return None
    except requests.exceptions.Timeout:
        print("  [정보] Ollama 연결 시간 초과. sentence-transformers로 대체됩니다.")
        return None

    for i, text in enumerate(texts):
        if not text.strip():
            # 빈 텍스트는 0벡터로 대체
            embeddings.append([0.0] * 768)
            continue

        try:
            resp = requests.post(
                api_url,
                json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            embedding = data.get("embedding")
            if embedding is None:
                print(f"  [경고] Ollama 응답에 embedding 키가 없습니다. (청크 {i})")
                return None
            embeddings.append(embedding)

        except requests.exceptions.HTTPError as e:
            if "404" in str(e):
                print(f"  [경고] Ollama 모델 '{OLLAMA_EMBED_MODEL}'을 찾을 수 없습니다.")
                print(f"  다음 명령어로 모델을 다운로드하십시오: ollama pull {OLLAMA_EMBED_MODEL}")
            else:
                print(f"  [경고] Ollama API 오류: {e}")
            return None
        except Exception as e:
            print(f"  [경고] Ollama 임베딩 실패: {e}")
            return None

    # --- Output ---
    return embeddings


def _embed_with_sentence_transformers(texts: list[str]) -> list[list[float]]:
    """sentence-transformers를 사용하여 텍스트 리스트를 임베딩합니다.

    Ollama를 사용할 수 없을 때의 대체 방법입니다.
    한국어 지원 다국어 모델(paraphrase-multilingual-MiniLM-L12-v2)을 사용합니다.

    Args:
        texts: 임베딩할 텍스트 문자열 리스트

    Returns:
        임베딩 벡터 리스트 (384차원)

    Raises:
        RuntimeError: sentence-transformers 설치 실패 또는 모델 로드 실패 시
    """

    # --- Input ---
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError(
            "sentence-transformers가 설치되지 않았습니다.\n"
            "다음 명령어로 설치하십시오: pip install sentence-transformers"
        )

    # --- Process ---
    print(f"  [Fallback] sentence-transformers 모델 로딩: {FALLBACK_MODEL}")
    print("  (최초 실행 시 모델 다운로드로 수 분이 소요될 수 있습니다)")

    try:
        model = SentenceTransformer(FALLBACK_MODEL)
    except Exception as e:
        raise RuntimeError(
            f"sentence-transformers 모델 로드 실패: {FALLBACK_MODEL}\n"
            f"오류: {e}"
        ) from e

    # 빈 텍스트 처리
    clean_texts = [t if t.strip() else " " for t in texts]

    try:
        vectors = model.encode(clean_texts, show_progress_bar=True, convert_to_numpy=True)
    except Exception as e:
        raise RuntimeError(
            f"sentence-transformers 임베딩 실패\n오류: {e}"
        ) from e

    # --- Output ---
    return [v.tolist() for v in vectors]


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """청크 리스트를 임베딩 벡터 리스트로 변환합니다.

    Ollama nomic-embed-text를 1차 시도합니다.
    Ollama가 연결되지 않으면 sentence-transformers로 자동 대체합니다.

    Args:
        chunks: Chunk 객체 리스트

    Returns:
        임베딩 벡터 리스트. 각 원소는 청크에 대응하는 부동소수점 벡터입니다.

    Raises:
        RuntimeError: 모든 임베딩 방법이 실패할 경우
        ValueError: 청크 리스트가 비어있을 경우
    """

    # --- Input ---
    if not chunks:
        raise ValueError(
            "임베딩할 청크가 없습니다.\n"
            "청킹 단계가 올바르게 완료되었는지 확인하십시오."
        )

    texts = [chunk.text for chunk in chunks]
    print(f"  임베딩 시작: {len(texts)}개 청크")

    # --- Process ---
    # 1차 시도: Ollama
    print(f"  [1차 시도] Ollama ({OLLAMA_EMBED_MODEL}) 연결 확인...")
    start_time = time.time()
    embeddings = _embed_with_ollama(texts)

    if embeddings is not None:
        elapsed = time.time() - start_time
        dim = len(embeddings[0]) if embeddings else 0
        print(f"  [Ollama] 임베딩 완료: {len(embeddings)}개, {dim}차원, {elapsed:.1f}초")
    else:
        # 2차 시도: sentence-transformers
        print("  [2차 시도] sentence-transformers로 대체합니다...")
        start_time = time.time()
        embeddings = _embed_with_sentence_transformers(texts)
        elapsed = time.time() - start_time
        dim = len(embeddings[0]) if embeddings else 0
        print(f"  [sentence-transformers] 임베딩 완료: {len(embeddings)}개, {dim}차원, {elapsed:.1f}초")

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"임베딩 수({len(embeddings)})와 청크 수({len(chunks)})가 일치하지 않습니다.\n"
            "임베딩 과정 중 오류가 발생했을 가능성이 있습니다."
        )

    # --- Output ---
    return embeddings


def get_embedding_dim(embeddings: list[list[float]]) -> int:
    """임베딩 벡터의 차원 수를 반환합니다.

    Args:
        embeddings: 임베딩 벡터 리스트

    Returns:
        임베딩 차원 수. 리스트가 비어있으면 0을 반환합니다.
    """

    if not embeddings:
        return 0
    return len(embeddings[0])


if __name__ == "__main__":
    from pathlib import Path
    from chunker import chunk_document

    base_dir = Path(__file__).parent.parent
    sample_file = base_dir / "data" / "sample_docs" / "leave_rules.txt"

    if not sample_file.exists():
        print(f"샘플 파일이 없습니다: {sample_file}")
    else:
        text = sample_file.read_text(encoding="utf-8")
        chunks = chunk_document(text, source=sample_file.name, strategy="fixed", chunk_size=300)
        print(f"청크 수: {len(chunks)}")

        # 처음 3개만 테스트
        test_chunks = chunks[:3]
        print(f"\n임베딩 테스트: {len(test_chunks)}개 청크")
        embeddings = embed_chunks(test_chunks)
        print(f"임베딩 차원: {get_embedding_dim(embeddings)}")
        print(f"첫 번째 벡터 (앞 5개 값): {embeddings[0][:5]}")
