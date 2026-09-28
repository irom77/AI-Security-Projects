"""Configuration for the isolated red-teaming lab target."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class SettingsError(ValueError):
    """Raised when a lab setting violates the safety boundary."""


@dataclass(frozen=True)
class Settings:
    """Runtime settings with safe, local-only defaults."""

    model_name: str = "llama3.2:3b"
    model_backend: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    fake_secret: str = "NW-DUMMY-KEY-DO-NOT-USE"
    enable_guardrails: bool = False
    request_timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if environ is None else environ
        fake_secret = values.get("FAKE_SECRET", cls.fake_secret)
        if not fake_secret.startswith("NW-DUMMY-KEY-"):
            raise SettingsError("FAKE_SECRET must be a safe NW-DUMMY-KEY- placeholder")

        backend = values.get("MODEL_BACKEND", cls.model_backend).strip().lower()
        if backend not in {"ollama", "fake", "api"}:
            raise SettingsError("MODEL_BACKEND must be ollama, fake, or api")

        try:
            timeout = float(values.get("REQUEST_TIMEOUT_SECONDS", cls.request_timeout_seconds))
        except (TypeError, ValueError) as exc:
            raise SettingsError("REQUEST_TIMEOUT_SECONDS must be a number") from exc
        if timeout <= 0:
            raise SettingsError("REQUEST_TIMEOUT_SECONDS must be greater than zero")

        return cls(
            model_name=values.get("MODEL_NAME", cls.model_name).strip(),
            model_backend=backend,
            ollama_base_url=values.get("OLLAMA_BASE_URL", cls.ollama_base_url).rstrip("/"),
            fake_secret=fake_secret,
            enable_guardrails=_parse_bool(values.get("ENABLE_GUARDRAILS", "false")),
            request_timeout_seconds=timeout,
        )


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise SettingsError("ENABLE_GUARDRAILS must be a boolean")

