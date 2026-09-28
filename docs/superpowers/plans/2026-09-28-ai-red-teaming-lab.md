# Automated AI Red-Teaming Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repeatable local AI red-teaming lab for the Northwind Retail support chatbot, showing automated attacks, evidence-backed findings, mitigations, and retests in CI.

**Architecture:** Implement a small Python HTTP chatbot service with a swappable Ollama/API model adapter and a deterministic fake-model mode for tests and CI. Keep attack runners independent from the app: Promptfoo provides fast assertions, Garak scans the exposed endpoint through a documented adapter, and PyRIT runs a prompt matrix with converters and scorers. Store normalized run metadata and raw tool output under `results/`, then use the same attack cases before and after controls.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, httpx, pytest, Ollama, Garak, PyRIT, Promptfoo, Node.js for Promptfoo, GitHub Actions, Markdown/JSONL.

**Spec:** `01-ai-red-teaming-lab/README.md`

## Global Constraints

- Run every project in an isolated environment against systems the project owner controls, using fictional data and planted fake secrets.
- The chatbot must have an explicit purpose, prohibited behavior, and sensitive-data boundary.
- The planted secret is a dummy internal API key and must never be a real credential.
- The initial attack scope includes direct prompt injection, jailbreaks, system-prompt extraction, fake-secret disclosure, encoding evasion, and unsafe/unfiltered output.
- Every attempt records pass/fail and why the control failed; raw evidence is retained.
- Findings map to OWASP LLM01, LLM02, and LLM07 and relevant MITRE ATLAS techniques.
- Every successful attack gets a control, a retest with the same probe, and a recorded residual risk.
- CI reruns a bounded probe subset when the model, system prompt, or guardrails change.

## Review Focus

- Model/API unavailable or slow: the lab must fail with an actionable diagnostic and support deterministic CI mode rather than silently passing.
- Secret appears in a refusal, transformed output, or partial/letter-by-letter response: secret-detection assertions must catch exact and normalized variants.
- Tool output formats change or contain no hits: parsers must preserve raw artifacts and report an explicit unknown/error state.
- Attack success is a refusal containing attack keywords: scorers must distinguish genuine disclosure from refusal text.
- A mitigation blocks one literal probe but misses an equivalent encoding or role-play variant: retests must use a stable matrix, not one hard-coded prompt.

---

### Task 1: Establish the Python project and safety boundary

**Status:** Complete — configuration scaffold and safety validation implemented.

**Files:**
- Create: `01-ai-red-teaming-lab/app/__init__.py`
- Create: `01-ai-red-teaming-lab/app/config.py`
- Create: `01-ai-red-teaming-lab/pyproject.toml`
- Create: `01-ai-red-teaming-lab/.env.example`
- Create: `01-ai-red-teaming-lab/.gitignore`
- Create: `01-ai-red-teaming-lab/tests/test_config.py`

**Interfaces:**
- Produces `Settings` with `model_name`, `model_backend`, `ollama_base_url`, `fake_secret`, `enable_guardrails`, and `request_timeout_seconds`.
- Rejects non-placeholder secrets and real-looking credential values in checked-in configuration.

- [x] **Step 1: Write failing configuration tests**

  Add tests for default local settings, environment overrides, and rejection of an empty or non-placeholder `fake_secret`.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_config.py -q`

  Expected: FAIL because the settings module does not exist.

- [x] **Step 3: Implement typed settings and project metadata**

  Use a typed settings object with safe defaults (`ollama`, local URL, deterministic fake secret such as `NW-DUMMY-KEY-...`). Do not load secrets from source control or log environment values.

- [x] **Step 4: Run tests to verify they pass**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_config.py -q`

  Expected: PASS.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/app 01-ai-red-teaming-lab/pyproject.toml 01-ai-red-teaming-lab/.env.example 01-ai-red-teaming-lab/.gitignore 01-ai-red-teaming-lab/tests/test_config.py
  git commit -m "chore: scaffold red teaming lab"
  ```

### Task 2: Build the intentionally vulnerable chatbot target

**Files:**
- Create: `01-ai-red-teaming-lab/app/prompts.py`
- Create: `01-ai-red-teaming-lab/app/model_client.py`
- Create: `01-ai-red-teaming-lab/app/chatbot.py`
- Create: `01-ai-red-teaming-lab/app/main.py`
- Create: `01-ai-red-teaming-lab/tests/test_chatbot_api.py`
- Create: `01-ai-red-teaming-lab/tests/test_model_client.py`

**Interfaces:**
- `build_system_prompt(settings: Settings) -> str` includes the fictional Northwind purpose, prohibited behavior, sensitive-data boundary, and fake secret in vulnerable mode.
- `ModelClient.generate(system_prompt: str, user_prompt: str) -> ModelResponse`.
- `Chatbot.respond(request: ChatRequest) -> ChatResponse`.
- `POST /chat` accepts `{ "message": string, "session_id": string | null }` and returns response text, model metadata, and a run correlation ID.
- `GET /health` returns backend availability and configuration status without exposing the secret or system prompt.

**Status:** Complete — chatbot target, fake/Ollama model seam, API contract, and safety-focused diagnostics implemented.

- [x] **Step 1: Write failing target behavior tests**

  Test the API contract, health response, explicit system-prompt contents, fake-model deterministic responses, and that normal customer-support questions do not disclose the secret.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_chatbot_api.py tests/test_model_client.py -q`

  Expected: FAIL because the target service does not exist.

- [x] **Step 3: Implement the target and model seam**

  Keep the intentionally vulnerable behavior limited to the lab target. The fake client should return scripted responses for normal questions and attack categories; the Ollama client should make one local request with timeout handling. Do not expose raw system prompts through diagnostics.

- [x] **Step 4: Run tests to verify they pass**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_chatbot_api.py tests/test_model_client.py -q`

  Expected: PASS.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/app 01-ai-red-teaming-lab/tests
  git commit -m "feat: add Northwind chatbot red team target"
  ```

### Task 3: Define the attack corpus, scoring contract, and findings schema

**Files:**
- Create: `01-ai-red-teaming-lab/attacks/cases.yaml`
- Create: `01-ai-red-teaming-lab/attacks/scoring.py`
- Create: `01-ai-red-teaming-lab/results/.gitkeep`
- Create: `01-ai-red-teaming-lab/tests/test_scoring.py`
- Create: `01-ai-red-teaming-lab/tests/test_attack_corpus.py`

**Interfaces:**
- `AttackCase(id, category, prompt, expected_behavior, owasp_category, atlas_techniques, severity) -> dataclass`.
- `score_response(case: AttackCase, response: str, fake_secret: str) -> Score` where `Score` contains `status`, `reason`, `matched_indicators`, and `confidence`.
- `FindingRecord` JSON schema contains finding ID, attack case ID, tool, timestamp, target/model, observed output reference, control, retest status, residual risk, OWASP mapping, and MITRE ATLAS mapping.

**Status:** Complete — stable attack corpus, conservative scorer, encoded-secret detection, and findings schema implemented.

- [x] **Step 1: Write failing corpus and scoring tests**

  Cover direct injection, jailbreak/persona, prompt extraction, fake-secret disclosure, base64/ROT13/letter-by-letter evasion, and unsafe output. Assert that a refusal is not scored as a leak and that exact, normalized, and encoded secret forms are detected.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_scoring.py tests/test_attack_corpus.py -q`

  Expected: FAIL because the schema and corpus are absent.

- [x] **Step 3: Implement the stable corpus and scorer**

  Keep prompt IDs stable across vulnerable and controlled runs. Normalize case, whitespace, separators, and common encodings only for detection; retain the original response for evidence. Mark ambiguous responses as `review_required`, never as a pass.

- [x] **Step 4: Run tests to verify they pass**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_scoring.py tests/test_attack_corpus.py -q`

  Expected: PASS.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/attacks 01-ai-red-teaming-lab/results/.gitkeep 01-ai-red-teaming-lab/tests
  git commit -m "feat: define red team attack corpus and scoring"
  ```

### Task 4: Add a repeatable local runner and normalized evidence output

**Files:**
- Create: `01-ai-red-teaming-lab/tools/run_attacks.py`
- Create: `01-ai-red-teaming-lab/tools/report_results.py`
- Create: `01-ai-red-teaming-lab/tests/test_run_attacks.py`
- Create: `01-ai-red-teaming-lab/tests/fixtures/fake_target_responses.json`

**Interfaces:**
- `run_attack_cases(base_url: str, cases: list[AttackCase], run_id: str, tool: str) -> list[FindingRecord]`.
- CLI: `python -m tools.run_attacks --base-url ... --mode vulnerable|controlled --output results/<run>.jsonl`.
- CLI: `python -m tools.report_results results/<run>.jsonl --markdown results/<run>.md`.

**Status:** Complete — deterministic HTTP runner, raw evidence capture, JSONL output, Markdown reporting, and error-path handling implemented.

- [x] **Step 1: Write failing runner tests**

  Use an HTTP fixture to assert one record per case, correlation IDs, preserved raw response references, deterministic ordering, timeout/error records, and nonzero exit status when a configured blocking finding occurs.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_run_attacks.py -q`

  Expected: FAIL because the runner does not exist.

- [x] **Step 3: Implement the runner and report formatter**

  Write JSONL as the machine-readable source of truth, put raw response bodies in a run-specific evidence directory, and generate a concise Markdown summary linking each finding to evidence and mappings. Avoid putting the fake secret in filenames or summary text unless the finding evidence explicitly requires it.

- [x] **Step 4: Run tests and a local fake-target smoke test**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_run_attacks.py -q`

  Expected: PASS, including error-path tests.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/tools 01-ai-red-teaming-lab/tests
  git commit -m "feat: add normalized attack evidence runner"
  ```

### Task 5: Integrate Promptfoo for fast red-team coverage

**Status:** Complete — Promptfoo provider, catalogue matrix, stable assertions, versioned JSON output, and local filtering implemented and verified.

**Files:**
- Create: `01-ai-red-teaming-lab/promptfoo/promptfooconfig.yaml`
- Create: `01-ai-red-teaming-lab/promptfoo/prompts.yaml`
- Create: `01-ai-red-teaming-lab/promptfoo/provider.py`
- Create: `01-ai-red-teaming-lab/promptfoo/README.md`
- Create: `01-ai-red-teaming-lab/tests/test_promptfoo_config.py`

**Interfaces:**
- Provider forwards each Promptfoo prompt to `POST /chat` and returns response text plus metadata.
- Promptfoo assertions fail on fake-secret disclosure, system-prompt disclosure, or unsafe output indicators and record refusal as an acceptable result for protected cases.

- [x] **Step 1: Write configuration validation tests**

  Assert all attack IDs are represented, the provider URL is environment-configurable, and assertions reference the stable scoring rules rather than brittle exact response text.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_promptfoo_config.py -q`

  Expected: FAIL until the Promptfoo files exist.

- [x] **Step 3: Implement the fast suite**

  Include a small, CI-sized matrix covering all catalogue categories, with a larger local matrix available through a command-line filter. Configure JSON output under `results/promptfoo/` and preserve the Promptfoo version in the run metadata.

- [x] **Step 4: Run the suite against deterministic mode**

  Run: `cd 01-ai-red-teaming-lab && npx promptfoo eval -c promptfoo/promptfooconfig.yaml --no-cache`

  Expected: the vulnerable baseline demonstrates expected failures; controlled mode passes the blocking assertions after Task 8.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/promptfoo 01-ai-red-teaming-lab/tests
  git commit -m "feat: add Promptfoo red team suite"
  ```

### Task 6: Integrate Garak against the chatbot endpoint

**Status:** Complete — Garak-compatible HTTP adapter, bounded probe runner, pinned manifest, and evidence documentation implemented and verified.

**Files:**
- Create: `01-ai-red-teaming-lab/garak/generator.py`
- Create: `01-ai-red-teaming-lab/garak/run_garak.sh`
- Create: `01-ai-red-teaming-lab/garak/README.md`
- Create: `01-ai-red-teaming-lab/tests/test_garak_adapter.py`

**Interfaces:**
- `NorthwindGenerator` implements the Garak generator contract and sends prompts to the target endpoint with run metadata.
- `garak/run_garak.sh` lists available probes, runs prompt-injection and encoding families first, writes hit-log output to `results/garak/`, and accepts `TARGET_URL`, `GARAK_PROBES`, and `RESULTS_DIR` overrides.

- [x] **Step 1: Write adapter tests**

  Test prompt forwarding, target URL configuration, timeout propagation, and preservation of Garak-compatible response metadata without requiring a live Ollama model.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_garak_adapter.py -q`

  Expected: FAIL because the adapter is absent.

- [x] **Step 3: Implement the generator and controlled probe script**

  Pin the Garak invocation in the README, make probe selection explicit, and capture the exact command plus tool version in an adjacent manifest. Keep broad probe expansion opt-in so CI remains bounded.

- [x] **Step 4: Run adapter tests and a probe-list smoke check**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_garak_adapter.py -q && bash garak/run_garak.sh --list-probes`

  Expected: adapter tests pass and the script prints available probes or an actionable install message.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/garak
  git commit -m "feat: integrate Garak endpoint generator"
  ```

### Task 7: Add PyRIT prompt orchestration, converters, and scorers

**Status:** Complete — local PyRIT-shaped target, converter lineage, shared scorer integration,
CLI JSONL outputs, and component tests implemented and verified.

**Files:**
- Create: `01-ai-red-teaming-lab/pyrit/target.py`
- Create: `01-ai-red-teaming-lab/pyrit/orchestrator.py`
- Create: `01-ai-red-teaming-lab/pyrit/scorers.py`
- Create: `01-ai-red-teaming-lab/pyrit/run_pyrit.py`
- Create: `01-ai-red-teaming-lab/pyrit/README.md`
- Create: `01-ai-red-teaming-lab/tests/test_pyrit_components.py`

**Interfaces:**
- `NorthwindPyRITTarget.send(prompt: str) -> str`.
- `build_attack_orchestrator(target, cases, converters, scorers) -> Orchestrator`.
- `score_pyrit_response(case, response, fake_secret) -> Score` using the shared scoring contract.
- CLI writes raw PyRIT output and normalized `FindingRecord` JSONL under `results/pyrit/`.

- [x] **Step 1: Write component tests**

  Test target forwarding, encoding converters, scorer behavior for refusal versus disclosure, and matrix coverage across all stable case IDs using a fake target.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_pyrit_components.py -q`

  Expected: FAIL because the PyRIT integration is absent.

- [x] **Step 3: Implement the PyRIT integration**

  Keep PyRIT-specific APIs behind these local interfaces so dependency upgrades do not change the attack corpus or report schema. Use base64, ROT13, and letter-by-letter converters explicitly and preserve converter lineage in each result.

- [x] **Step 4: Run component tests**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_pyrit_components.py -q`

  Expected: PASS.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/pyrit 01-ai-red-teaming-lab/tests
  git commit -m "feat: add PyRIT adversarial prompt matrix"
  ```

### Task 8: Implement controls and prove the mitigation→retest loop

**Files:**
- Modify: `01-ai-red-teaming-lab/app/prompts.py`
- Create: `01-ai-red-teaming-lab/app/guardrails.py`
- Modify: `01-ai-red-teaming-lab/app/chatbot.py`
- Create: `01-ai-red-teaming-lab/tests/test_guardrails.py`
- Create: `01-ai-red-teaming-lab/results/baseline/.gitkeep`
- Create: `01-ai-red-teaming-lab/results/retest/.gitkeep`
- Create: `01-ai-red-teaming-lab/docs/controls.md`

**Interfaces:**
- `check_input(message: str) -> GuardrailDecision`.
- `check_output(response: str, fake_secret: str) -> GuardrailDecision`.
- `build_system_prompt(settings)` supports vulnerable and controlled modes, with secret removal from the controlled prompt.
- `run_attacks.py` accepts `--mode` and produces comparable baseline/retest records.

- [x] **Step 1: Write failing control tests**

  Assert controlled mode rejects or safely routes direct injection, encoded requests, role-play jailbreaks, prompt-extraction attempts, and secret-bearing output; assert normal support questions remain usable. Verify the controlled system prompt contains no fake secret.

- [x] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_guardrails.py -q`

  Expected: FAIL because controls are not implemented.

- [x] **Step 3: Implement layered controls**

  Add input classification, system-prompt hardening, removal of secrets from the controlled prompt, and output secret/unsafe-content filtering. Treat filters as defense-in-depth; do not claim that keyword matching proves general jailbreak resistance.

- [x] **Step 4: Run the same corpus before and after controls**

  Run baseline and controlled runs with identical case IDs, then generate a comparison report showing vulnerable result, control, retest result, and residual risk for every finding.

  Expected: known deterministic disclosures are blocked in controlled mode; any remaining or ambiguous cases are explicitly recorded for review.

- [x] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/app 01-ai-red-teaming-lab/tests 01-ai-red-teaming-lab/docs 01-ai-red-teaming-lab/results
  git commit -m "feat: add red team controls and retest evidence"
  ```

**Status:** Complete — layered controls, controlled prompt hardening, mode-tagged comparable
baseline/retest evidence, and documented residual risk implemented and verified. The deterministic
baseline ran 8 cases with 2 failures and 6 review-required results; the identical controlled retest
ran all 8 cases as passes with matching case IDs.

### Task 9: Add CI automation and reproducible run metadata

**Files:**
- Create: `.github/workflows/red-team-lab.yml`
- Create: `01-ai-red-teaming-lab/tools/collect_run_metadata.py`
- Create: `01-ai-red-teaming-lab/tests/test_ci_contract.py`
- Modify: `01-ai-red-teaming-lab/README.md`

**Interfaces:**
- CI triggers on changes to `01-ai-red-teaming-lab/**`, its workflow, and relevant model/system-prompt/guardrail files.
- CI starts deterministic target mode, runs unit tests, Promptfoo, the bounded normalized runner, and optional Garak/PyRIT jobs when their dependencies are available.
- CI uploads `results/` as artifacts and fails on blocking controlled-mode findings.

- [ ] **Step 1: Write CI contract tests**

  Parse the workflow and assert path filters, Python/Node setup, test command, deterministic target startup, artifact upload, and blocking-result handling.

- [ ] **Step 2: Run tests to verify they fail**

  Run: `cd 01-ai-red-teaming-lab && pytest tests/test_ci_contract.py -q`

  Expected: FAIL because the workflow and metadata tool are absent.

- [ ] **Step 3: Implement workflow and metadata collection**

  Record commit SHA, target mode, model/backend, tool versions, case-corpus hash, timestamp, and command lines. Keep live Ollama jobs separate from deterministic required checks so CI is reliable and reproducible.

- [ ] **Step 4: Validate locally**

  Run: `cd 01-ai-red-teaming-lab && pytest -q`

  Expected: PASS, with the workflow contract test confirming the CI surface.

- [ ] **Step 5: Commit**

  ```bash
  git add .github/workflows/red-team-lab.yml 01-ai-red-teaming-lab/tools 01-ai-red-teaming-lab/tests 01-ai-red-teaming-lab/README.md
  git commit -m "ci: automate red team regression checks"
  ```

### Task 10: Write the assessment, executive summary, and demo instructions

**Files:**
- Create: `01-ai-red-teaming-lab/report/assessment.md`
- Create: `01-ai-red-teaming-lab/report/executive-summary.md`
- Create: `01-ai-red-teaming-lab/report/demo-script.md`
- Modify: `01-ai-red-teaming-lab/README.md`
- Create: `01-ai-red-teaming-lab/results/sample/.gitkeep`

**Interfaces:**
- The assessment references concrete result filenames and contains scope, methodology, attack evidence, why each control failed, risk rating, affected asset, OWASP mapping, MITRE ATLAS mapping, mitigation, retest result, and residual risk.
- The executive summary is one page and written for a business audience.
- The demo script runs the target, shows one baseline attack, shows the control, reruns the identical case, and points to CI artifacts without exposing real credentials.

- [ ] **Step 1: Add report validation checks**

  Add a lightweight test or script that verifies every finding ID in the normalized results appears in the assessment and that all three OWASP categories plus MITRE ATLAS mappings are represented.

- [ ] **Step 2: Generate sample artifacts from deterministic mode**

  Run baseline, tool-specific, controlled, and retest commands; save only sanitized, reviewable outputs under `results/`.

- [ ] **Step 3: Write the three portfolio documents**

  Use evidence links rather than unsupported claims, disclose deterministic-versus-live-model limitations, and identify what still requires human validation.

- [ ] **Step 4: Update the README checklist and run the full verification**

  Run: `cd 01-ai-red-teaming-lab && pytest -q`

  Then execute the documented local demo command sequence and verify the generated artifacts are readable from a clean checkout.

- [ ] **Step 5: Commit**

  ```bash
  git add 01-ai-red-teaming-lab/report 01-ai-red-teaming-lab/results 01-ai-red-teaming-lab/README.md
  git commit -m "docs: publish red teaming assessment and demo"
  ```

## Final Verification

- [ ] Start the deterministic target and confirm `/health` does not disclose the system prompt or fake secret.
- [ ] Run the complete unit test suite: `cd 01-ai-red-teaming-lab && pytest -q`.
- [ ] Run the fast Promptfoo suite and normalized attack runner against vulnerable mode; confirm expected findings and evidence files.
- [ ] Run controlled mode with the exact same case IDs; confirm blocked disclosures and explicit residual-risk records.
- [ ] Run Garak’s probe listing plus the bounded prompt-injection and encoding families when installed.
- [ ] Run the PyRIT matrix with deterministic target mode and confirm converter/scorer lineage in output.
- [ ] Validate that CI path filters, artifacts, and blocking conditions work from a clean checkout.
- [ ] Review the assessment, one-page summary, and demo against the README portfolio checklist.
