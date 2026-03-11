"""
LLM 초기화 서비스.

LLM_PROVIDER 환경 변수(ollama | openai)에 따라 LLM을 초기화하고,
Jinja2 템플릿 기반 프롬프트 렌더링과 LLM 호출을 제공합니다.

환경 변수:
    LLM_PROVIDER: LLM 공급자 (기본값: ollama)
    LLM_MODEL_NAME: 모델명 (기본값: deepseek-r1:1.5b)
    OLLAMA_BASE_URL: Ollama 서버 URL (기본값: http://localhost:11434)
    OPENAI_API_KEY: OpenAI API 키 (PROVIDER=openai 시 필요)
"""

import json
import os
import re

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()


class LLMService:
    """LLM 초기화 및 프롬프트 렌더링 서비스.

    LLM_PROVIDER 환경 변수에 따라 Ollama 또는 OpenAI LLM을 초기화합니다.
    Jinja2 Environment를 설정하여 app/prompts/ 디렉토리의 템플릿을 렌더링합니다.

    Attributes:
        provider: LLM 공급자 문자열 (ollama | openai).
        model_name: 사용할 모델명.
        llm: 초기화된 LangChain LLM 객체.
        jinja_env: Jinja2 템플릿 환경.
    """

    def __init__(self) -> None:
        """
        환경 변수를 읽어 LLM과 Jinja2 Environment를 초기화합니다.

        LLM_PROVIDER=ollama 이면 ChatOllama, openai 이면 ChatOpenAI를 사용합니다.
        """
        # --- Input ---
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.model_name = os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # --- Process ---
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0,
            )
        else:
            from langchain_ollama import ChatOllama

            self.llm = ChatOllama(
                model=self.model_name,
                base_url=ollama_base_url,
                temperature=0,
            )

        # Jinja2 Environment 초기화
        prompts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts",
        )
        self.jinja_env = Environment(
            loader=FileSystemLoader(prompts_dir),
            autoescape=False,
        )

        # --- Output ---
        print(f"[LLMService] 초기화 완료 — provider={self.provider}, model={self.model_name}")

    def render_prompt(self, template_name: str, **kwargs: object) -> str:
        """
        app/prompts/ 디렉토리의 Jinja2 템플릿을 렌더링합니다.

        Args:
            template_name: 템플릿 파일명 (예: "router_prompt.j2").
            **kwargs: 템플릿에 전달할 변수.

        Returns:
            str: 렌더링된 프롬프트 문자열.

        Raises:
            Exception: 템플릿 파일이 존재하지 않거나 렌더링 실패 시.
        """
        # --- Input ---
        # --- Process ---
        template = self.jinja_env.get_template(template_name)
        # --- Output ---
        return template.render(**kwargs)

    def invoke(self, prompt: str) -> str:
        """
        LLM을 호출하고 응답 텍스트를 반환합니다.

        DeepSeek 모델의 <think>...</think> 태그를 자동으로 제거합니다.

        Args:
            prompt: LLM에 전달할 프롬프트 문자열.

        Returns:
            str: LLM 응답 텍스트 (think 태그 제거 후).

        Raises:
            Exception: LLM 호출 실패 시.
        """
        # --- Input ---
        # --- Process ---
        response = self.llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)

        # DeepSeek <think>...</think> 태그 제거
        cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

        # --- Output ---
        return cleaned

    def generate_answer(self, query: str, context: str) -> str:
        """
        answer_prompt.j2 템플릿을 렌더링하여 LLM 답변을 생성합니다.

        Args:
            query: 사용자 질의 문자열.
            context: 검색된 컨텍스트 문자열.

        Returns:
            str: LLM이 생성한 한국어 답변.
        """
        # --- Input ---
        # --- Process ---
        prompt = self.render_prompt("answer_prompt.j2", query=query, context=context)
        # --- Output ---
        return self.invoke(prompt)

    def classify_intent(self, query: str) -> dict:
        """
        router_prompt.j2 템플릿으로 사용자 질의의 인텐트를 분류합니다.

        Args:
            query: 사용자 질의 문자열.

        Returns:
            dict: {"route": "unstructured|hybrid", "reason": "분류 이유"}.
                  JSON 파싱 실패 시 {"route": "hybrid", "reason": "분석 오류"} 반환.
        """
        # --- Input ---
        # --- Process ---
        try:
            prompt = self.render_prompt("router_prompt.j2", query=query)
            raw = self.invoke(prompt)

            # JSON 파싱 시도 (마크다운 코드 블록 제거 후)
            cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
            result = json.loads(cleaned)

            if "route" not in result:
                raise ValueError("route 키가 없습니다.")

            # --- Output ---
            return result

        except Exception:
            return {"route": "hybrid", "reason": "분석 오류"}


# 싱글톤 인스턴스
llm_service = LLMService()
