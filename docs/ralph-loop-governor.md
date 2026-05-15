# Ralph Loop Governor

This document defines a repeatable workflow for using Claude Ralph Loop as a long-running implementation engine while Codex acts as architect, reviewer, correction writer, and final gatekeeper.

## Start From Codex

In Codex:

```text
$ralph-loop-governor implement <feature goal>
```

Codex should infer lanes, prompt, status file, correction queue, gates, evidence templates, reviewer subagents, and the Claude command from that request. Use a longer prompt only when you need to override defaults such as monitor interval, required domain docs, or gate commands.

## Prerequisites

Claude Code must have the Anthropic-verified [Ralph Loop plugin](https://claude.com/plugins/ralph-loop) installed before running the executor. The plugin provides the iterative loop command that keeps re-running Claude until the completion promise is emitted or the iteration limit is reached.

## Run In Claude

Initial kickoff:

```text
/ralph-loop:ralph-loop "@docs/roadmap/<feature>/ralph-loop-prompt.md" --max-iterations 30 --completion-promise RALPH_DONE
```

If your Claude Code installation exposes the plugin command as `/ralph-loop`, use that command name with the same prompt and flags.

Correction restart:

```text
/ralph-loop:ralph-loop "Read @docs/roadmap/<feature>/ralph-loop-prompt.md, @docs/roadmap/<feature>/correction-queue.md, and @docs/roadmap/<feature>/gates.md. Close every blocking correction with code, tests, and evidence. If no blocking correction remains, run the mandatory final stabilization wait: five clean cycles of sleep 180 seconds, then reread correction queue, gates, status, git status, and recent commits. Any change, open blocker, failed gate, stale evidence, new commit, or unexplained dirty worktree resets the five-cycle count to zero. Output RALPH_DONE only after all five cycles stay clean." --max-iterations 20 --completion-promise RALPH_DONE
```

Keep natural-language prompts quoted.

## Codex Monitor Loop

Codex should write a monitor file outside the repo unless the user asks otherwise:

```text
~/workspace/<repo>-<feature>-ralph-loop-monitor.md
```

When the user reports "Ralph started", "Loop started", or equivalent, Codex must enter the active monitor loop immediately. Use a 5-minute interval by default unless the user requested another interval. The interval is a real idle wait: Codex stops all monitoring work, runs no intermediate checks, sends no progress updates, and does no parallel review or implementation work until the wait expires.

Each cycle:

1. Idle for the configured interval.
2. Record timestamp, `git status --short --branch`, recent commits, changed areas, lane evidence/status, correction queue, gates, `RALPH_DONE` signal, open blockers, and no-change streak.
3. Update `status.md`, `correction-queue.md`, and gate/evidence artifacts as needed.
4. Compare implementation against lanes, correction queue, and product invariants.
5. Spawn read-only reviewers for changed domains.
6. Add or update blocking corrections for every reviewer finding that can break product behavior, security, data integrity, parity, or release gates.
7. Reset the no-change streak on implementation changes.

Keep treating Ralph as active until `RALPH_DONE` is detected, the user stops the run, or three configured idle checks show no implementation change and final gates begin.

## Final Stabilization Wait

Ralph must not emit `RALPH_DONE` immediately after it believes the work is complete. The executor can make a change, believe the run is complete, and then miss stale evidence, gate drift, or newly written governor corrections.

When Ralph believes there are no open blocking corrections:

1. Commit or explicitly document all WIP. Do not begin stabilization with an unexplained dirty worktree.
2. Run and record the required focused gates for the run.
3. Start a clean-cycle counter at zero.
4. Repeat until the counter reaches five:
   - sleep exactly 180 seconds;
   - reread `correction-queue.md`, `gates.md`, `status.md`, `git status --short --branch`, and recent commits;
   - if there is any open blocker, dirty or unexplained worktree state, new commit, failed gate, stale evidence, or contradictory status, fix it and reset the counter to zero;
   - if everything is still clean and consistent, increment the counter by one.
5. Only after five consecutive clean cycles, which is at least 15 minutes, may Ralph emit `<promise>RALPH_DONE</promise>`.

Codex must reject `RALPH_DONE` if this five-cycle stabilization evidence is missing, shorter than 15 minutes, or reset conditions were ignored.

## Files For Each Feature

Use this structure:

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

If the feature is already described by a durable architecture reference, keep that reference in the repo's normal documentation area and use the roadmap directory only for the active implementation plan, correction queue, and evidence.

## Reviewer Lanes

Use subagents with disjoint scopes. This is required for substantial output, especially at lane boundaries and before final gates:

| Agent | Scope |
| --- | --- |
| `ralph-loop-security-reviewer` | auth, authorization, isolation, unsafe routes, secrets, production config |
| `ralph-loop-data-integrity-reviewer` | persistence, data movement, idempotency, transactions, cleanup safety |
| `ralph-loop-read-surface-reviewer` | API/CLI/UI parity, output formats, read authority, fail-closed behavior |
| `ralph-loop-e2e-gate-runner` | E2E gates, external services, reproducibility evidence, skipped gates |
| `ralph-loop-refactor-integrator` | post-hardening refactors with explicit write scope |

Default reviewer mode is read-only. Only assign write scopes after Ralph stops or when the user asks Codex to intervene.

Reviewer output must feed steering. Do not leave findings only in chat: copy blocking findings into `correction-queue.md`, update `status.md`, and restart or steer Ralph with a correction prompt when needed.

## Correction Format

Corrections must be specific enough for an executor:

```markdown
### CQ-001: Verify ownership before destructive cleanup

Severity: critical
Blocking: yes
Status: open
Owner: Ralph

Problem:
The implementation can delete local state before the remote authority proves it has accepted every required record.

Risk:
A partial sync or replay can cause permanent data loss.

Required fix:
- Gate cleanup behind a durable receipt.
- Reject partial receipts.
- Add replay and rollback tests.

Acceptance:
- [ ] Test rejects cleanup without receipt.
- [ ] Test rejects partial receipt.
- [ ] Test proves retry is idempotent.

Evidence:
- Commit:
- Tests:
```

## Final Gates

Base gate categories:

```text
<install or environment setup command>
<build command>
<typecheck or static analysis command>
<test command>
<lint or format-check command>
<security or dependency audit command>
<end-to-end command, if applicable>
git diff --check
```

Use repository-local guidance, scripts, CI, and domain skills to replace placeholders with real commands. If a gate fails or cannot run, classify it before declaring Done.

## Done Rule

Ralph can satisfy `<promise>RALPH_DONE</promise>` only when:

- every lane has evidence;
- no blocking correction remains open;
- required gates are green or classified;
- required E2E passed when applicable;
- the final stabilization wait completed five consecutive clean stabilization cycles with reset conditions respected;
- the worktree state is documented;
- Codex final review has no critical unresolved findings.

If Codex has to patch critical issues directly, mark the section as `Architect intervention` and rerun the relevant gates.
