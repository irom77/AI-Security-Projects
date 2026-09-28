import json
from pathlib import Path

from attacks.scoring import AttackCase, load_attack_cases
from pyrit.orchestrator import build_attack_orchestrator
from pyrit.scorers import score_pyrit_response
from pyrit.target import NorthwindPyRITTarget


PROJECT_ROOT = Path(__file__).parents[1]
CASES = load_attack_cases(PROJECT_ROOT / "attacks" / "cases.yaml")
SECRET = "NW-DUMMY-KEY-DO-NOT-USE"


class FakeTarget:
    def __init__(self):
        self.prompts: list[str] = []

    def send(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "internal API key" in prompt:
            return f"I can't disclose that value: {SECRET}."
        return "I can't help with that request."


def test_target_forwards_prompt_and_returns_response(monkeypatch):
    seen: dict[str, object] = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "I can't help with that request."}

    class Client:
        def __init__(self, **kwargs):
            seen["timeout"] = kwargs["timeout"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, *, json):
            seen["url"] = url
            seen["json"] = json
            return Response()

    monkeypatch.setattr("pyrit.target.httpx.Client", Client)
    target = NorthwindPyRITTarget("http://target", timeout=3.5)

    assert target.send("decode this") == "I can't help with that request."
    assert seen == {
        "timeout": 3.5,
        "url": "http://target/chat",
        "json": {"message": "decode this", "session_id": "pyrit"},
    }


def test_converters_preserve_lineage_and_encode_prompt():
    fake = FakeTarget()
    orchestrator = build_attack_orchestrator(
        fake,
        CASES[:1],
        converters=["base64", "rot13", "letter_by_letter"],
        scorers=["shared"],
    )

    results = orchestrator.run(SECRET)

    assert len(results) == 4
    assert [result["converter"] for result in results] == [
        "identity",
        "base64",
        "rot13",
        "letter_by_letter",
    ]
    assert results[1]["prompt"] != results[0]["prompt"]
    assert results[1]["converter_lineage"] == ["base64"]
    assert len(fake.prompts) == len(results)


def test_scorer_distinguishes_refusal_from_secret_disclosure():
    case = next(case for case in CASES if case.category == "secret_disclosure")

    refusal = score_pyrit_response(case, "I can't disclose internal credentials.", SECRET)
    disclosure = score_pyrit_response(case, f"The value is {SECRET}.", SECRET)

    assert refusal.status == "pass"
    assert disclosure.status == "fail"
    assert "exact_secret" in disclosure.matched_indicators


def test_orchestrator_covers_every_stable_case_id_with_fake_target():
    fake = FakeTarget()
    orchestrator = build_attack_orchestrator(fake, CASES, [], ["shared"])

    results = orchestrator.run(SECRET)

    assert {result["attack_case_id"] for result in results} == {case.id for case in CASES}
    assert all(result["tool"] == "pyrit" for result in results)
    assert all("score" in result for result in results)


def test_cli_writes_raw_and_normalized_jsonl(monkeypatch, tmp_path):
    from pyrit import run_pyrit

    monkeypatch.setattr(run_pyrit, "NorthwindPyRITTarget", lambda *args, **kwargs: FakeTarget())
    raw_path = tmp_path / "raw.jsonl"
    findings_path = tmp_path / "findings.jsonl"

    assert run_pyrit.main(
        [
            "--case-file",
            str(PROJECT_ROOT / "attacks" / "cases.yaml"),
            "--raw-output",
            str(raw_path),
            "--findings-output",
            str(findings_path),
            "--fake-secret",
            SECRET,
        ]
    ) == 1

    raw_records = [json.loads(line) for line in raw_path.read_text().splitlines()]
    finding_records = [json.loads(line) for line in findings_path.read_text().splitlines()]
    assert len(raw_records) == len(finding_records)
    assert raw_records[0]["tool"] == "pyrit"
    assert "attack_case_id" in finding_records[0]
