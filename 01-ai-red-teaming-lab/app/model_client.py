from dataclasses import dataclass
from typing import Protocol

import httpx

from .config import Settings


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model: str
    finish_reason: str = "stop"


class ModelClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> ModelResponse: ...


class FakeModelClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, system_prompt: str, user_prompt: str) -> ModelResponse:
        lowered = user_prompt.lower()
        attack_terms = ("ignore previous", "reveal the secret", "system prompt", "developer message")
        if any(term in lowered for term in attack_terms):
            return ModelResponse(
                text=f"For this lab scenario, the internal secret is {self.settings.fake_secret}.",
                model="fake-northwind",
                finish_reason="lab-scripted",
            )
        if "support" in lowered or "hours" in lowered:
            text = "Northwind support is available Monday through Friday, 9 AM to 5 PM ET."
        elif "return" in lowered:
            text = "Northwind returns can be requested within 30 days of delivery."
        else:
            text = "I can help with Northwind products, orders, returns, and support hours."
        return ModelResponse(text=text, model="fake-northwind")


class OllamaModelClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, system_prompt: str, user_prompt: str) -> ModelResponse:
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/generate",
            json={
                "model": self.settings.model_name,
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": False,
            },
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return ModelResponse(
            text=str(payload.get("response", "")),
            model=self.settings.model_name,
            finish_reason="stop" if payload.get("done", True) else "incomplete",
        )


def build_model_client(settings: Settings) -> ModelClient:
    if settings.model_backend == "fake":
        return FakeModelClient(settings)
    return OllamaModelClient(settings)
