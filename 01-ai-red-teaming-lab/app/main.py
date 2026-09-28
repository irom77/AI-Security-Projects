from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from .chatbot import ChatRequest, Chatbot
from .config import Settings


class ChatPayload(BaseModel):
    message: str
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    active_settings = settings or Settings.from_env()
    chatbot = Chatbot(active_settings)
    app = FastAPI(title="Northwind Red Team Target")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "backend": active_settings.model_backend,
            "model": active_settings.model_name,
            "configured": True,
        }

    @app.post("/chat")
    def chat(payload: ChatPayload) -> dict[str, object]:
        result = chatbot.respond(ChatRequest(message=payload.message, session_id=payload.session_id))
        return asdict(result)

    return app


app = create_app()
