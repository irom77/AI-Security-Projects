import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
REPO_ROOT = PROJECT_ROOT.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "red-team-lab.yml"


def test_workflow_declares_reproducible_required_checks_and_artifacts():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for changed_path in (
        "01-ai-red-teaming-lab/**",
        ".github/workflows/red-team-lab.yml",
    ):
        assert changed_path in workflow
    for required_surface in (
        "actions/checkout@v4",
        "actions/setup-python@v5",
        "actions/setup-node@v4",
        "pytest -q",
        "python -m uvicorn app.main:app",
        "python tools/run_attacks.py",
        "--mode controlled",
        "promptfoo eval",
        "actions/upload-artifact@v4",
        "if: always()",
    ):
        assert required_surface in workflow
    assert "raise SystemExit(1 if blocking else 0)" in workflow


def test_metadata_cli_writes_reproducible_run_metadata(tmp_path):
    output_path = tmp_path / "metadata.json"
    command = [
        sys.executable,
        "tools/collect_run_metadata.py",
        "--output",
        str(output_path),
        "--mode",
        "controlled",
        "--model",
        "fake-model",
        "--backend",
        "fake",
        "--command",
        "python tools/run_attacks.py --mode controlled",
    ]

    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    metadata = json.loads(output_path.read_text(encoding="utf-8"))

    assert metadata["target_mode"] == "controlled"
    assert metadata["model"] == "fake-model"
    assert metadata["backend"] == "fake"
    assert metadata["commit_sha"]
    assert len(metadata["case_corpus_sha256"]) == 64
    assert metadata["timestamp_utc"].endswith("+00:00")
    assert metadata["commands"] == ["python tools/run_attacks.py --mode controlled"]
    assert "python" in metadata["tool_versions"]
