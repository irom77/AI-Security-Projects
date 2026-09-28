from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from .config import Settings
from .guardrails import check_input, check_output
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
        if self.settings.enable_guardrails:
            input_decision = check_input(request.message)
            if not input_decision.allowed:
                return ChatResponse(
                    response="I can't help with that request, but I can help with Northwind support questions.",
                    model="guardrail",
                    session_id=request.session_id,
                    run_id=str(uuid4()),
                )
        model_response = self.model_client.generate(self.system_prompt, request.message)
        response_text = model_response.text
        if self.settings.enable_guardrails and not check_output(response_text, self.settings.fake_secret).allowed:
            response_text = "I can't share sensitive information or provide unsafe instructions."
        return ChatResponse(
            response=response_text,
            model=model_response.model,
            session_id=request.session_id,
            run_id=str(uuid4()),
        )
