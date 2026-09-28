# Executive Summary

The Northwind Retail chatbot red-team exercise found that an intentionally vulnerable
configuration could expose a planted internal value and system-prompt content when attackers
used direct instruction override and prompt-extraction requests. Six additional attack paths were
ambiguous in the deterministic baseline and therefore require human review rather than being
classified as safe.

The exercise covered prompt injection, jailbreak framing, system-prompt extraction, sensitive
information disclosure, encoding evasion, and unsafe output. Findings are mapped to OWASP LLM01,
LLM02, and LLM07 and to MITRE ATLAS AML.T0051 and AML.T0056. Evidence is available in the
versioned baseline and retest JSONL files and in the linked per-case response artifacts.

After input/output controls and controlled prompt behavior were enabled, the identical eight-case
corpus passed in the retest. This is a positive regression signal for the fictional deterministic
target, not a production security certification. The test uses a fake backend and a dummy value;
live-model quality, adversarial creativity, multi-turn behavior, and operational impact remain
unvalidated.

Business recommendation: keep the CI regression gate, remove secrets from model prompts, expand
the attack corpus, and require a human review step for ambiguous or live-model findings before
release. The demo can be run locally without credentials using the instructions in
[demo-script.md](demo-script.md).
