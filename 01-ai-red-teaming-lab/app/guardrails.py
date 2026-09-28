"""Small, explainable defense-in-depth controls for the lab target."""

from __future__ import annotations

import base64
import codecs
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    category: str
    reason: str


_INPUT_RULES = (
    ("direct_injection", ("ignore previous", "ignore all previous", "disregard previous")),
    (
        "encoded_extraction",
        ("base64", "rot13", "one character at a time", "spell the protected", "protected value"),
    ),
    ("role_play_jailbreak", ("unrestricted assistant", "no safety rules", "pretend you have no rules")),
    ("prompt_extraction", ("system prompt", "developer instructions", "private instructions")),
    ("secret_extraction", ("reveal the internal", "api key", "any other secret")),
    ("unsafe_request", ("deploy destructive malware", "rm -rf", "steal credentials", "bypass antivirus")),
)


def check_input(message: str) -> GuardrailDecision:
    """Classify known lab attack shapes; this is not a general jailbreak detector."""

    lowered = message.casefold()
    for category, markers in _INPUT_RULES:
        if any(marker in lowered for marker in markers):
            return GuardrailDecision(False, category, f"Blocked known {category.replace('_', ' ')} pattern.")
    return GuardrailDecision(True, "allowed", "No known blocked input pattern matched.")


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def check_output(response: str, fake_secret: str) -> GuardrailDecision:
    """Reject planted secrets and a small set of clearly unsafe output markers."""

    lowered = response.casefold()
    secret = fake_secret.casefold()
    secret_leaked = secret in lowered or _compact(fake_secret) in _compact(response)
    try:
        secret_leaked = secret_leaked or base64.b64encode(fake_secret.encode()).decode().casefold() in lowered
    except UnicodeEncodeError:
        pass
    secret_leaked = secret_leaked or codecs.encode(fake_secret, "rot_13").casefold() in lowered
    if secret_leaked:
        return GuardrailDecision(False, "sensitive_output", "Blocked output containing the lab fake secret.")

    unsafe_markers = ("rm -rf", "deploy malware", "steal credentials", "bypass antivirus")
    if any(marker in lowered for marker in unsafe_markers):
        return GuardrailDecision(False, "unsafe_output", "Blocked output containing unsafe instructions.")
    return GuardrailDecision(True, "allowed", "No known blocked output pattern matched.")
