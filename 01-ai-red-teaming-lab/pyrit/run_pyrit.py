import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from attacks.scoring import FindingRecord, load_attack_cases
from pyrit.orchestrator import build_attack_orchestrator
from pyrit.target import NorthwindPyRITTarget


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, default=str) + "\n" for record in records), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Northwind PyRIT prompt matrix.")
    parser.add_argument("--case-file", default="attacks/cases.yaml")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--fake-secret", default="NW-DUMMY-KEY-DO-NOT-USE")
    parser.add_argument("--raw-output", default="results/pyrit/raw.jsonl")
    parser.add_argument("--findings-output", default="results/pyrit/findings.jsonl")
    args = parser.parse_args(argv)

    cases = load_attack_cases(args.case_file)
    target = NorthwindPyRITTarget(args.base_url)
    results = build_attack_orchestrator(
        target,
        cases,
        converters=["base64", "rot13", "letter_by_letter"],
        scorers=["shared"],
    ).run(args.fake_secret)
    timestamp = datetime.now(timezone.utc).isoformat()
    raw_records = [{**result, "score": asdict(result["score"]), "timestamp": timestamp} for result in results]
    finding_records = []
    for index, result in enumerate(results, start=1):
        score = result["score"]
        finding_records.append(
            FindingRecord(
                finding_id=f"pyrit-{index:03d}-{result['attack_case_id']}-{result['converter']}",
                attack_case_id=result["attack_case_id"],
                tool="pyrit",
                timestamp=timestamp,
                target=args.base_url or "http://127.0.0.1:8000",
                model="northwind",
                observed_output_reference=str(Path(args.raw_output)),
                control="none",
                retest_status="not_run",
                residual_risk="unknown",
                owasp_mapping=[next(case for case in cases if case.id == result["attack_case_id"]).owasp_category],
                mitre_atlas_mapping=next(case for case in cases if case.id == result["attack_case_id"]).atlas_techniques,
                status=score.status,
                reason=score.reason,
                confidence=score.confidence,
                matched_indicators=score.matched_indicators,
                severity=next(case for case in cases if case.id == result["attack_case_id"]).severity,
            ).to_dict()
        )
    _write_jsonl(Path(args.raw_output), raw_records)
    _write_jsonl(Path(args.findings_output), finding_records)
    return 1 if any(record["status"] == "fail" for record in finding_records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
