# Ralph Loop: <feature name>

You are implementing `<feature name>` in this repository.

Codex is acting as architect and gatekeeper. It may update correction and gate files while you work. Treat those files as blocking input.

Codex will actively review your code with focused subagents and steer this run through `correction-queue.md`, `gates.md`, and updates to this prompt. Those review findings are part of the implementation contract, not optional advice. Expect Codex to reject `RALPH_DONE` if subagent findings remain open.

## Read First

- AGENTS.md
- docs/roadmap/<feature>/
- <matching Codex skills>
- <canonical architecture or product docs>
- <feature-specific docs>

## Product Contract

- <invariant 1>
- <invariant 2>
- <invariant 3>

## Work Lanes

1. <lane 1>
2. <lane 2>
3. <lane 3>

At the start of each iteration:

- inspect `git status --short --branch`;
- identify the first incomplete lane or open correction;
- reread `correction-queue.md` and treat every `Blocking: yes` correction as higher priority than new feature work;
- continue from there without restarting completed work;
- preserve user changes and unrelated agent changes;
- do not touch generated directories by hand.

## Required Files

Keep these files current:

- `docs/roadmap/<feature>/status.md`
- `docs/roadmap/<feature>/correction-queue.md`
- `docs/roadmap/<feature>/gates.md`
- `docs/roadmap/<feature>/evidence/lane-N.md`

## Implementation Rules

- Follow local repo conventions.
- Commit coherent lane/correction changes if the repo workflow expects commits.
- Add or update tests with each meaningful behavior change.
- Close reviewer findings with code, tests, and evidence; do not mark a correction closed because the implementation "looks right".
- Do not leave destructive behavior guarded only by optimistic assumptions.
- If a command cannot run, document the blocker and add a reproducible fallback when possible.

## Required Gates

Before Done, run or explicitly classify the repository's required gates:

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

## Final Stabilization Wait

Do not output `RALPH_DONE` immediately after closing a correction or making a commit. Missing stabilization evidence is a false completion.

Before outputting `RALPH_DONE`, complete the final stabilization wait:

1. Confirm there are no open blocking corrections and no unexplained dirty worktree changes.
2. Run or record the required gates.
3. Perform five consecutive clean cycles:
   - sleep exactly 180 seconds;
   - reread `correction-queue.md`, `gates.md`, `status.md`, `git status --short --branch`, and recent commits;
   - if any blocker, failed gate, stale evidence, new commit, or unexplained dirty worktree state appears, fix it and reset the cycle count to zero;
   - otherwise count that as one clean cycle.
4. Only after five clean cycles, minimum 15 minutes, may you output `RALPH_DONE`.

## Completion Rule

Only satisfy the completion promise when the statement is true. This run assumes Claude Code has the Ralph Loop plugin installed. With that plugin, completion means outputting exactly:

```text
<promise>RALPH_DONE</promise>
```

when every lane is implemented, every blocking correction is closed with evidence, required gates are green or classified, the final stabilization wait has completed, and the worktree state is documented.
