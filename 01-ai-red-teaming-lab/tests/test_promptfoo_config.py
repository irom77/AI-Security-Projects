from pathlib import Path

import yaml

from attacks.scoring import load_attack_cases


PROJECT_ROOT = Path(__file__).parents[1]
PROMPTFOO_ROOT = PROJECT_ROOT / "promptfoo"
CASES_PATH = PROJECT_ROOT / "attacks" / "cases.yaml"


def _load_config() -> dict:
    return yaml.safe_load(
        (PROMPTFOO_ROOT / "promptfooconfig.yaml").read_text(encoding="utf-8")
    )


def test_promptfoo_matrix_covers_every_stable_attack_case():
    cases = load_attack_cases(CASES_PATH)
    config = _load_config()
    prompts = yaml.safe_load((PROMPTFOO_ROOT / "prompts.yaml").read_text(encoding="utf-8"))

    configured_ids = {
        test["vars"]["attack_id"]
        for test in config["tests"]
        if "attack_id" in test.get("vars", {})
    }
    assert configured_ids == {case.id for case in cases}
    assert prompts == ["{{ attack_prompt }}"]
    assert {test["metadata"]["category"] for test in config["tests"]} >= {
        "direct_injection",
        "jailbreak_persona",
        "prompt_extraction",
        "secret_disclosure",
        "encoding_evasion",
        "unsafe_output",
    }


def test_promptfoo_provider_uses_environment_configurable_chat_url():
    config = _load_config()
    provider = config["providers"][0]

    assert provider["id"] == "file://provider.py"
    assert provider["config"]["url"] == "{{ env.NORTHWIND_CHATBOT_URL }}"
    assert provider["config"]["url"].startswith("{{ env.")


def test_promptfoo_assertions_use_stable_indicators_and_accept_refusal():
    config = _load_config()
    assertions = config["defaultTest"]["assert"]
    assertion_text = "\n".join(str(assertion.get("value", "")) for assertion in assertions)

    assert all(assertion["type"] == "javascript" for assertion in assertions)
    assert "exact_secret" in assertion_text
    assert "base64_secret" in assertion_text
    assert "rot13_secret" in assertion_text
    assert "unsafe_instruction" in assertion_text
    assert "cannot confirm or deny" in assertion_text
    assert "i can't" in assertion_text
    assert "response text" not in assertion_text.lower()


def test_promptfoo_writes_versioned_json_results_to_project_results():
    config = _load_config()

    assert config["outputPath"] == "results/promptfoo/latest.json"
    assert config["metadata"]["promptfoo_version"]
    assert config["metadata"]["evidence_format"] == "promptfoo-json"
