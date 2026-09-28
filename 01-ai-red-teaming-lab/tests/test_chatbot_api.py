from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_reports_configuration_without_sensitive_prompt_or_secret():
    settings = Settings(model_backend="fake")
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["backend"] == "fake"
    assert body["model"] == settings.model_name
    assert body["configured"] is True
    assert settings.fake_secret not in response.text
    assert "system" not in body


def test_chat_returns_text_metadata_and_correlation_id():
    settings = Settings(model_backend="fake")
    client = TestClient(create_app(settings))

    response = client.post(
        "/chat", json={"message": "What are your support hours?", "session_id": "session-1"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["response"]
    assert body["model"] == "fake-northwind"
    assert body["session_id"] == "session-1"
    assert isinstance(body["run_id"], str) and body["run_id"]
    assert settings.fake_secret not in body["response"]


def test_chat_accepts_null_session_id_and_rejects_blank_message():
    client = TestClient(create_app(Settings(model_backend="fake")))

    response = client.post("/chat", json={"message": "Tell me about returns", "session_id": None})
    invalid = client.post("/chat", json={"message": "   "})

    assert response.status_code == 200
    assert response.json()["session_id"] is None
    assert invalid.status_code == 422
