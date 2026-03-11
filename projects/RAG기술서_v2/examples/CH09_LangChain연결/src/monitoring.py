"""모니터링 모듈 — 로깅, 토큰 추적, 응답 캐시.

구조화 로그(JSON 포맷), 토큰 사용량 추적, 메모리 기반 TTL 캐시를
하나의 모듈에서 관리합니다.

챕터 9.3: 운영 설정 — 로깅·캐싱·토큰 모니터링
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cachetools import TTLCache

# ============================================================
# 구조화 로깅
# ============================================================


class JsonFormatter(logging.Formatter):
    """JSON 형식으로 로그를 포맷하는 핸들러 클래스.

    Attributes:
        없음 (상위 Formatter 속성 사용)
    """

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 문자열로 변환합니다.

        Args:
            record: 로그 레코드 객체

        Returns:
            JSON 형식의 로그 문자열
        """

        # --- Input ---
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
        }

        # --- Process ---
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # --- Output ---
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """구조화 로그 설정을 초기화합니다.

    콘솔에는 가독성 높은 텍스트 포맷으로,
    파일에는 JSON 포맷으로 로그를 출력합니다.

    Args:
        log_level: 로그 레벨 문자열 ("DEBUG" | "INFO" | "WARNING" | "ERROR")
        log_file:  로그 파일 경로. None이면 파일 핸들러를 추가하지 않습니다.

    Returns:
        설정 완료된 루트 Logger 객체
    """

    # --- Input ---
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # --- Process ---
    logger = logging.getLogger("ch09")
    logger.setLevel(numeric_level)

    # 중복 핸들러 방지
    if logger.handlers:
        logger.handlers.clear()

    # 콘솔 핸들러 (텍스트 포맷)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (JSON 포맷)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    # --- Output ---
    return logger


# ============================================================
# 토큰 사용량 추적
# ============================================================


@dataclass
class TokenUsageRecord:
    """단일 LLM 호출의 토큰 사용 기록.

    Attributes:
        model:             사용한 LLM 모델명
        prompt_tokens:     입력(프롬프트) 토큰 수
        completion_tokens: 생성(완성) 토큰 수
        total_tokens:      총 토큰 수
        timestamp:         호출 시각 (Unix timestamp)
    """

    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int = field(init=False)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """총 토큰 수를 자동으로 계산합니다."""
        self.total_tokens = self.prompt_tokens + self.completion_tokens


class TokenUsageTracker:
    """LLM 토큰 사용량을 추적하고 요약 리포트를 생성하는 클래스.

    로컬 LLM(Ollama)도 메모리와 CPU를 소비하므로
    불필요하게 긴 프롬프트를 보내는 것을 방지하기 위해 사용합니다.

    Attributes:
        records:        토큰 사용 기록 목록
        _logger:        내부 로거
    """

    # 모델별 비용 추정 (원/1K 토큰, 로컬 모델은 0원)
    _COST_PER_1K: dict[str, float] = {
        "deepseek-r1":   0.0,
        "deepseek-r1:7b": 0.0,
        "deepseek-r1:1.5b": 0.0,
        "default":       0.0,
    }

    def __init__(self) -> None:
        """TokenUsageTracker를 초기화합니다."""
        self.records: list[TokenUsageRecord] = []
        self._logger = logging.getLogger("ch09.token_tracker")

    def track(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "deepseek-r1",
    ) -> TokenUsageRecord:
        """토큰 사용량을 기록합니다.

        Args:
            prompt_tokens:     입력 프롬프트 토큰 수
            completion_tokens: 생성된 완성 토큰 수
            model:             사용한 LLM 모델명

        Returns:
            생성된 TokenUsageRecord 객체
        """

        # --- Input ---
        record = TokenUsageRecord(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        # --- Process ---
        self.records.append(record)
        self._logger.debug(
            "토큰 사용 기록: 모델=%s, 입력=%d, 생성=%d, 합계=%d",
            model,
            prompt_tokens,
            completion_tokens,
            record.total_tokens,
        )

        # --- Output ---
        return record

    def get_summary(self) -> dict[str, Any]:
        """총 토큰 사용량과 비용 추정을 계산하여 반환합니다.

        Returns:
            요약 딕셔너리:
            - total_calls (int):             총 LLM 호출 횟수
            - total_prompt_tokens (int):     총 입력 토큰
            - total_completion_tokens (int): 총 생성 토큰
            - total_tokens (int):            총 토큰
            - estimated_cost_krw (float):    추정 비용 (원)
            - by_model (dict):               모델별 집계
        """

        # --- Input ---
        if not self.records:
            return {
                "total_calls": 0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_krw": 0.0,
                "by_model": {},
            }

        # --- Process ---
        total_prompt = sum(r.prompt_tokens for r in self.records)
        total_completion = sum(r.completion_tokens for r in self.records)
        total_tokens = sum(r.total_tokens for r in self.records)

        by_model: dict[str, dict[str, int | float]] = {}
        for record in self.records:
            entry = by_model.setdefault(
                record.model,
                {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            )
            entry["calls"] += 1
            entry["prompt_tokens"] += record.prompt_tokens
            entry["completion_tokens"] += record.completion_tokens
            entry["total_tokens"] += record.total_tokens

        cost_per_1k = self._COST_PER_1K.get(
            self.records[0].model,
            self._COST_PER_1K["default"],
        )
        estimated_cost = (total_tokens / 1000) * cost_per_1k

        # --- Output ---
        return {
            "total_calls": len(self.records),
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_tokens,
            "estimated_cost_krw": estimated_cost,
            "by_model": by_model,
        }

    def save_report(self, path: str) -> None:
        """토큰 사용 리포트를 JSON 파일로 저장합니다.

        Args:
            path: 저장할 파일 경로 (예: './outputs/token_report.json')

        Raises:
            OSError: 파일 쓰기 실패 시
        """

        # --- Input ---
        report_path = Path(path)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # --- Process ---
        summary = self.get_summary()
        report = {
            "summary": summary,
            "records": [
                {
                    "model":             r.model,
                    "prompt_tokens":     r.prompt_tokens,
                    "completion_tokens": r.completion_tokens,
                    "total_tokens":      r.total_tokens,
                    "timestamp":         r.timestamp,
                }
                for r in self.records
            ],
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # --- Output ---
        self._logger.info("토큰 리포트 저장 완료: %s", report_path)


# ============================================================
# 응답 캐시
# ============================================================


class ResponseCache:
    """TTL 기반 메모리 응답 캐시 클래스.

    동일한 질문에 대해 이전 응답을 재사용하여
    LLM 호출 횟수와 응답 시간을 줄입니다.

    Attributes:
        _cache:      TTLCache 내부 저장소
        _hits:       캐시 히트 횟수
        _misses:     캐시 미스 횟수
        _logger:     내부 로거
    """

    def __init__(self, maxsize: int = 256, ttl: int = 300) -> None:
        """ResponseCache를 초기화합니다.

        Args:
            maxsize: 캐시에 저장할 최대 항목 수 (기본값: 256)
            ttl:     캐시 유지 시간(초) (기본값: 300)
        """

        # --- Input ---
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._hits: int = 0
        self._misses: int = 0
        self._logger = logging.getLogger("ch09.response_cache")

    def get(self, key: str) -> Any | None:
        """캐시에서 값을 조회합니다.

        Args:
            key: 캐시 키 문자열

        Returns:
            캐시에 저장된 값. 없으면 None.
        """

        # --- Input ---
        # --- Process ---
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
            self._logger.debug("캐시 히트: key=%s", key[:50])
        else:
            self._misses += 1
            self._logger.debug("캐시 미스: key=%s", key[:50])

        # --- Output ---
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """캐시에 값을 저장합니다.

        TTL은 TTLCache 초기화 시 설정된 값을 사용합니다.
        (cachetools TTLCache는 항목별 TTL 재정의를 지원하지 않습니다.)

        Args:
            key:   캐시 키 문자열
            value: 저장할 값
            ttl:   미사용 (인터페이스 일관성을 위해 유지)
        """

        # --- Input ---
        # --- Process ---
        self._cache[key] = value
        self._logger.debug("캐시 저장: key=%s", key[:50])

        # --- Output ---
        # None (사이드 이펙트: 캐시 저장)

    def get_stats(self) -> dict[str, int | float]:
        """캐시 히트율 통계를 반환합니다.

        Returns:
            통계 딕셔너리:
            - hits (int):      캐시 히트 횟수
            - misses (int):    캐시 미스 횟수
            - total (int):     총 조회 횟수
            - hit_rate (float): 히트율 (0.0~1.0)
            - current_size (int): 현재 캐시 항목 수
        """

        # --- Input ---
        total = self._hits + self._misses

        # --- Process ---
        hit_rate = self._hits / total if total > 0 else 0.0

        # --- Output ---
        return {
            "hits":         self._hits,
            "misses":       self._misses,
            "total":        total,
            "hit_rate":     round(hit_rate, 4),
            "current_size": len(self._cache),
        }
