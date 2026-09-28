import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from uuid import uuid4

import httpx

from attacks.scoring import AttackCase, FindingRecord, load_attack_cases, score_response
from app.config import Settings


def _safe_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)


def run_attack_cases(
    base_url: str, cases: list[AttackCase], run_id: str, tool: str
) -> list[FindingRecord]:
    settings = Settings()
    safe_run_id = _safe_component(run_id)
    evidence_dir = Path("results") / "evidence" / safe_run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    records: list[FindingRecord] = []
    timestamp = datetime.now(timezone.utc).isoformat()

    with httpx.Client(timeout=settings.request_timeout_seconds) as client:
        for case in sorted(cases, key=lambda item: item.id):
            evidence_path = evidence_dir / f"{_safe_component(case.id)}.json"
            reference = evidence_path.as_posix()
            try:
                response = client.post(
                    f"{base_url.rstrip('/')}/chat",
                    json={"message": case.prompt, "session_id": run_id, "case_id": case.id},
                )
                response.raise_for_status()
                payload = response.json()
                response_text = str(payload.get("response", ""))
                evidence_path.write_text(
                    json.dumps({"case_id": case.id, "request": case.prompt, "response": payload}, indent=2)
                    + "\n",
                    encoding="utf-8",
                )
                score = score_response(case, response_text, settings.fake_secret)
                records.append(
                    FindingRecord(
                        finding_id=f"{safe_run_id}-{case.id}",
                        attack_case_id=case.id,
                        tool=tool,
                        timestamp=timestamp,
                        target=base_url,
                        model=str(payload.get("model", "unknown")),
                        observed_output_reference=reference,
                        control="configured target controls",
                        retest_status="not_run",
                        residual_risk=case.severity if score.status == "fail" else "unknown",
                        owasp_mapping=[case.owasp_category],
                        mitre_atlas_mapping=case.atlas_techniques,
                        status=score.status,
                        reason=score.reason,
                        confidence=score.confidence,
                        matched_indicators=score.matched_indicators,
                        severity=case.severity,
                    )
                )
            except httpx.TimeoutException as exc:
                reason = f"Request timeout: {exc}"
                evidence_path.write_text(
                    json.dumps({"case_id": case.id, "request": case.prompt, "error": reason}, indent=2) + "\n",
                    encoding="utf-8",
                )
                records.append(
                    FindingRecord(
                        finding_id=f"{safe_run_id}-{case.id}",
                        attack_case_id=case.id,
                        tool=tool,
                        timestamp=timestamp,
                        target=base_url,
                        model="unknown",
                        observed_output_reference=reference,
                        control="configured target controls",
                        retest_status="not_run",
                        residual_risk=case.severity,
                        owasp_mapping=[case.owasp_category],
                        mitre_atlas_mapping=case.atlas_techniques,
                        status="error",
                        reason=reason,
                        confidence="high",
                        matched_indicators=[],
                        severity=case.severity,
                    )
                )
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                reason = f"Request failed: {exc}"
                evidence_path.write_text(
                    json.dumps({"case_id": case.id, "request": case.prompt, "error": reason}, indent=2) + "\n",
                    encoding="utf-8",
                )
                records.append(
                    FindingRecord(
                        finding_id=f"{safe_run_id}-{case.id}",
                        attack_case_id=case.id,
                        tool=tool,
                        timestamp=timestamp,
                        target=base_url,
                        model="unknown",
                        observed_output_reference=reference,
                        control="configured target controls",
                        retest_status="not_run",
                        residual_risk=case.severity,
                        owasp_mapping=[case.owasp_category],
                        mitre_atlas_mapping=case.atlas_techniques,
                        status="error",
                        reason=reason,
                        confidence="high",
                        matched_indicators=[],
                        severity=case.severity,
                    )
                )
    return records


def _write_jsonl(path: Path, records: Sequence[FindingRecord | dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            payload = record.to_dict() if isinstance(record, FindingRecord) else record
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the stable Northwind attack corpus.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--mode", choices=("vulnerable", "controlled"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case-file", type=Path, default=Path("attacks/cases.yaml"))
    parser.add_argument("--run-id", default=f"run-{uuid4().hex[:12]}")
    parser.add_argument("--tool", default="local-runner")
    args = parser.parse_args(argv)
    cases = load_attack_cases(args.case_file)
    records = run_attack_cases(args.base_url, cases, args.run_id, args.tool)
    _write_jsonl(args.output, records)
    return 1 if any(
        (record.status if isinstance(record, FindingRecord) else record.get("status")) in {"fail", "error"}
        for record in records
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())
