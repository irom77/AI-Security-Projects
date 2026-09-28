# Controls and retest evidence

The lab uses layered controls as defense-in-depth:

1. `check_input` blocks a small, explainable catalogue of known injection, extraction,
   encoding-evasion, role-play, and unsafe-request shapes.
2. Controlled mode hardens the system prompt and removes the fake secret from it entirely.
3. `check_output` blocks the planted secret and clearly unsafe instruction markers before a
   response leaves the application.

These filters are intentionally narrow. A passing result demonstrates that the deterministic
cases were blocked; it does not prove general jailbreak resistance. New equivalent variants and
human review remain required.

## Reproduce baseline and retest

Start the target twice, using the same commit and attack corpus:

```bash
cd 01-ai-red-teaming-lab
MODEL_BACKEND=fake ENABLE_GUARDRAILS=false .venv/bin/uvicorn app.main:app --port 8000
.venv/bin/python -m tools.run_attacks --base-url http://127.0.0.1:8000 \
  --mode vulnerable --case-file attacks/cases.yaml --output results/baseline/run.jsonl
```

Then restart it with `ENABLE_GUARDRAILS=true` and run the identical command with
`--mode controlled` and `results/retest/run.jsonl`. Every record includes the stable case ID and
the mode, making the two JSONL files directly comparable.

| Finding class | Baseline | Controlled retest | Residual risk |
|---|---|---|---|
| Known deterministic secret disclosure | Expected fail | Expected pass | New variants require review |
| Known injection/extraction shapes | Expected fail or review | Expected pass | Keyword bypass and semantic jailbreaks |
| Normal support question | Expected pass | Expected pass | Model quality still requires validation |

Keep generated JSONL and raw evidence under `results/`; the repository stores directory markers,
not live-model output or credentials.
