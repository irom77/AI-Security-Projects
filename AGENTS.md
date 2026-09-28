# Repository guidance

This repository is a portfolio of hands-on AI security projects. Treat the root
[`README.md`](README.md) as the canonical contract for how projects are documented and presented.
Keep project documentation aligned with its sections, vocabulary, safety note, and portfolio
standard.

## Documentation contract

Every project must have an up-to-date `<project>/README.md` that covers:

- business scenario and system purpose
- Mermaid architecture diagram with components and trust boundaries
- threat model or attack catalogue
- attack and evaluation methodology, including success/failure scoring
- findings format mapped to relevant OWASP LLM Top 10 and MITRE ATLAS categories
- mitigations and retest evidence
- portfolio checklist covering code, results, CI, report, demo, and executive summary
- links to every tool and standard referenced

Present completed work as the root README requires: a concise project README, a short recorded
demo, and a one-page executive summary in plain business language. State what was built directly,
where AI assisted, and what still needs human validation. Use fictional data, planted fake secrets,
and isolated systems only.

Keep both the root README and the affected project README current whenever scope, architecture,
status, deliverables, or implementation evidence changes. Update links, checklists, and status
labels in the same change that makes the underlying change.

## Plans and implementation

Create implementation plans under `docs/`, normally at:

```text
docs/superpowers/plans/YYYY-MM-DD-<project-slug>.md
```

Before implementation, write the plan with ordered tasks, affected files, interfaces, tests,
verification commands, and a clear completion criterion for every task. Link the plan from both
the root README and the affected project README.

Implement one task at a time. For each task:

1. Mark the task in progress in the plan and read the relevant repository context.
2. Write or update failing tests before implementation when behavior is changing.
3. Implement only the current task and preserve unrelated working-tree changes.
4. Run focused verification, then the project’s full test suite.
5. Review the diff, tests, documentation impact, safety boundaries, and plan completion criteria.
6. Present the completed task for review and pause for approval before committing or pushing it.
7. After approval, mark every completed step and the task status in the plan, commit the task as
   an atomic change, and push the commit.

Do not silently batch tasks. A task is complete only when its plan status, implementation, tests,
documentation, review, commit, and push are all current. Record verification results in the plan
or its associated execution ledger when one exists.

## Git and review rules

- Implement planned work directly on the `main` branch unless the user explicitly requests a
  different branch or isolated worktree.
- Keep commits scoped to one completed plan task or one explicitly requested documentation change.
- Do not include unrelated user changes in a commit; inspect `git status` and the diff first.
- Review every task before commit and push, checking both the implementation and the documentation
  contract above.
- Prefer reversible, explicit commands and never discard user work without confirmation.
- After committing and pushing, report the commit, verification result, and any remaining
  uncommitted files before moving to the next task.
