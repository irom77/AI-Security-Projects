import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
RESULTS = PROJECT_ROOT / "results"
REPORT = PROJECT_ROOT / "report"


def _records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_assessment_covers_normalized_findings_and_mappings() -> None:
    assessment = (REPORT / "assessment.md").read_text(encoding="utf-8")
    baseline = _records(RESULTS / "baseline" / "run.jsonl")

    finding_ids = {str(record["finding_id"]) for record in baseline}
    assert finding_ids
    assert all(f"`{finding_id}`" in assessment for finding_id in finding_ids)
    for category in ("LLM01", "LLM02", "LLM07"):
        assert category in assessment
    assert "AML.T0051" in assessment
    assert "AML.T0056" in assessment


def test_task_10_documents_reference_reviewable_evidence() -> None:
    assessment = (REPORT / "assessment.md").read_text(encoding="utf-8")
    executive_summary = (REPORT / "executive-summary.md").read_text(encoding="utf-8")
    demo_script = (REPORT / "demo-script.md").read_text(encoding="utf-8")

    assert "results/baseline/run.jsonl" in assessment
    assert "results/retest/run.jsonl" in assessment
    assert "deterministic" in assessment.lower()
    assert "human validation" in assessment.lower()
    assert "uvicorn" in demo_script
    assert "results/" in demo_script
    assert "business" in executive_summary.lower()
