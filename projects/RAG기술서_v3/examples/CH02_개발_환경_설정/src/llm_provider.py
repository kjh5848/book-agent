"""LLM Provider 팩토리 모듈.

.env의 LLM_PROVIDER 값에 따라 Ollama / OpenAI / vLLM 클라이언트를 반환하는
팩토리 패턴 구현체입니다.
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


# === 공통 베이스 클래스 ===

class BaseLLMClient:
    """모든 LLM 클라이언트가 구현해야 하는 추상 베이스 클래스.

    Attributes:
        model: 사용할 모델 이름
    """

    def __init__(self, model: str) -> None:
        """베이스 클라이언트를 초기화합니다.

        Args:
            model: LLM 모델 이름
        """
        self.model = model

    def generate(self, prompt: str) -> str:
        """프롬프트를 받아 LLM 응답을 생성합니다.

        Args:
            prompt: 사용자 입력 프롬프트 문자열

        Returns:
            LLM이 생성한 응답 문자열

        Raises:
            NotImplementedError: 하위 클래스에서 반드시 구현해야 합니다.
        """
        raise NotImplementedError("하위 클래스에서 generate() 메서드를 구현해야 합니다.")


# === Ollama 클라이언트 ===

class OllamaClient(BaseLLMClient):
    """Ollama 로컬 서버에 HTTP 요청을 보내는 LLM 클라이언트.

    Attributes:
        model: 사용할 Ollama 모델 이름 (예: deepseek-r1:8b)
        base_url: Ollama 서버 기본 URL (예: http://localhost:11434)
    """

    def __init__(self, model: str, base_url: str) -> None:
        """OllamaClient를 초기화합니다.

        Args:
            model: 사용할 Ollama 모델 이름
            base_url: Ollama 서버 기본 URL

        Raises:
            ValueError: base_url이 비어 있으면 발생합니다.
        """
        super().__init__(model)
        if not base_url:
            print("오류: OLLAMA_BASE_URL 환경 변수가 설정되지 않았습니다.")
            print(".env 파일에서 OLLAMA_BASE_URL 값을 확인하십시오.")
            sys.exit(1)
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        """Ollama /api/generate 엔드포인트를 호출하여 응답을 반환합니다.

        Args:
            prompt: 사용자 입력 프롬프트 문자열

        Returns:
            Ollama가 생성한 응답 문자열

        Raises:
            SystemExit: Ollama 서버에 연결할 수 없거나 오류 응답이 오면 종료합니다.
        """
        # === INPUT ===
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        # === PROCESS ===
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print("오류: Ollama 서버에 연결할 수 없습니다.")
            print("'ollama serve' 명령을 먼저 실행하십시오.")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("오류: Ollama 서버 응답 시간이 초과되었습니다.")
            print("모델 로딩 시간이 길 수 있습니다. 잠시 후 다시 시도하십시오.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"오류: Ollama 서버에서 HTTP 오류가 반환되었습니다. ({e})")
            sys.exit(1)

        # === OUTPUT ===
        result = response.json()
        return result.get("response", "").strip()


# === OpenAI 클라이언트 ===

class OpenAIClient(BaseLLMClient):
    """OpenAI API를 호출하는 LLM 클라이언트.

    Attributes:
        model: 사용할 OpenAI 모델 이름 (예: gpt-4o-mini)
        client: openai.OpenAI 인스턴스
    """

    def __init__(self, model: str, api_key: str) -> None:
        """OpenAIClient를 초기화합니다.

        Args:
            model: 사용할 OpenAI 모델 이름
            api_key: OpenAI API 키

        Raises:
            SystemExit: api_key가 비어 있으면 종료합니다.
        """
        super().__init__(model)
        if not api_key:
            print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            print(".env 파일에 API 키를 입력하십시오. (.env.example 참조)")
            sys.exit(1)

        try:
            import openai
        except ImportError:
            print("오류: openai 패키지가 설치되지 않았습니다.")
            print("pip install openai 명령을 실행하십시오.")
            sys.exit(1)

        self.client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """OpenAI Chat Completions API를 호출하여 응답을 반환합니다.

        Args:
            prompt: 사용자 입력 프롬프트 문자열

        Returns:
            OpenAI가 생성한 응답 문자열

        Raises:
            SystemExit: API 호출 오류 시 종료합니다.
        """
        # === INPUT ===
        messages = [{"role": "user", "content": prompt}]

        # === PROCESS ===
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except Exception as e:
            print(f"오류: OpenAI API 호출 중 문제가 발생했습니다. ({e})")
            print("API 키와 네트워크 연결을 확인하십시오.")
            sys.exit(1)

        # === OUTPUT ===
        return response.choices[0].message.content.strip()


# === vLLM 클라이언트 ===

class VLLMClient(BaseLLMClient):
    """vLLM 자체 호스팅 서버에 OpenAI 호환 API로 요청하는 LLM 클라이언트.

    vLLM은 OpenAI API와 호환되므로 openai 패키지를 그대로 사용합니다.

    Attributes:
        model: 사용할 vLLM 모델 이름
        base_url: vLLM 서버 기본 URL (예: http://localhost:8000)
        client: openai.OpenAI 인스턴스 (base_url 오버라이드)
    """

    def __init__(self, model: str, base_url: str) -> None:
        """VLLMClient를 초기화합니다.

        Args:
            model: 사용할 vLLM 모델 이름
            base_url: vLLM 서버 기본 URL

        Raises:
            SystemExit: base_url이 비어 있거나 openai 패키지 미설치 시 종료합니다.
        """
        super().__init__(model)
        if not base_url:
            print("오류: VLLM_BASE_URL 환경 변수가 설정되지 않았습니다.")
            print(".env 파일에서 VLLM_BASE_URL 값을 확인하십시오.")
            sys.exit(1)

        try:
            import openai
        except ImportError:
            print("오류: openai 패키지가 설치되지 않았습니다.")
            print("pip install openai 명령을 실행하십시오.")
            sys.exit(1)

        # vLLM은 OpenAI 호환 API를 제공하므로 base_url만 변경합니다.
        self.client = openai.OpenAI(
            api_key="not-needed",  # vLLM은 API 키가 필요 없습니다
            base_url=f"{base_url.rstrip('/')}/v1",
        )

    def generate(self, prompt: str) -> str:
        """vLLM 서버에 OpenAI 호환 Chat Completions 요청을 보내 응답을 반환합니다.

        Args:
            prompt: 사용자 입력 프롬프트 문자열

        Returns:
            vLLM이 생성한 응답 문자열

        Raises:
            SystemExit: 서버 연결 오류 시 종료합니다.
        """
        # === INPUT ===
        messages = [{"role": "user", "content": prompt}]

        # === PROCESS ===
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except Exception as e:
            print(f"오류: vLLM 서버 호출 중 문제가 발생했습니다. ({e})")
            print("vLLM 서버가 실행 중인지, VLLM_BASE_URL이 올바른지 확인하십시오.")
            sys.exit(1)

        # === OUTPUT ===
        return response.choices[0].message.content.strip()


# === 팩토리 함수 ===

def get_llm_client() -> BaseLLMClient:
    """환경 변수 LLM_PROVIDER 값에 따라 적합한 LLM 클라이언트를 반환합니다.

    .env 파일의 LLM_PROVIDER 값을 읽어 올바른 클라이언트 인스턴스를 생성합니다.
    - ollama: 로컬 Ollama 서버 (기본값, 무료)
    - openai: OpenAI API (API 키 필요, 유료)
    - vllm: 자체 호스팅 vLLM 서버 (무료)

    Returns:
        BaseLLMClient 하위 클래스의 인스턴스

    Raises:
        SystemExit: 지원하지 않는 LLM_PROVIDER 값이면 종료합니다.

    Example:
        >>> client = get_llm_client()
        >>> response = client.generate("안녕하세요")
        >>> print(response)
    """
    # === INPUT ===
    provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

    # === PROCESS ===
    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaClient(model=model, base_url=base_url)

    elif provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY", "")
        return OpenAIClient(model=model, api_key=api_key)

    elif provider == "vllm":
        model = os.getenv("VLLM_MODEL", "deepseek-r1")
        base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000")
        return VLLMClient(model=model, base_url=base_url)

    else:
        # === OUTPUT (오류) ===
        print(f"오류: 지원하지 않는 LLM_PROVIDER 값입니다. ('{provider}')")
        print("사용 가능한 값: ollama, openai, vllm")
        print(".env 파일의 LLM_PROVIDER 설정을 확인하십시오.")
        sys.exit(1)


def test_llm_connection() -> None:
    """현재 설정된 LLM Provider에 '안녕하세요'를 전송하여 연결을 테스트합니다.

    get_llm_client()로 클라이언트를 생성하고 간단한 인사말을 전송합니다.
    성공 시 응답을 출력하고, 실패 시 오류 메시지를 출력합니다.
    """
    # === INPUT ===
    test_prompt = "안녕하세요. 한 문장으로 자기소개를 해 주십시오."
    provider = os.getenv("LLM_PROVIDER", "ollama")

    print(f"[LLM Provider 연결 테스트]")
    print(f"  Provider : {provider}")

    # === PROCESS ===
    client = get_llm_client()
    print(f"  Model    : {client.model}")
    print(f"  질문     : {test_prompt}")
    print("-" * 50)

    response = client.generate(test_prompt)

    # === OUTPUT ===
    print(f"  응답     : {response}")
    print("-" * 50)
    print("LLM 연결 테스트 성공.")


if __name__ == "__main__":
    test_llm_connection()
