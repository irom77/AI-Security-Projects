import os
from typing import Any

import httpx


class NorthwindPyRITTarget:
    """Small PyRIT-shaped target adapter for the Northwind `/chat` endpoint."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = (base_url or os.environ.get("NORTHWIND_CHATBOT_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout

    def send(self, prompt: str) -> str:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/chat",
                json={"message": prompt, "session_id": "pyrit"},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
        return str(payload["response"])
