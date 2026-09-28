from pathlib import Path

from attacks.scoring import AttackCase, FindingRecord, load_attack_cases


CORPUS_PATH = Path(__file__).parents[1] / "attacks" / "cases.yaml"


def test_corpus_contains_stable_cases_for_required_attack_categories():
    cases = load_attack_cases(CORPUS_PATH)

    assert len(cases) >= 7
    assert {case.category for case in cases} >= {
        "direct_injection",
        "jailbreak_persona",
        "prompt_extraction",
        "secret_disclosure",
        "encoding_evasion",
        "unsafe_output",
    }
    assert all(isinstance(case, AttackCase) for case in cases)
    assert len({case.id for case in cases}) == len(cases)
    assert all(case.owasp_category and case.atlas_techniques for case in cases)


def test_finding_record_has_required_json_fields_and_serializes():
    record = FindingRecord(
        finding_id="F-001",
        attack_case_id="secret-disclosure-001",
        tool="pytest",
        timestamp="2026-09-28T12:00:00Z",
        target="northwind-chatbot",
        model="fake-northwind",
        observed_output_reference="results/run.jsonl#1",
        control="output filter",
        retest_status="not_run",
        residual_risk="high",
        owasp_mapping=["LLM02"],
        mitre_atlas_mapping=["AML.T0051"],
    )

    payload = record.to_dict()

    assert payload["finding_id"] == "F-001"
    assert payload["attack_case_id"] == "secret-disclosure-001"
    assert payload["observed_output_reference"] == "results/run.jsonl#1"
    assert payload["owasp_mapping"] == ["LLM02"]
    assert payload["mitre_atlas_mapping"] == ["AML.T0051"]
