"""
대화 히스토리 관리 모듈.

세션 ID별로 대화 히스토리를 관리하며,
WindowMemory를 활용하여 최근 N턴의 대화만 유지한다.
"""

import os
import time
from collections import deque

from dotenv import load_dotenv

load_dotenv()


class WindowMemory:
    """
    최근 N턴의 대화만 유지하는 슬라이딩 윈도우 메모리.

    deque(maxlen=k) 기반으로 최근 k턴만 보관하며,
    프롬프트에 삽입할 텍스트 형식으로 히스토리를 반환한다.

    Attributes:
        k: 유지할 최근 대화 턴 수
        human_prefix: 사용자 메시지 접두사
        ai_prefix: AI 응답 접두사
    """

    def __init__(
        self,
        k: int = 5,
        human_prefix: str = "사용자",
        ai_prefix: str = "AI 비서",
    ) -> None:
        self.k = k
        self.human_prefix = human_prefix
        self.ai_prefix = ai_prefix
        self._turns: deque[tuple[str, str]] = deque(maxlen=k)

    def get_history(self) -> str:
        """최근 N턴의 대화를 텍스트로 반환한다."""
        lines = []
        for question, answer in self._turns:
            lines.append(f"{self.human_prefix}: {question}")
            lines.append(f"{self.ai_prefix}: {answer}")
        return "\n".join(lines)

    def save_turn(self, question: str, answer: str) -> None:
        """사용자 질문과 AI 답변 1턴을 저장한다."""
        self._turns.append((question, answer))

    def clear(self) -> None:
        """히스토리를 초기화한다."""
        self._turns.clear()


class ConversationManager:
    """
    세션별 대화 히스토리를 관리하는 클래스.

    최근 N턴의 대화만 유지하고(WindowMemory),
    설정된 TTL이 지나면 세션을 자동으로 만료한다.

    Attributes:
        window_size: 유지할 최근 대화 턴 수 (기본값: .env의 CONVERSATION_WINDOW_SIZE)
        session_ttl: 세션 만료 시간(초) (기본값: .env의 SESSION_TTL_SECONDS)
        _sessions: 세션 ID → (WindowMemory, 마지막 접근 시각) 딕셔너리
    """

    def __init__(
        self,
        window_size: int | None = None,
        session_ttl: int | None = None,
    ) -> None:
        """
        ConversationManager를 초기화한다.

        Args:
            window_size: 유지할 최근 대화 턴 수. None이면 .env 값 사용.
            session_ttl: 세션 만료 시간(초). None이면 .env 값 사용.
        """
        self.window_size: int = window_size or int(
            os.getenv("CONVERSATION_WINDOW_SIZE", "5")
        )
        self.session_ttl: int = session_ttl or int(
            os.getenv("SESSION_TTL_SECONDS", "3600")
        )
        # 세션 저장소: {session_id: (WindowMemory, last_access_time)}
        self._sessions: dict[str, tuple[WindowMemory, float]] = {}

    def _get_or_create_memory(self, session_id: str) -> WindowMemory:
        """
        세션 ID에 해당하는 Memory를 반환하거나 신규 생성한다.
        만료된 세션은 자동으로 정리한다.

        Args:
            session_id: 브라우저/클라이언트 세션 식별자

        Returns:
            해당 세션의 WindowMemory 인스턴스
        """
        # === INPUT ===
        now = time.time()

        # === PROCESS ===
        # 만료된 세션 정리
        self._cleanup_expired(now)

        if session_id not in self._sessions:
            # 신규 세션: 윈도우 크기 설정
            memory = WindowMemory(
                k=self.window_size,
                human_prefix="사용자",
                ai_prefix="AI 비서",
            )
            self._sessions[session_id] = (memory, now)
        else:
            # 기존 세션: 마지막 접근 시각 갱신
            memory, _ = self._sessions[session_id]
            self._sessions[session_id] = (memory, now)

        # === OUTPUT ===
        return self._sessions[session_id][0]

    def _cleanup_expired(self, now: float) -> None:
        """
        TTL이 지난 만료된 세션을 삭제한다.

        Args:
            now: 현재 Unix 타임스탬프
        """
        expired_keys = [
            sid
            for sid, (_, last_access) in self._sessions.items()
            if now - last_access > self.session_ttl
        ]
        for key in expired_keys:
            del self._sessions[key]

    def get_history_text(self, session_id: str) -> str:
        """
        세션의 대화 히스토리를 프롬프트 삽입용 문자열로 반환한다.

        Args:
            session_id: 세션 식별자

        Returns:
            대화 히스토리 문자열 (없으면 "없음")
        """
        # === INPUT ===
        memory = self._get_or_create_memory(session_id)

        # === PROCESS ===
        history = memory.get_history()

        # === OUTPUT ===
        return history if history else "없음"

    def save_turn(
        self,
        session_id: str,
        question: str,
        answer: str,
    ) -> None:
        """
        사용자 질문과 AI 답변을 세션 히스토리에 저장한다.

        Args:
            session_id: 세션 식별자
            question: 사용자 질문 문자열
            answer: AI 답변 문자열
        """
        # === INPUT ===
        memory = self._get_or_create_memory(session_id)

        # === PROCESS ===
        memory.save_turn(question, answer)
        # === OUTPUT ===
        # (메모리에 저장 완료, 반환값 없음)

    def clear_session(self, session_id: str) -> None:
        """
        지정한 세션의 대화 히스토리를 초기화한다.

        Args:
            session_id: 초기화할 세션 식별자
        """
        if session_id in self._sessions:
            memory, last_access = self._sessions[session_id]
            memory.clear()
            # 접근 시각은 그대로 유지하여 세션 자체는 유지
            self._sessions[session_id] = (memory, last_access)

    def get_session_count(self) -> int:
        """
        현재 활성 세션 수를 반환한다.

        Returns:
            활성 세션 수 (정수)
        """
        return len(self._sessions)


# 앱 전역 싱글턴 인스턴스
_conversation_manager: ConversationManager | None = None


def get_conversation_manager() -> ConversationManager:
    """
    ConversationManager 싱글턴 인스턴스를 반환한다.
    최초 호출 시 생성하고 이후 재사용한다.

    Returns:
        ConversationManager 인스턴스
    """
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
