"""Promptfoo provider for the Northwind chatbot HTTP target."""

from __future__ import annotations

import json
import os
from urllib import request


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """Forward a Promptfoo prompt to POST /chat and preserve run metadata."""

    config = options.get("config", {})
    base_url = str(config.get("url") or os.environ.get("NORTHWIND_CHATBOT_URL", "")).rstrip("/")
    if not base_url:
        raise ValueError("NORTHWIND_CHATBOT_URL must identify the chatbot base URL")

    variables = context.get("vars", {})
    attack_id = str(variables.get("attack_id", "unknown"))
    payload = json.dumps(
        {"message": prompt, "session_id": f"promptfoo-{attack_id}", "case_id": attack_id}
    ).encode("utf-8")
    request_obj = request.Request(
        f"{base_url}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(request_obj, timeout=float(config.get("timeout_seconds", 30))) as response:
        body = json.loads(response.read().decode("utf-8"))

    return {
        "output": str(body["response"]),
        "metadata": {
            "attack_id": attack_id,
            "target": f"{base_url}/chat",
            "model": str(body.get("model", "unknown")),
            "promptfoo_version": os.environ.get("PROMPTFOO_VERSION", "unknown"),
        },
    }
