"""
Ollama 임베딩 모듈.

Ollama REST API를 직접 호출(requests)하여 텍스트를 벡터(float 리스트)로 변환합니다.
LangChain 등 추상화 라이브러리를 사용하지 않으므로 API 동작 원리를 직접 확인할 수 있습니다.

Ollama 서버가 로컬에서 실행 중이어야 합니다:
    ollama serve
    ollama pull nomic-embed-text

API 엔드포인트:
    POST {OLLAMA_BASE_URL}/api/embeddings
    payload: {"model": str, "prompt": str}
    response: {"embedding": list[float]}
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

_OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_DEFAULT_EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")

# 알려진 모델별 임베딩 차원 수 매핑
_MODEL_DIMENSIONS: dict[str, int] = {
    "nomic-embed-text": 768,
    "mxbai-embed-large": 1024,
    "all-minilm": 384,
    "nomic-embed-text:latest": 768,
}

# 배치 크기: 한 번에 처리할 최대 텍스트 수
_BATCH_SIZE: int = 10


def get_embedding_model(model_name: str = _DEFAULT_EMBED_MODEL) -> dict:
    """임베딩 모델 정보를 반환합니다.

    Ollama에서 제공하는 임베딩 모델의 이름과 벡터 차원 수를 반환합니다.
    알려지지 않은 모델은 차원 수를 0으로 반환합니다.

    Args:
        model_name: 사용할 Ollama 임베딩 모델 이름.
                    기본값은 환경 변수 EMBED_MODEL 값입니다.

    Returns:
        모델 정보 딕셔너리: {"model": str, "dimension": int}
    """
    # --- Input ---
    model = model_name.strip()

    # --- Process ---
    dimension = _MODEL_DIMENSIONS.get(model, 0)
    if dimension == 0:
        print(
            f"[경고] '{model}' 모델의 차원 수가 알려지지 않았습니다. "
            "실제 임베딩 호출 후 차원을 확인하십시오."
        )

    # --- Output ---
    return {"model": model, "dimension": dimension}


def embed_single(text: str, model_name: str = _DEFAULT_EMBED_MODEL) -> list[float]:
    """단일 텍스트를 Ollama REST API로 임베딩 벡터로 변환합니다.

    POST {OLLAMA_BASE_URL}/api/embeddings 엔드포인트를 직접 호출합니다.
    빈 텍스트는 허용하지 않으며, 네트워크 오류 시 명확한 안내 메시지를 출력합니다.

    Args:
        text: 임베딩할 텍스트 문자열.
        model_name: 사용할 Ollama 임베딩 모델 이름.
                    기본값은 환경 변수 EMBED_MODEL 값입니다.

    Returns:
        텍스트의 임베딩 벡터 (float 리스트).

    Raises:
        ValueError: text가 비어 있을 때.
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: Ollama API가 오류 응답을 반환했을 때.
    """
    # --- Input ---
    if not text or not text.strip():
        raise ValueError(
            "임베딩할 텍스트가 비어 있습니다. 청킹 결과를 확인하십시오."
        )

    url = f"{_OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": model_name, "prompt": text}

    # --- Process ---
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Ollama 서버({_OLLAMA_BASE_URL})에 연결할 수 없습니다.\n"
            "다음 명령으로 서버를 먼저 실행하십시오:\n"
            "  ollama serve"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama 서버 응답 시간이 초과되었습니다. "
            "서버 상태를 확인하거나 잠시 후 다시 시도하십시오."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama API 오류 (상태 코드: {response.status_code}): {response.text}"
        )

    result = response.json()
    embedding = result.get("embedding")
    if embedding is None:
        raise RuntimeError(
            f"Ollama API 응답에 'embedding' 필드가 없습니다.\n"
            f"응답 내용: {result}\n"
            f"모델 이름이 올바른지 확인하십시오: {model_name}"
        )

    # --- Output ---
    return embedding


def embed_texts(
    texts: list[str],
    model_name: str = _DEFAULT_EMBED_MODEL,
    batch_delay: float = 0.05,
) -> list[list[float]]:
    """텍스트 리스트를 배치로 임베딩하여 벡터 리스트를 반환합니다.

    _BATCH_SIZE(10개) 단위로 묶어 처리하며, 진행 상황을 표준 출력으로 보고합니다.
    (Ollama는 현재 단일 요청당 하나의 텍스트만 처리하므로 내부적으로는 순차 호출입니다.)

    Args:
        texts: 임베딩할 텍스트 문자열의 리스트.
        model_name: 사용할 Ollama 임베딩 모델 이름.
                    기본값은 환경 변수 EMBED_MODEL 값입니다.
        batch_delay: 배치 간 대기 시간(초). 서버 과부하 방지용. 기본값은 0.05초.

    Returns:
        각 텍스트에 대응하는 임베딩 벡터(float 리스트)의 리스트.
        입력 texts와 동일한 순서로 반환됩니다.

    Raises:
        ValueError: texts 리스트가 비어 있을 때.
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: 임베딩 과정에서 오류가 발생했을 때.
    """
    # --- Input ---
    if not texts:
        raise ValueError(
            "임베딩할 텍스트 리스트가 비어 있습니다. 청킹 결과를 확인하십시오."
        )

    embeddings: list[list[float]] = []
    total = len(texts)

    # --- Process ---
    print(f"  임베딩 시작: 총 {total}개 텍스트, 배치 크기={_BATCH_SIZE}, 모델={model_name}")

    # 배치 단위로 나눠 처리
    for batch_start in range(0, total, _BATCH_SIZE):
        batch_end = min(batch_start + _BATCH_SIZE, total)
        batch = texts[batch_start:batch_end]

        for idx_in_batch, text in enumerate(batch):
            global_idx = batch_start + idx_in_batch + 1
            try:
                embedding = embed_single(text, model_name=model_name)
                embeddings.append(embedding)
            except (ConnectionError, RuntimeError) as e:
                raise RuntimeError(
                    f"텍스트 {global_idx}/{total} 임베딩 중 오류가 발생했습니다: {e}"
                )

        # 배치 완료 후 진행 상황 출력
        completed = min(batch_end, total)
        print(f"    진행: {completed}/{total} ({completed / total * 100:.1f}%)")

        # 마지막 배치가 아니면 대기
        if batch_end < total:
            time.sleep(batch_delay)

    # --- Output ---
    dim = len(embeddings[0]) if embeddings else 0
    print(f"  임베딩 완료: {len(embeddings)}개 벡터, 차원={dim}")
    return embeddings
