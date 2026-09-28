from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from .config import Settings
from .model_client import ModelClient, build_model_client
from .prompts import build_system_prompt


@dataclass(frozen=True)
class ChatRequest:
    message: str
    session_id: Optional[str] = None


@dataclass(frozen=True)
class ChatResponse:
    response: str
    model: str
    session_id: Optional[str]
    run_id: str


class Chatbot:
    def __init__(self, settings: Settings, model_client: Optional[ModelClient] = None):
        self.settings = settings
        self.model_client = model_client or build_model_client(settings)
        self.system_prompt = build_system_prompt(settings)

    def respond(self, request: ChatRequest) -> ChatResponse:
        model_response = self.model_client.generate(self.system_prompt, request.message)
        return ChatResponse(
            response=model_response.text,
            model=model_response.model,
            session_id=request.session_id,
            run_id=str(uuid4()),
        )
