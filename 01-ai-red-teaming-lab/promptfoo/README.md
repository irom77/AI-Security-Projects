# Promptfoo fast red-team suite

This suite gives the Northwind chatbot a small CI-sized matrix covering every
stable attack-catalogue category, plus two larger local variants. The provider
calls the target's `POST /chat` endpoint and returns Promptfoo metadata with the
attack ID, target, model, and Promptfoo version.

## Run

From this project directory, start the deterministic target in another shell
and set its base URL:

```bash
export NORTHWIND_CHATBOT_URL=http://127.0.0.1:8000
npx promptfoo@0.123.1 eval -c promptfoo/promptfooconfig.yaml --no-cache
```

Results are written to `results/promptfoo/latest.json`. The vulnerable
baseline is expected to show failures; the controlled target is expected to
pass the blocking assertions after Task 8. Use the local variants when
exploring beyond the CI matrix:

```bash
npx promptfoo@0.123.1 eval -c promptfoo/promptfooconfig.yaml --no-cache --filter-pattern 'local-'
```

Assertions use the stable indicator vocabulary from `attacks/scoring.py` and
accept an explicit refusal for protected cases. They do not compare complete
responses to brittle exact strings.
