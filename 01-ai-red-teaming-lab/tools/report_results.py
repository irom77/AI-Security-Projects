import argparse
import json
from pathlib import Path
from typing import Iterable


def load_records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def render_markdown(records: Iterable[dict[str, object]]) -> str:
    lines = [
        "# Red-team run results",
        "",
        "| Finding | Case | Status | Severity | Mappings | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        owasp = ", ".join(str(item) for item in record.get("owasp_mapping", []))
        atlas = ", ".join(str(item) for item in record.get("mitre_atlas_mapping", []))
        mappings = "; ".join(item for item in (owasp, atlas) if item) or "-"
        evidence = str(record.get("observed_output_reference", "-"))
        lines.append(
            f"| `{record.get('finding_id', '-')}` | `{record.get('attack_case_id', '-')}` | "
            f"**{record.get('status', 'unknown')}** | {record.get('severity', '-')} | {mappings} | `{evidence}` |"
        )
        if record.get("reason"):
            lines.append(f"\nReason: {record['reason']}\n")
    return "\n".join(lines) + "\n"


def write_markdown_report(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(load_records(input_path)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render JSONL attack results as Markdown.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    write_markdown_report(args.input, args.markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
