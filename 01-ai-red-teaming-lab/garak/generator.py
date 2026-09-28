"""Garak generator adapter for the Northwind chatbot HTTP endpoint."""

from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

import httpx

try:  # Garak is an optional scanner dependency for this lab.
    from garak.attempt import Message
except ModuleNotFoundError:  # pragma: no cover - exercised when Garak is absent.
    class Message:
        def __init__(self, text: str, notes: dict[str, Any] | None = None) -> None:
            self.text = text
            self.notes = notes or {}


class NorthwindGenerator:
    """Minimal Garak-compatible generator for the Northwind ``/chat`` API."""

    active = True
    generator_family_name = "Northwind HTTP"
    supports_multiple_generations = False
    parallel_capable = True

    def __init__(
        self,
        name: str = "northwind",
        target_url: str | None = None,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        run_id: str | None = None,
        attack_id: str | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.name = name
        self.target_url = (target_url or os.environ.get("NORTHWIND_CHATBOT_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout
        self.run_id = run_id or os.environ.get("GARAK_RUN_ID", str(uuid4()))
        self.attack_id = attack_id or os.environ.get("GARAK_ATTACK_ID", "unknown")
        self.client = httpx.Client(timeout=timeout, transport=transport)

    def _call_model(self, prompt: Any, generations_this_call: int = 1) -> list[Message | None]:
        """Send one prompt and return the response in Garak's list contract."""
        if generations_this_call != 1:
            raise ValueError("NorthwindGenerator supports one generation per request")
        prompt_text = self._prompt_text(prompt)
        response = self.client.post(
            f"{self.target_url}/chat",
            json={
                "message": prompt_text,
                "session_id": f"garak-{self.run_id}",
                "run_id": self.run_id,
                "attack_id": self.attack_id,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return [
            Message(
                text=str(payload["response"]),
                notes={
                    "garak": {
                        "attack_id": self.attack_id,
                        "model": payload.get("model"),
                        "run_id": payload.get("run_id", self.run_id),
                        "session_id": payload.get("session_id"),
                    }
                },
            )
        ]

    @staticmethod
    def _prompt_text(prompt: Any) -> str:
        if isinstance(prompt, str):
            return prompt
        return prompt.last_message().text

    def close(self) -> None:
        self.client.close()
