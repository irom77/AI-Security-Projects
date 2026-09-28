# PyRIT integration

This adapter keeps PyRIT-specific orchestration behind local interfaces so the stable Northwind
attack corpus and `FindingRecord` schema survive dependency upgrades. The target forwards prompts
to `POST /chat`; the bounded matrix runs identity, base64, ROT13, and letter-by-letter variants.

PyRIT is optional for this repository's deterministic tests. The local adapter is runnable without
the package and is suitable for controlled demonstrations against the fictional target.

From `01-ai-red-teaming-lab/`, run:

```bash
python -m pyrit.run_pyrit --base-url http://127.0.0.1:8000
```

Raw PyRIT-shaped results are written to `results/pyrit/raw.jsonl`; normalized findings are written
to `results/pyrit/findings.jsonl`. A nonzero exit status means at least one response matched the
shared failure scorer. Do not use real secrets or targets outside the lab owner's control.
