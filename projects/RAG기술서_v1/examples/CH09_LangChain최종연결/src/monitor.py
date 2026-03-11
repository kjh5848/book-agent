"""
CH09 LangChain 최종 연결 — 모니터링 모듈.

에이전트 실행 시 응답 시간, 도구 호출 횟수, 캐시 히트율을 측정하고
요약 통계를 콘솔에 출력합니다.

사용 방법:
    from src.monitor import metrics_collector, RequestMetrics
    import time

    start = time.time()
    # ... 에이전트 실행 ...
    elapsed_ms = int((time.time() - start) * 1000)

    metrics_collector.record(RequestMetrics(
        question="질문 내용",
        response_time_ms=elapsed_ms,
        tool_calls=["get_leave_balance", "search_company_documents"],
        cached=False,
    ))
    metrics_collector.print_summary()
"""

from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """단일 요청에 대한 측정값을 담는 데이터 클래스입니다.

    Attributes:
        question: 사용자가 입력한 질문 문자열.
        response_time_ms: 에이전트 실행 전체 소요 시간 (밀리초).
        tool_calls: 해당 요청에서 호출된 Tool 이름 목록.
        cached: LangChain 캐시에서 응답이 반환된 경우 True.
    """

    question: str
    response_time_ms: int
    tool_calls: list[str]
    cached: bool


class MetricsCollector:
    """요청 메트릭을 수집하고 요약 통계를 제공하는 클래스입니다.

    수집된 RequestMetrics를 내부 목록에 저장하고,
    전체 요청 수, 평균 응답 시간, 캐시 히트율, 도구별 호출 횟수를 계산합니다.

    Attributes:
        _records: 수집된 RequestMetrics 객체 목록.
    """

    def __init__(self) -> None:
        """내부 메트릭 목록을 초기화합니다."""
        # --- Input ---
        # --- Output ---
        self._records: list[RequestMetrics] = []

    def record(self, metrics: RequestMetrics) -> None:
        """단일 요청 메트릭을 수집 목록에 추가합니다.

        Args:
            metrics: 기록할 RequestMetrics 객체.

        Returns:
            None
        """
        # --- Input ---
        # --- Process ---
        self._records.append(metrics)
        # --- Output ---

    def summary(self) -> dict:
        """수집된 메트릭 전체에 대한 요약 통계를 반환합니다.

        Returns:
            dict: 다음 키를 포함하는 요약 딕셔너리.
                - total_requests (int): 전체 요청 수.
                - avg_response_ms (float): 평균 응답 시간 (밀리초).
                - cache_hit_rate (float): 캐시 히트율 (0.0~1.0).
                - tool_usage (dict[str, int]): 도구별 호출 횟수.
        """
        # --- Input ---
        total = len(self._records)

        # --- Process ---
        if total == 0:
            return {
                "total_requests": 0,
                "avg_response_ms": 0.0,
                "cache_hit_rate": 0.0,
                "tool_usage": {},
            }

        avg_ms = sum(r.response_time_ms for r in self._records) / total
        cache_hits = sum(1 for r in self._records if r.cached)
        cache_hit_rate = cache_hits / total

        tool_usage: dict[str, int] = {}
        for record in self._records:
            for tool_name in record.tool_calls:
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        # --- Output ---
        return {
            "total_requests": total,
            "avg_response_ms": round(avg_ms, 2),
            "cache_hit_rate": round(cache_hit_rate, 4),
            "tool_usage": tool_usage,
        }

    def print_summary(self) -> None:
        """수집된 메트릭 요약을 콘솔에 출력합니다.

        총 요청 수, 평균 응답 시간, 캐시 히트율, 도구별 호출 횟수를
        읽기 쉬운 형태로 출력합니다.

        Returns:
            None
        """
        # --- Input ---
        stats = self.summary()

        # --- Process ---
        print("\n" + "=" * 50)
        print("  세션 통계 요약")
        print("=" * 50)
        print(f"  총 요청 수     : {stats['total_requests']}회")
        print(f"  평균 응답 시간 : {stats['avg_response_ms']:.1f}ms")
        cache_pct = stats["cache_hit_rate"] * 100
        print(f"  캐시 히트율    : {cache_pct:.1f}%")
        print("  도구별 호출 횟수:")

        tool_usage: dict[str, int] = stats["tool_usage"]
        if tool_usage:
            for tool_name, count in sorted(tool_usage.items()):
                print(f"    - {tool_name}: {count}회")
        else:
            print("    (도구 호출 없음)")

        # --- Output ---
        print("=" * 50 + "\n")


# 싱글톤 인스턴스
metrics_collector = MetricsCollector()
