"""
세션 관리 모듈.

HTTP 요청에서 세션 ID를 추출하거나 신규 생성하는 유틸리티를 제공한다.
세션 ID는 UUID v4 기반이며 브라우저 쿠키 또는 요청 본문에서 읽어온다.
"""

import uuid

from fastapi import Request
from fastapi.responses import JSONResponse


SESSION_COOKIE_NAME = "rag_session_id"


def get_session_id(request: Request) -> str:
    """
    요청에서 세션 ID를 읽어 반환한다.
    쿠키에 세션 ID가 없으면 새로 생성한다.

    Args:
        request: FastAPI Request 객체

    Returns:
        세션 ID 문자열 (UUID v4 형식)
    """
    # === INPUT ===
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    # === PROCESS ===
    if not session_id:
        session_id = str(uuid.uuid4())

    # === OUTPUT ===
    return session_id


def set_session_cookie(response: JSONResponse, session_id: str) -> JSONResponse:
    """
    응답 객체에 세션 쿠키를 설정한다.

    Args:
        response: FastAPI JSONResponse 객체
        session_id: 설정할 세션 ID 문자열

    Returns:
        쿠키가 설정된 JSONResponse 객체
    """
    # === INPUT & PROCESS ===
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,       # JavaScript 접근 차단 (XSS 방지)
        samesite="lax",      # CSRF 방지
        max_age=3600,        # 1시간
    )

    # === OUTPUT ===
    return response


def generate_session_id() -> str:
    """
    새로운 UUID v4 기반 세션 ID를 생성하여 반환한다.

    Returns:
        새 세션 ID 문자열
    """
    return str(uuid.uuid4())
