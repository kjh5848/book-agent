"""CLI 기반 채팅 인터페이스 모듈.

커넥트HR 사내 문서 Q&A 시스템의 커맨드라인 인터페이스입니다.
사용자 입력을 받아 RAG 체인에 전달하고, 출처가 포함된 답변을 출력합니다.
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional

from rag_chain import RAGChain


# 화면 구분선 길이
SEPARATOR_WIDTH = 60


def _print_banner() -> None:
    """커넥트HR AI 어시스턴트 시작 배너를 출력합니다."""

    # --- Output ---
    print("\n" + "=" * SEPARATOR_WIDTH)
    print("  커넥트HR AI 어시스턴트")
    print("  사내 문서 기반 Q&A 시스템 (RAG 엔진)")
    print("=" * SEPARATOR_WIDTH)
    print("  사용 가능한 명령:")
    print("    /quit  — 종료")
    print("    /clear — 대화 히스토리 초기화")
    print("    /stats — 검색 통계 표시")
    print("    /help  — 도움말")
    print("=" * SEPARATOR_WIDTH)
    print()


def _print_separator(char: str = "-", width: int = SEPARATOR_WIDTH) -> None:
    """구분선을 출력합니다.

    Args:
        char: 구분선에 사용할 문자 (기본값: "-")
        width: 구분선 너비 (기본값: SEPARATOR_WIDTH)
    """

    print(char * width)


def _format_elapsed_time(elapsed_seconds: float) -> str:
    """경과 시간을 읽기 좋은 문자열로 변환합니다.

    Args:
        elapsed_seconds: 경과 시간 (초 단위)

    Returns:
        "0.5초" 또는 "1분 30초" 형식의 문자열
    """

    # --- Process ---
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.1f}초"
    else:
        minutes = int(elapsed_seconds // 60)
        seconds = elapsed_seconds % 60
        return f"{minutes}분 {seconds:.0f}초"

    # --- Output ---
    # 형식화된 시간 문자열


class ChatSession:
    """CLI 채팅 세션 관리 클래스.

    대화 히스토리와 검색 통계를 관리하며, 사용자 입력에 대한
    RAG 응답을 순서대로 처리합니다.

    Attributes:
        rag_chain: 질문 처리에 사용되는 RAGChain 인스턴스
        history: 대화 히스토리 리스트 (질문/답변 쌍)
        stats: 누적 검색 통계 딕셔너리
    """

    def __init__(self, rag_chain: RAGChain) -> None:
        """ChatSession을 초기화합니다.

        Args:
            rag_chain: 초기화된 RAGChain 인스턴스
        """

        # --- Input ---
        self.rag_chain = rag_chain
        self.history: list[dict] = []
        self.stats: dict = {
            "total_questions": 0,
            "total_elapsed_seconds": 0.0,
            "average_elapsed_seconds": 0.0,
            "session_start": datetime.now().isoformat(),
        }

        # --- Output ---
        # 세션 초기화 완료

    def process_question(self, question: str) -> Optional[str]:
        """사용자 질문을 처리하고 답변을 반환합니다.

        Args:
            question: 사용자가 입력한 질문 문자열

        Returns:
            출처가 포함된 답변 문자열. 처리 실패 시 None을 반환합니다.
        """

        # --- Input ---
        if not question or not question.strip():
            return None

        # --- Process ---
        start_time = time.time()
        result = self.rag_chain.invoke(question=question)
        elapsed = time.time() - start_time

        # 대화 히스토리 추가
        self.history.append({
            "question": question,
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
        })

        # 통계 갱신
        self.stats["total_questions"] += 1
        self.stats["total_elapsed_seconds"] += elapsed
        self.stats["average_elapsed_seconds"] = (
            self.stats["total_elapsed_seconds"] / self.stats["total_questions"]
        )

        # --- Output ---
        return result["answer"]

    def clear_history(self) -> None:
        """대화 히스토리를 초기화합니다."""

        # --- Process ---
        self.history.clear()
        print("  대화 히스토리가 초기화되었습니다.")

        # --- Output ---
        # history 리스트 비워짐

    def print_stats(self) -> None:
        """누적 검색 통계를 출력합니다."""

        # --- Output ---
        _print_separator()
        print("  검색 통계")
        _print_separator(char="-", width=40)
        print(f"  총 질문 수       : {self.stats['total_questions']}회")

        avg_time = self.stats.get("average_elapsed_seconds", 0.0)
        total_time = self.stats.get("total_elapsed_seconds", 0.0)
        print(f"  평균 응답 시간   : {_format_elapsed_time(avg_time)}")
        print(f"  총 소요 시간     : {_format_elapsed_time(total_time)}")
        print(f"  세션 시작 시각   : {self.stats['session_start']}")

        chain_status = self.rag_chain.get_status()
        print(f"  LLM 모드         : {chain_status['mode']}")
        print(f"  모델명           : {chain_status['model']}")
        print(f"  검색 top-k       : {chain_status['top_k']}")
        _print_separator()

    def print_help(self) -> None:
        """사용 가능한 명령어 도움말을 출력합니다."""

        # --- Output ---
        _print_separator()
        print("  도움말")
        _print_separator(char="-", width=40)
        print("  일반 텍스트    : 사내 문서 기반으로 답변합니다")
        print("  /quit          : 프로그램을 종료합니다")
        print("  /clear         : 대화 히스토리를 초기화합니다")
        print("  /stats         : 검색 통계를 표시합니다")
        print("  /help          : 이 도움말을 표시합니다")
        print()
        print("  예시 질문:")
        print("  - 연차 휴가는 몇 일 발생하나요?")
        print("  - 특별휴가 조건이 무엇인가요?")
        print("  - 재택근무 신청 방법을 알려주세요")
        _print_separator()


def run_chat_loop(rag_chain: RAGChain) -> None:
    """CLI 채팅 루프를 실행합니다.

    사용자 입력을 반복적으로 받아 RAG 체인에 전달하고,
    출처가 포함된 답변을 출력합니다. /quit 입력 시 종료합니다.

    Args:
        rag_chain: 초기화된 RAGChain 인스턴스
    """

    # --- Input ---
    session = ChatSession(rag_chain=rag_chain)
    _print_banner()

    # RAG 체인 상태 출력
    status = rag_chain.get_status()
    print(f"  모드: {status['mode']} | 모델: {status['model']} | top-k: {status['top_k']}")
    print()

    # --- Process ---
    while True:
        try:
            # 사용자 입력 받기
            user_input = input("질문 > ").strip()

            # 빈 입력 무시
            if not user_input:
                continue

            # 특수 명령 처리
            command = user_input.lower()

            if command in ("/quit", "/exit", "/q"):
                print("\n  커넥트HR AI 어시스턴트를 종료합니다.")
                session.print_stats()
                break

            elif command == "/clear":
                session.clear_history()
                continue

            elif command == "/stats":
                session.print_stats()
                continue

            elif command == "/help":
                session.print_help()
                continue

            # 일반 질문 처리
            print()
            print("  답변 생성 중...")
            start_display = time.time()

            answer = session.process_question(question=user_input)

            elapsed = time.time() - start_display
            elapsed_str = _format_elapsed_time(elapsed)

            # 답변 출력
            _print_separator()
            if answer:
                print(answer)
            else:
                print("  답변을 생성할 수 없습니다.")
            _print_separator(char="-", width=40)
            print(f"  응답 시간: {elapsed_str}")
            _print_separator()
            print()

        except KeyboardInterrupt:
            # Ctrl+C 처리
            print("\n\n  인터럽트 감지. 종료합니다.")
            session.print_stats()
            break

        except EOFError:
            # 파이프 입력 종료
            print("\n  입력 스트림 종료.")
            break

    # --- Output ---
    # 채팅 루프 종료
