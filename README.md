# AI Security Projects

Five hands-on projects for building a portfolio that proves — not just claims — the ability to
attack, defend, monitor and govern real AI systems. Based on the 2027 hiring-signal thesis: courses
and certificates are common, demonstrated evidence of attack → control → retest → business
translation is not.

> **Safety note.** Every project runs in an isolated environment, against systems you own, using
> fictional data and planted, fake secrets. Never point these tools or techniques at systems,
> models or accounts you do not control.

## Projects

| # | Project | Focus | OWASP LLM Top 10 | Status |
|---|---------|-------|-------------------|--------|
| 1 | [Automated AI Red-Teaming Lab](01-ai-red-teaming-lab/README.md) | Attack a chatbot with Garak + PyRIT, automate in CI | LLM01, LLM02, LLM07 | In progress — 7/10 tasks complete; next: Task 8 |
| 2 | [Secure RAG Application](02-secure-rag-application/README.md) | Threat-model and attack a retrieval pipeline | LLM01, LLM02, LLM08 | Planned |
| 3 | [Secure AI Agent](03-secure-ai-agent/README.md) | Break and re-architect a tool-using agent | LLM01, LLM06, LLM07 | Planned |
| 4 | [AI Security Monitoring & Detection Lab](04-ai-security-monitoring/README.md) | Detect misuse across the systems above | LLM01, LLM02, LLM06 | Planned |
| 5 | [AI Security & Governance Assurance System](05-ai-governance-assurance/README.md) | Connect findings to risk, controls and evidence | All (via mapping) | Planned |

Each project folder contains its own README with: business scenario, architecture diagram, threat
model, attack methodology, findings format, mitigations, and links to every tool and standard
referenced. Depth over breadth — three of these done thoroughly and documented well outperform all
five done superficially.

Implementation plans are kept in [`docs/superpowers/plans/`](docs/superpowers/plans/).

## Standards and Frameworks Referenced

| Framework | Use | Link |
|---|---|---|
| OWASP Top 10 for LLM Applications | Vulnerability classification for prompts, RAG and outputs | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| OWASP GenAI Security Project — Agentic AI Threats | Agent-specific risks: goal hijacking, tool misuse, memory poisoning | https://genai.owasp.org/ |
| MITRE ATLAS | Adversary tactics/techniques for AI systems | https://atlas.mitre.org/ |
| NIST AI Risk Management Framework (AI RMF 1.0) | Govern / Map / Measure / Manage structure for AI risk | https://www.nist.gov/itl/ai-risk-management-framework |
| NIST Generative AI Profile (NIST AI 600-1) | GenAI-specific risk profile on top of the AI RMF | https://www.nist.gov/itl/ai-risk-management-framework |

## Tools Referenced Across Projects

| Tool | Purpose | Link |
|---|---|---|
| Ollama | Run open-weight LLMs locally for a free, isolated target | https://ollama.com/ |
| Garak | Open-source LLM vulnerability scanner (probes, generators, hit-logs) | https://github.com/NVIDIA/garak |
| PyRIT | Adversarial-prompt orchestration framework (targets, orchestrators, scorers, converters) | https://github.com/Azure/PyRIT |
| Promptfoo | Fast red-team/eval suite for LLM apps | https://www.promptfoo.dev/ |
| LangChain | RAG pipeline components (loaders, retrievers, chains) | https://python.langchain.com/ |
| LlamaIndex | Alternative RAG/indexing framework | https://www.llamaindex.ai/ |
| Chroma | Lightweight local vector database | https://www.trychroma.com/ |
| Elastic / OpenSearch | Ship and search telemetry for the monitoring lab | https://www.elastic.co/ · https://opensearch.org/ |
| GitHub Actions | CI automation for rerunning red-team probes on change | https://docs.github.com/actions |

## How Each Project Is Documented

- Business scenario — who the fictional org is and what the system does
- Architecture — a Mermaid diagram of components and trust boundaries
- Threat model / attack catalogue — what is tested and why
- Methodology — tools, steps, how success/failure is scored
- Findings format — how results map to OWASP LLM Top 10 / MITRE ATLAS
- Mitigations and retest — the control implemented and proof it worked
- Portfolio checklist — what to actually ship (code, report, demo, README)

## Presenting the Work

For each completed project: a concise README, a short recorded demo, and a one-page executive
summary in plain business language. State what was built directly, where AI assisted, and what
still needs human validation.
