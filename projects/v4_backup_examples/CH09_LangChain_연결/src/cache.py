"""
CH09 LangChain 연결 전략 — 응답 캐시 및 임베딩 캐시.

TTL 기반 응답 캐시와 로컬 파일 기반 임베딩 캐시를 제공합니다.
동일한 요청에 대해 LLM 재호출 없이 저장된 결과를 반환하여 비용과 지연 시간을 줄입니다.
"""

import hashlib
import json
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# --- 기본 설정 상수 ---
DEFAULT_RESPONSE_TTL: int = 3600        # 응답 캐시 TTL (초): 1시간
DEFAULT_EMBEDDING_CACHE_DIR: str = "./outputs/embedding_cache"
DEFAULT_RESPONSE_CACHE_MAX_SIZE: int = 1000  # 최대 캐시 항목 수


class ResponseCache:
    """TTL 기반 인메모리 응답 캐시.

    동일한 질문에 대한 LLM 응답을 일정 시간 동안 저장하여 재사용합니다.
    메모리 기반이므로 프로세스 재시작 시 초기화됩니다.

    Attributes:
        ttl: 캐시 유효 시간 (초)
        max_size: 최대 저장 항목 수
        _store: 내부 캐시 딕셔너리 {키: (값, 만료 타임스탬프)}
        _hits: 캐시 적중 횟수
        _misses: 캐시 미적중 횟수
    """

    def __init__(self, ttl: int = DEFAULT_RESPONSE_TTL, max_size: int = DEFAULT_RESPONSE_CACHE_MAX_SIZE) -> None:
        """ResponseCache를 초기화합니다.

        Args:
            ttl: 캐시 유효 시간 (초). 기본값은 3600초(1시간).
            max_size: 최대 저장 항목 수. 초과 시 오래된 항목을 제거합니다.
        """
        self.ttl = ttl
        self.max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._hits: int = 0
        self._misses: int = 0
        logger.info("[ResponseCache] 초기화 완료 (TTL: %d초, 최대 크기: %d)", ttl, max_size)

    def _make_key(self, query: str, context: str = "") -> str:
        """쿼리와 컨텍스트로 캐시 키를 생성합니다.

        Args:
            query: 사용자 질문
            context: 추가 컨텍스트 (선택사항)

        Returns:
            SHA-256 해시 기반의 캐시 키 문자열
        """
        raw = f"{query}::{context}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, query: str, context: str = "") -> Optional[Any]:
        """캐시에서 응답을 조회합니다.

        Args:
            query: 사용자 질문
            context: 추가 컨텍스트 (선택사항)

        Returns:
            캐시된 응답 값. 캐시 미스 또는 만료 시 None을 반환합니다.
        """
        # --- INPUT ---
        key = self._make_key(query, context)

        # --- PROCESS ---
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            logger.debug("[ResponseCache] 미스: key=%s...", key[:12])
            return None

        value, expires_at = entry
        if time.time() > expires_at:
            # 만료된 항목 제거
            del self._store[key]
            self._misses += 1
            logger.debug("[ResponseCache] 만료: key=%s...", key[:12])
            return None

        self._hits += 1
        logger.info("[ResponseCache] 적중: key=%s... (잔여 TTL: %.0f초)", key[:12], expires_at - time.time())

        # --- OUTPUT ---
        return value

    def set(self, query: str, value: Any, context: str = "") -> None:
        """캐시에 응답을 저장합니다.

        Args:
            query: 사용자 질문
            value: 저장할 응답 값
            context: 추가 컨텍스트 (선택사항)
        """
        # --- INPUT ---
        key = self._make_key(query, context)

        # --- PROCESS ---
        # 최대 크기 초과 시 가장 오래된 항목 제거
        if len(self._store) >= self.max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k][1])
            del self._store[oldest_key]
            logger.debug("[ResponseCache] 최대 크기 초과로 항목 제거: key=%s...", oldest_key[:12])

        expires_at = time.time() + self.ttl
        self._store[key] = (value, expires_at)

        # --- OUTPUT ---
        logger.info("[ResponseCache] 저장: key=%s... (만료: %.0f초 후)", key[:12], self.ttl)

    def clear(self) -> int:
        """만료된 캐시 항목을 제거합니다.

        Returns:
            제거된 항목 수
        """
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for key in expired_keys:
            del self._store[key]
        logger.info("[ResponseCache] 만료 항목 %d개 제거", len(expired_keys))
        return len(expired_keys)

    def stats(self) -> dict[str, Any]:
        """캐시 통계를 반환합니다.

        Returns:
            적중률, 항목 수 등 통계 딕셔너리
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        return {
            "total_items": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_seconds": self.ttl,
            "max_size": self.max_size,
        }


class EmbeddingCache:
    """로컬 파일 기반 임베딩 캐시.

    동일한 텍스트에 대한 임베딩 벡터를 파일에 저장하여 재계산을 방지합니다.
    프로세스 재시작 후에도 캐시가 유지됩니다.

    Attributes:
        cache_dir: 캐시 파일을 저장할 디렉토리 경로
        _hits: 캐시 적중 횟수
        _misses: 캐시 미적중 횟수
    """

    def __init__(self, cache_dir: str = DEFAULT_EMBEDDING_CACHE_DIR) -> None:
        """EmbeddingCache를 초기화합니다.

        Args:
            cache_dir: 캐시 파일을 저장할 디렉토리 경로. 존재하지 않으면 생성합니다.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._hits: int = 0
        self._misses: int = 0
        logger.info("[EmbeddingCache] 초기화 완료 (캐시 디렉토리: %s)", self.cache_dir)

    def _make_cache_path(self, text: str) -> Path:
        """텍스트로부터 캐시 파일 경로를 생성합니다.

        Args:
            text: 임베딩할 텍스트

        Returns:
            캐시 파일의 Path 객체
        """
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.pkl"

    def get(self, text: str) -> Optional[list[float]]:
        """캐시에서 임베딩 벡터를 조회합니다.

        Args:
            text: 임베딩 벡터를 조회할 텍스트

        Returns:
            캐시된 임베딩 벡터 (float 리스트). 캐시 미스 시 None을 반환합니다.
        """
        # --- INPUT ---
        cache_path = self._make_cache_path(text)

        # --- PROCESS ---
        if not cache_path.exists():
            self._misses += 1
            logger.debug("[EmbeddingCache] 미스: %s", cache_path.name[:16])
            return None

        try:
            with open(cache_path, "rb") as f:
                embedding = pickle.load(f)
            self._hits += 1
            logger.debug("[EmbeddingCache] 적중: %s", cache_path.name[:16])
            # --- OUTPUT ---
            return embedding
        except (pickle.UnpicklingError, EOFError) as exc:
            logger.warning("[EmbeddingCache] 캐시 파일 손상, 삭제: %s (%s)", cache_path.name, exc)
            cache_path.unlink(missing_ok=True)
            self._misses += 1
            return None

    def set(self, text: str, embedding: list[float]) -> None:
        """캐시에 임베딩 벡터를 저장합니다.

        Args:
            text: 임베딩한 텍스트
            embedding: 저장할 임베딩 벡터

        Raises:
            OSError: 파일 쓰기에 실패한 경우
        """
        # --- INPUT ---
        cache_path = self._make_cache_path(text)

        # --- PROCESS & OUTPUT ---
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(embedding, f)
            logger.debug("[EmbeddingCache] 저장: %s (%d dims)", cache_path.name[:16], len(embedding))
        except OSError as exc:
            logger.error("[EmbeddingCache] 저장 실패: %s", exc)
            raise

    def stats(self) -> dict[str, Any]:
        """캐시 통계를 반환합니다.

        Returns:
            적중률, 항목 수 등 통계 딕셔너리
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        cached_files = list(self.cache_dir.glob("*.pkl"))
        total_size_mb = sum(f.stat().st_size for f in cached_files) / (1024 * 1024)

        return {
            "cache_dir": str(self.cache_dir),
            "cached_items": len(cached_files),
            "total_size_mb": round(total_size_mb, 2),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
        }


# --- 싱글톤 인스턴스 ---
response_cache = ResponseCache(
    ttl=int(os.getenv("CACHE_TTL", str(DEFAULT_RESPONSE_TTL))),
    max_size=int(os.getenv("CACHE_MAX_SIZE", str(DEFAULT_RESPONSE_CACHE_MAX_SIZE))),
)

embedding_cache = EmbeddingCache(
    cache_dir=os.getenv("EMBEDDING_CACHE_DIR", DEFAULT_EMBEDDING_CACHE_DIR),
)
