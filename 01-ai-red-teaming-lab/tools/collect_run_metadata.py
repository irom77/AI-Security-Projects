"""Write reproducibility metadata for a red-team run."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tool_versions() -> dict[str, str]:
    versions = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    for executable in ("promptfoo", "garak", "pyrit"):
        try:
            result = subprocess.run(
                [executable, "--version"], capture_output=True, text=True, check=False
            )
        except OSError:
            continue
        version = (result.stdout or result.stderr).strip()
        if version:
            versions[executable] = version
    return versions


def collect_metadata(
    *,
    mode: str,
    model: str,
    backend: str,
    case_file: Path,
    commands: list[str],
) -> dict[str, object]:
    return {
        "commit_sha": _git_commit(),
        "target_mode": mode,
        "model": model,
        "backend": backend,
        "tool_versions": _tool_versions(),
        "case_corpus": str(case_file),
        "case_corpus_sha256": _sha256(case_file),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commands": commands,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("vulnerable", "controlled"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--case-file", type=Path, default=Path("attacks/cases.yaml"))
    parser.add_argument("--command", action="append", dest="commands", default=[])
    args = parser.parse_args(argv)

    metadata = collect_metadata(
        mode=args.mode,
        model=args.model,
        backend=args.backend,
        case_file=args.case_file,
        commands=args.commands,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
