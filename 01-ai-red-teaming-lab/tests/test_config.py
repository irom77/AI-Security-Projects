import pytest


def test_default_settings_use_local_ollama_and_placeholder_secret():
    from app.config import Settings

    settings = Settings.from_env({})

    assert settings.model_backend == "ollama"
    assert settings.model_name == "llama3.2:3b"
    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.fake_secret.startswith("NW-DUMMY-KEY-")
    assert settings.enable_guardrails is False
    assert settings.request_timeout_seconds == 30.0


def test_environment_values_override_defaults():
    from app.config import Settings

    settings = Settings.from_env(
        {
            "MODEL_BACKEND": "fake",
            "MODEL_NAME": "test-model",
            "OLLAMA_BASE_URL": "http://ollama.test:11434/",
            "FAKE_SECRET": "NW-DUMMY-KEY-OVERRIDE",
            "ENABLE_GUARDRAILS": "true",
            "REQUEST_TIMEOUT_SECONDS": "7.5",
        }
    )

    assert settings.model_backend == "fake"
    assert settings.model_name == "test-model"
    assert settings.ollama_base_url == "http://ollama.test:11434"
    assert settings.fake_secret == "NW-DUMMY-KEY-OVERRIDE"
    assert settings.enable_guardrails is True
    assert settings.request_timeout_seconds == 7.5


@pytest.mark.parametrize("secret", ["", "real-api-key", "sk-live-1234567890"])
def test_non_placeholder_secret_is_rejected(secret):
    from app.config import Settings, SettingsError

    with pytest.raises(SettingsError, match="placeholder"):
        Settings.from_env({"FAKE_SECRET": secret})
