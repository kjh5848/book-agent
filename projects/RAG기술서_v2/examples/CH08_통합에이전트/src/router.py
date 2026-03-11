"""질문 라우팅 모듈 — 정형/비정형/복합 질의 분류기.

사용자 질문을 세 가지 유형으로 분류합니다.
  - structured: 정형 데이터(DB) 조회가 필요한 질문
  - unstructured: 비정형 문서(RAG) 검색이 필요한 질문
  - hybrid: DB 조회와 문서 검색이 모두 필요한 복합 질문

1단계로 규칙 기반(키워드 매칭)을 적용하고,
불명확한 경우 2단계로 LLM 의도 분류를 사용합니다.

챕터 8.2: 질문 라우팅 전략 (규칙 기반 -> LLM 판단)
"""

import os
import re
import json
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")

# 질문 유형 리터럴 타입
QueryType = Literal["structured", "unstructured", "hybrid"]

# ============================================================
# 키워드 사전
# ============================================================

# 정형 데이터(DB) 관련 키워드
STRUCTURED_KEYWORDS: list[str] = [
    "연차", "잔여", "남은", "사용한", "급여", "매출", "직원", "부서",
    "입사", "재직", "연봉", "월급", "목표", "달성", "분기", "실적",
    "팀장", "과장", "대리", "사원", "개발자", "인원", "몇 명",
]

# 비정형 데이터(문서) 관련 키워드
UNSTRUCTURED_KEYWORDS: list[str] = [
    "정책", "규정", "절차", "방법", "어떻게", "안내", "가이드",
    "규칙", "기준", "조건", "원칙", "지침", "프로세스", "신청",
    "육아휴직", "출산휴가", "보안", "VPN", "온보딩", "교육",
    "복리후생", "퇴직", "승진", "평가",
]


def _check_ollama_available() -> bool:
    """Ollama 서버 연결 가능 여부를 확인합니다.

    Returns:
        연결 가능하면 True, 불가능하면 False
    """

    # --- Process ---
    try:
        import requests
        response = requests.get(OLLAMA_BASE_URL, timeout=3)
        return response.status_code == 200
    except Exception:
        return False

    # --- Output ---
    # bool 반환


class QueryRouter:
    """질문을 정형/비정형/복합 유형으로 분류하는 라우터 클래스.

    1단계: 규칙 기반 키워드 매칭으로 빠르게 분류합니다.
    2단계: 규칙만으로 불명확한 경우 LLM 의도 분류를 사용합니다.

    Attributes:
        use_llm_fallback: LLM 2단계 분류 사용 여부
        llm: Ollama LLM 인스턴스 (LLM 폴백 활성화 시)
    """

    def __init__(self, use_llm_fallback: bool = True) -> None:
        """QueryRouter를 초기화합니다.

        Args:
            use_llm_fallback: LLM 기반 2단계 분류 활성화 여부 (기본값: True)
        """

        # --- Input ---
        self.use_llm_fallback = use_llm_fallback
        self.llm = None

        # --- Process ---
        if use_llm_fallback and _check_ollama_available():
            try:
                from langchain_ollama import ChatOllama
                self.llm = ChatOllama(
                    model=OLLAMA_MODEL,
                    base_url=OLLAMA_BASE_URL,
                    temperature=0.0,
                )
                print(f"  [라우터] LLM 폴백 활성화: {OLLAMA_MODEL}")
            except ImportError:
                print("  [라우터] langchain-ollama 없음. 규칙 기반만 사용합니다.")
        else:
            if use_llm_fallback:
                print("  [라우터] Ollama 미연결. 규칙 기반만 사용합니다.")

        # --- Output ---
        # self.llm 설정 완료

    def _rule_based_classify(self, question: str) -> tuple[QueryType | None, float]:
        """규칙 기반(키워드 매칭)으로 질문 유형을 분류합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            (유형, 신뢰도) 튜플.
            유형이 불명확하면 (None, 0.0) 반환.
        """

        # --- Input ---
        question_lower = question.lower()

        # --- Process ---
        structured_hits = [kw for kw in STRUCTURED_KEYWORDS if kw in question_lower]
        unstructured_hits = [kw for kw in UNSTRUCTURED_KEYWORDS if kw in question_lower]

        has_structured = len(structured_hits) > 0
        has_unstructured = len(unstructured_hits) > 0

        if has_structured and has_unstructured:
            confidence = min(0.95, 0.5 + (len(structured_hits) + len(unstructured_hits)) * 0.05)
            return "hybrid", confidence
        elif has_structured:
            confidence = min(0.95, 0.6 + len(structured_hits) * 0.1)
            return "structured", confidence
        elif has_unstructured:
            confidence = min(0.95, 0.6 + len(unstructured_hits) * 0.1)
            return "unstructured", confidence

        # 키워드 매칭 실패 — 불명확
        # --- Output ---
        return None, 0.0

    def _llm_classify(self, question: str) -> tuple[QueryType, float]:
        """LLM 기반으로 질문 유형을 분류합니다.

        규칙 기반으로 분류하지 못할 때 호출됩니다.
        LLM에게 structured / unstructured / hybrid 중 하나를 선택하게 합니다.

        Args:
            question: 사용자 질문 문자열

        Returns:
            (유형, 신뢰도) 튜플
        """

        # --- Input ---
        prompt = f"""당신은 HR 시스템의 질문 분류기입니다.
다음 질문을 아래 세 가지 유형 중 하나로 분류하십시오.

유형 정의:
- structured: 직원 정보, 연차 잔액, 매출 등 데이터베이스(DB)에서 조회하는 질문
- unstructured: 회사 정책, 규정, 절차, 방법 등 문서에서 검색하는 질문
- hybrid: DB 조회와 문서 검색이 모두 필요한 질문

질문: {question}

반드시 아래 JSON 형식으로만 답하십시오.
{{"type": "structured" | "unstructured" | "hybrid", "reason": "짧은 이유"}}"""

        # --- Process ---
        try:
            from langchain_core.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=prompt)])
            raw_text = response.content.strip()

            # JSON 파싱 (LLM이 마크다운 코드블록에 감쌀 수 있으므로 추출)
            json_match = re.search(r'\{[^}]+\}', raw_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                query_type = parsed.get("type", "unstructured")
                if query_type not in ("structured", "unstructured", "hybrid"):
                    query_type = "unstructured"
                return query_type, 0.75
        except Exception as e:
            print(f"  [라우터 경고] LLM 분류 실패: {e}")

        # 최종 실패 시 비정형으로 기본 처리
        # --- Output ---
        return "unstructured", 0.5

    def classify(self, question: str) -> dict:
        """질문을 정형/비정형/복합 유형으로 분류합니다.

        1단계: 규칙 기반 키워드 매칭으로 분류를 시도합니다.
        2단계: 1단계가 실패하면 LLM 분류를 사용합니다. (LLM 활성화 시)

        Args:
            question: 사용자 질문 문자열

        Returns:
            분류 결과 딕셔너리:
            - type (str): "structured" | "unstructured" | "hybrid"
            - confidence (float): 신뢰도 (0.0 ~ 1.0)
            - method (str): "rule" | "llm" | "default"

        Raises:
            ValueError: 질문이 빈 문자열인 경우
        """

        # --- Input ---
        if not question or not question.strip():
            raise ValueError("질문이 비어있습니다. 질문을 입력하십시오.")

        # --- Process ---
        # 1단계: 규칙 기반 분류
        query_type, confidence = self._rule_based_classify(question)

        if query_type is not None:
            return {
                "type": query_type,
                "confidence": confidence,
                "method": "rule",
            }

        # 2단계: LLM 분류 (LLM 연결 및 활성화 시)
        if self.use_llm_fallback and self.llm is not None:
            query_type, confidence = self._llm_classify(question)
            return {
                "type": query_type,
                "confidence": confidence,
                "method": "llm",
            }

        # 최종 기본값: 비정형 처리
        # --- Output ---
        return {
            "type": "unstructured",
            "confidence": 0.4,
            "method": "default",
        }
