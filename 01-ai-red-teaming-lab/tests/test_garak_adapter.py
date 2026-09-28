import importlib.util
from pathlib import Path

import httpx
import pytest


GENERATOR_PATH = Path(__file__).parents[1] / "garak" / "generator.py"
SPEC = importlib.util.spec_from_file_location("northwind_garak_generator", GENERATOR_PATH)
generator_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(generator_module)
NorthwindGenerator = generator_module.NorthwindGenerator


def load_prompt(prompt: str):
    try:
        from garak.attempt import Conversation, Message, Turn

        return Conversation([Turn("user", Message(prompt))])
    except ModuleNotFoundError:
        return prompt


def test_generator_forwards_prompt_and_run_metadata():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "response": "safe response",
                "model": "fake-model",
                "session_id": "garak-session",
                "run_id": "run-123",
            },
            request=request,
        )

    generator = NorthwindGenerator(
        target_url="http://target.test/base",
        timeout=7.5,
        transport=httpx.MockTransport(handler),
        run_id="run-123",
        attack_id="encoding.base64",
    )

    output = generator._call_model(load_prompt("decode this"))[0]

    assert requests[0].url == "http://target.test/base/chat"
    assert requests[0].read().decode() == (
        '{"message":"decode this","session_id":"garak-run-123",'
        '"run_id":"run-123","attack_id":"encoding.base64"}'
    )
    assert output.text == "safe response"
    assert output.notes["garak"]["attack_id"] == "encoding.base64"
    assert output.notes["garak"]["run_id"] == "run-123"


def test_generator_reads_target_url_from_environment(monkeypatch):
    monkeypatch.setenv("NORTHWIND_CHATBOT_URL", "http://env-target.test")

    generator = NorthwindGenerator(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"response": "ok"}, request=request)))

    assert generator.target_url == "http://env-target.test"


def test_generator_rejects_non_positive_timeout():
    with pytest.raises(ValueError, match="timeout must be greater than zero"):
        NorthwindGenerator(target_url="http://target.test", timeout=0)


def test_generator_propagates_timeout_to_http_client():
    extensions = []

    def handler(request: httpx.Request) -> httpx.Response:
        extensions.append(request.extensions["timeout"])
        return httpx.Response(200, json={"response": "ok"}, request=request)

    generator = NorthwindGenerator(
        target_url="http://target.test",
        timeout=4.25,
        transport=httpx.MockTransport(handler),
    )

    generator._call_model(load_prompt("timeout check"))

    assert extensions[0]["read"] == 4.25


def test_generator_preserves_endpoint_metadata_in_garak_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "response": "answer",
                "model": "northwind-test",
                "session_id": "session-42",
                "run_id": "run-42",
            },
            request=request,
        )

    generator = NorthwindGenerator(
        target_url="http://target.test",
        transport=httpx.MockTransport(handler),
    )

    output = generator._call_model(load_prompt("hello"))[0]

    assert output.notes["garak"]["model"] == "northwind-test"
    assert output.notes["garak"]["session_id"] == "session-42"
    assert output.notes["garak"]["run_id"] == "run-42"
