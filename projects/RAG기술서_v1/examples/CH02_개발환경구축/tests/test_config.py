"""test_config.py — config.py 단위 테스트

이 테스트 파일은 환경 변수 로딩 및 설정 함수가 올바르게 동작하는지 검증합니다.
실제 외부 서비스(Ollama, PostgreSQL) 없이 독립적으로 실행할 수 있습니다.

실행 방법:
    pytest tests/test_config.py -v
"""

import os
import sys
from pathlib import Path

import pytest

# 테스트 실행 시 src 모듈을 찾을 수 있도록 경로를 추가합니다.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestGetLlmConfig:
    """get_llm_config 함수 테스트 모음"""

    def test_ollama_provider_returns_correct_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """LLM_PROVIDER=ollama 설정 시 올바른 키를 반환하는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_MODEL", "deepseek-r1")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # --- Process ---
        # 모듈을 다시 임포트하여 환경 변수 변경을 반영합니다.
        import importlib
        import config
        importlib.reload(config)
        result = config.get_llm_config()

        # --- Output ---
        assert result["provider"] == "ollama"
        assert result["model"] == "deepseek-r1"
        assert result["base_url"] == "http://localhost:11434"

    def test_unsupported_provider_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """지원하지 않는 LLM_PROVIDER 값 입력 시 SystemExit이 발생하는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.setenv("LLM_PROVIDER", "unsupported_provider")

        # --- Process ---
        import importlib
        import config
        importlib.reload(config)

        # --- Output ---
        with pytest.raises(SystemExit):
            config.get_llm_config()


class TestGetPostgresUrl:
    """get_postgres_url 함수 테스트 모음"""

    def test_url_format_is_correct(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PostgreSQL 접속 URL이 올바른 형식으로 생성되는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.setenv("POSTGRES_HOST", "localhost")
        monkeypatch.setenv("POSTGRES_PORT", "5432")
        monkeypatch.setenv("POSTGRES_DB", "test_db")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")

        # --- Process ---
        import importlib
        import config
        importlib.reload(config)
        url = config.get_postgres_url()

        # --- Output ---
        assert url == "postgresql://testuser:testpass@localhost:5432/test_db"

    def test_url_contains_all_components(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """생성된 URL에 모든 접속 정보가 포함되는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.setenv("POSTGRES_HOST", "db.example.com")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_DB", "company_db")
        monkeypatch.setenv("POSTGRES_USER", "admin")
        monkeypatch.setenv("POSTGRES_PASSWORD", "secret")

        # --- Process ---
        import importlib
        import config
        importlib.reload(config)
        url = config.get_postgres_url()

        # --- Output ---
        assert "db.example.com" in url
        assert "5433" in url
        assert "company_db" in url
        assert "admin" in url
        assert "secret" in url


class TestRequireEnv:
    """_require_env 함수 테스트 모음"""

    def test_missing_env_var_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """필수 환경 변수 누락 시 SystemExit이 발생하는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.delenv("NON_EXISTENT_VAR", raising=False)

        # --- Process ---
        import importlib
        import config
        importlib.reload(config)

        # --- Output ---
        with pytest.raises(SystemExit):
            config._require_env("NON_EXISTENT_VAR")

    def test_existing_env_var_returns_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """존재하는 환경 변수의 값을 올바르게 반환하는지 확인합니다.

        Args:
            monkeypatch: pytest 환경 변수 패치 픽스처
        """

        # --- Input ---
        monkeypatch.setenv("TEST_VAR", "hello")

        # --- Process ---
        import importlib
        import config
        importlib.reload(config)
        result = config._require_env("TEST_VAR")

        # --- Output ---
        assert result == "hello"
