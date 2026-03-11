"""
CH09 LangChain 연결 전략 — 구조화된 로깅 및 Langfuse 모니터링.

JSON 형식의 구조화된 로그 포맷, 토큰 사용량 추적, Langfuse 연동을 제공합니다.
Langfuse 패키지가 설치되지 않은 경우 자동으로 비활성화됩니다.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional


# --- JSON 구조화 로그 포맷터 ---
class JsonFormatter(logging.Formatter):
    """로그 레코드를 JSON 형식으로 직렬화하는 포맷터.

    각 로그 항목은 timestamp, level, logger, message 필드를 포함합니다.
    추가 필드는 extra 딕셔너리를 통해 주입할 수 있습니다.

    Attributes:
        fmt_keys: JSON에 포함할 추가 필드 목록
    """

    def __init__(self, fmt_keys: Optional[list[str]] = None) -> None:
        """JsonFormatter를 초기화합니다.

        Args:
            fmt_keys: JSON에 포함할 추가 필드 이름 목록 (선택사항)
        """
        super().__init__()
        self.fmt_keys = fmt_keys or []

    def format(self, record: logging.LogRecord) -> str:
        """LogRecord를 JSON 문자열로 변환합니다.

        Args:
            record: Python 로깅 레코드 객체

        Returns:
            JSON 직렬화된 로그 문자열
        """
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 추가 필드 포함
        for key in self.fmt_keys:
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)

        # exc_info가 있으면 포함
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    use_json: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """애플리케이션 로깅 시스템을 설정합니다.

    Args:
        level: 로그 레벨 문자열 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: True이면 JSON 형식, False이면 일반 텍스트 형식으로 출력합니다.
        log_file: 로그 파일 경로. None이면 콘솔에만 출력합니다.

    Raises:
        ValueError: 유효하지 않은 로그 레벨 문자열이 입력된 경우
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"유효하지 않은 로그 레벨입니다: '{level}'. INFO, DEBUG, WARNING, ERROR 중 하나를 사용하십시오.")

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 기존 핸들러 제거
    root_logger.handlers.clear()

    # 포맷터 선택
    if use_json:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (선택사항)
    if log_file:
        log_path = os.path.dirname(log_file)
        if log_path:
            os.makedirs(log_path, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logging.getLogger(__name__).info("로그 파일 저장 경로: %s", log_file)

    logging.getLogger(__name__).info(
        "로깅 설정 완료 (레벨: %s, JSON: %s)", level, use_json
    )


# --- 토큰 사용량 추적기 ---
class TokenTracker:
    """LLM API 호출별 토큰 사용량을 추적합니다.

    각 호출의 입력 토큰, 출력 토큰, 비용을 누적 집계합니다.

    Attributes:
        _records: 개별 호출 기록 목록
        _total_input_tokens: 누적 입력 토큰 수
        _total_output_tokens: 누적 출력 토큰 수
    """

    # 간략한 비용 기준 (달러/1000토큰, 참고용)
    COST_PER_1K_TOKENS: dict[str, dict[str, float]] = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "deepseek-r1:8b": {"input": 0.0, "output": 0.0},  # 로컬 모델: 무료
    }

    def __init__(self) -> None:
        """TokenTracker를 초기화합니다."""
        self._records: list[dict[str, Any]] = []
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._logger = logging.getLogger(__name__)

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "chat",
        latency_ms: float = 0.0,
    ) -> None:
        """토큰 사용량을 기록합니다.

        Args:
            model: 사용한 LLM 모델 이름
            input_tokens: 입력(프롬프트) 토큰 수
            output_tokens: 출력(생성) 토큰 수
            operation: 작업 유형 (chat, embedding 등)
            latency_ms: 응답 소요 시간 (밀리초)
        """
        # --- INPUT ---
        cost_table = self.COST_PER_1K_TOKENS.get(model, {"input": 0.0, "output": 0.0})
        cost_usd = (
            (input_tokens / 1000 * cost_table["input"])
            + (output_tokens / 1000 * cost_table["output"])
        )

        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost_usd, 6),
            "latency_ms": round(latency_ms, 2),
        }

        # --- PROCESS ---
        self._records.append(record)
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens

        # --- OUTPUT ---
        self._logger.info(
            "[TokenTracker] 사용량 기록: model=%s, input=%d, output=%d, cost=$%.6f, latency=%.0fms",
            model, input_tokens, output_tokens, cost_usd, latency_ms,
        )

    def summary(self) -> dict[str, Any]:
        """누적 토큰 사용량 요약을 반환합니다.

        Returns:
            총 호출 횟수, 누적 토큰 수, 총 비용 등 요약 딕셔너리
        """
        total_cost = sum(r["cost_usd"] for r in self._records)
        avg_latency = (
            sum(r["latency_ms"] for r in self._records) / len(self._records)
            if self._records
            else 0.0
        )
        return {
            "total_calls": len(self._records),
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_tokens": self._total_input_tokens + self._total_output_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(avg_latency, 2),
        }

    def recent(self, n: int = 5) -> list[dict[str, Any]]:
        """최근 n개의 호출 기록을 반환합니다.

        Args:
            n: 반환할 최근 기록 수

        Returns:
            최근 호출 기록 딕셔너리 목록
        """
        return self._records[-n:]


# --- Langfuse 래퍼 ---
class LangfuseMonitor:
    """Langfuse LLM 모니터링 도구 연동 래퍼.

    langfuse 패키지가 설치된 경우 자동으로 활성화됩니다.
    설치되지 않은 경우 모든 메서드는 아무 동작도 하지 않습니다(no-op).

    Langfuse 설치: pip install langfuse
    환경 변수 설정:
        LANGFUSE_PUBLIC_KEY: Langfuse 공개 키
        LANGFUSE_SECRET_KEY: Langfuse 비밀 키
        LANGFUSE_HOST: Langfuse 서버 주소 (기본: https://cloud.langfuse.com)

    Attributes:
        enabled: Langfuse 활성화 여부
        _client: Langfuse 클라이언트 객체 (활성화 시)
    """

    def __init__(self) -> None:
        """LangfuseMonitor를 초기화합니다."""
        self._logger = logging.getLogger(__name__)
        self.enabled = False
        self._client: Any = None
        self._init_langfuse()

    def _init_langfuse(self) -> None:
        """Langfuse 클라이언트를 초기화합니다.

        langfuse 패키지와 환경 변수가 모두 설정된 경우에만 활성화됩니다.
        """
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

        if not public_key or not secret_key:
            self._logger.info(
                "[Langfuse] LANGFUSE_PUBLIC_KEY 또는 LANGFUSE_SECRET_KEY가 설정되지 않았습니다. "
                "모니터링을 사용하려면 .env에 키를 추가하십시오."
            )
            return

        try:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            )
            self.enabled = True
            self._logger.info("[Langfuse] 모니터링 활성화됨")
        except ImportError:
            self._logger.info(
                "[Langfuse] langfuse 패키지가 설치되지 않았습니다. "
                "설치하려면: pip install langfuse"
            )

    def trace(self, name: str, input_data: Any, output_data: Any, metadata: Optional[dict] = None) -> None:
        """LLM 호출 추적 기록을 Langfuse에 전송합니다.

        Args:
            name: 추적 이름 (예: "qa_chain", "agent_run")
            input_data: 입력 데이터 (질문, 프롬프트 등)
            output_data: 출력 데이터 (응답 등)
            metadata: 추가 메타데이터 딕셔너리 (선택사항)
        """
        if not self.enabled or self._client is None:
            return

        try:
            self._client.trace(
                name=name,
                input=input_data if isinstance(input_data, str) else str(input_data),
                output=output_data if isinstance(output_data, str) else str(output_data),
                metadata=metadata or {},
            )
            self._logger.debug("[Langfuse] 추적 전송 완료: %s", name)
        except Exception as exc:
            self._logger.warning("[Langfuse] 추적 전송 실패: %s", exc)

    def flush(self) -> None:
        """대기 중인 Langfuse 이벤트를 즉시 전송합니다."""
        if not self.enabled or self._client is None:
            return
        try:
            self._client.flush()
        except Exception as exc:
            self._logger.warning("[Langfuse] flush 실패: %s", exc)


# --- 싱글톤 인스턴스 ---
token_tracker = TokenTracker()
langfuse_monitor = LangfuseMonitor()
