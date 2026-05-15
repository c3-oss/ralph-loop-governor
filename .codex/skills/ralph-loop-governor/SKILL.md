---
name: ralph-loop-governor
description: Use when preparing, launching, monitoring, steering, or post-reviewing a Claude Ralph Loop implementation run. Applies when the user wants Codex to generate executor prompts, lane plans, correction queues, evidence templates, reviewer subagent work, gates, or a repeatable mixed Codex/Claude workflow.
---

# Ralph Loop Governor

Use this skill to turn a large implementation request into a governed Ralph Loop: Codex plans, monitors, reviews, writes blocking corrections, and runs final gates; Claude/Ralph does long-running implementation throughput.

This is code review and steering, not passive status tracking. Codex must actively review executor code with focused subagents, convert important findings into blocking corrections, and steer the executor until the lane contract and gates are satisfied.

## User Invocation

Preferred:

```text
$ralph-loop-governor implement <goal>
```

or:

```text
$ralph-loop-governor prepare a Ralph Loop for <feature>
```

Do not require the user to ask for lanes, prompts, status files, correction queues, gates, evidence templates, subagents, or executor commands. Infer and create those artifacts from the feature request. If the request is too vague to produce safe lanes, ask one concise clarifying question.

## Core Contract

- Codex is the architect and gatekeeper; Ralph is the executor.
- Ralph must not be the final judge of its own Done.
- Codex must review code with subagents during the run, not only after Ralph claims completion.
- Codex must steer Ralph through `correction-queue.md`, `ralph-loop-prompt.md`, and gate updates whenever reviewers find blockers.
- Domain-specific skills own product architecture, path ownership, invariants, and validation. Import them into the prompt when applicable.
- Convert fuzzy goals into lane invariants, acceptance criteria, and tests.
- Every blocking finding becomes a correction with an ID, status, owner, and evidence.
- Final completion requires gates and evidence, not just a clean worktree.

## Setup Workflow

1. Read repository instructions and any matched domain skills or architecture docs before creating the executor prompt.
2. Create or update the feature workspace:

```text
docs/roadmap/<feature>/
  ralph-loop-prompt.md
  status.md
  correction-queue.md
  gates.md
  evidence/
    lane-01.md
    lane-02.md
```

3. Generate a kickoff prompt from `assets/ralph-loop-prompt-template.md`.
4. State that Claude Code must have the Anthropic-verified Ralph Loop plugin installed: https://claude.com/plugins/ralph-loop.
5. Give the user an exact Claude command:

```text
/ralph-loop:ralph-loop "@docs/roadmap/<feature>/ralph-loop-prompt.md" --max-iterations 30 --completion-promise RALPH_DONE
```

If the user's Claude Code exposes the plugin command as `/ralph-loop`, tell them to use that command name with the same prompt and flags.

6. If restarting Ralph to consume corrections, use a quoted prompt:

```text
/ralph-loop:ralph-loop "Read @docs/roadmap/<feature>/ralph-loop-prompt.md, @docs/roadmap/<feature>/correction-queue.md, and @docs/roadmap/<feature>/gates.md. Close every blocking correction with evidence, wait 5 minutes, reread the correction queue, and repeat until no blocking correction remains open." --max-iterations 20 --completion-promise RALPH_DONE
```

## Monitoring Workflow

- Write the monitor outside the target repo unless the user asks otherwise, for example `~/workspace/<repo>-<feature>-ralph-loop-monitor.md`.
- When the user reports "Ralph started", "Loop started", or equivalent, enter the active monitor loop immediately.
- Use a 5-minute interval by default unless the user requested a different interval. The interval is a real idle wait: stop monitoring work, run no intermediate checks, send no progress updates, and do no parallel review or implementation work until the wait expires.
- Each check records timestamp, `git status --short --branch`, recent commits, changed areas, lane evidence/status, correction queue, gates, `RALPH_DONE` signal, open blockers, and no-change streak.
- After material implementation changes or completed lanes, spawn focused read-only reviewer subagents for changed domains.
- If Ralph is making progress, do not edit implementation files.
- If reviewer findings or Codex review reveal blockers, immediately add or update entries in `correction-queue.md` with concrete acceptance criteria and update `ralph-loop-prompt.md` when the executor needs stronger steering.
- Keep treating Ralph as active until `RALPH_DONE` is detected, the user stops the run, or three configured idle checks show no implementation changes and final gates begin.

## Reviewer Subagents

Reviewer subagents are mandatory for substantial Ralph output. Use disjoint reviewer scopes as soon as material code lands, at lane boundaries, and before final gates:

- `ralph-loop-security-reviewer`: auth, authorization, tenant or account isolation, unsafe config, exposed secrets, dangerous endpoints.
- `ralph-loop-data-integrity-reviewer`: data movement, persistence, idempotency, transactions, destructive cleanup, replay safety.
- `ralph-loop-read-surface-reviewer`: user-visible read surfaces, API/CLI/UI parity, output formats, fail-closed behavior.
- `ralph-loop-e2e-gate-runner`: end-to-end gates, external service setup, reproducibility evidence, skipped gates.
- `ralph-loop-refactor-integrator`: post-hardening code shape and maintainability with explicit write scope.

Default reviewer mode is read-only. Assign write scopes only after Ralph has stopped or when the user explicitly wants Codex to intervene.

Reviewer findings are not advisory notes to remember later. Every finding that can break product behavior, security, data integrity, parity, or release gates must become a `CQ-*` correction before the next Ralph restart or final review.

## Correction Queue Rules

Use `assets/correction-queue-template.md` for formatting.

Every blocking correction needs:

- stable ID such as `CQ-001`;
- severity and blocking flag;
- concrete file paths or commands where known;
- product, security, data, or release risk;
- required fix;
- acceptance criteria;
- evidence field with commits and tests.

Do not close a correction because an agent claims it is fixed. Close it only when code, tests, and evidence support the claim.

## Evidence And Gates

Use `assets/lane-evidence-template.md` and `assets/gates-template.md`.

Start with repository-local commands discovered from guidance, package manifests, task runners, CI, and existing scripts. Common gate categories:

- dependency install or environment setup;
- build;
- typecheck or static analysis;
- unit/integration tests;
- lint or formatting check;
- security/dependency audit;
- end-to-end tests;
- whitespace diff check.

Classify any skipped or failed gate as blocking, acceptable with reason, or follow-up risk.

## Architect Intervention

If Ralph stops with critical blockers:

- label direct Codex fixes as `Architect intervention`;
- keep patches scoped by subsystem;
- rerun focused tests and the final gate;
- separate "Ralph delivered" from "Codex repaired" in the final report.
