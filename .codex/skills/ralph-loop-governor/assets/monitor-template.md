# <Repo> <Feature> Ralph Loop Monitor

Repository: `<repo path>`
Feature workspace: `docs/roadmap/<feature>/`
Governor: Codex
Executor: Ralph/Claude
Completion signal: RALPH_DONE
Monitor interval: 5 minutes unless overridden

## Policy

- Stay read-only with respect to implementation files while Ralph is active and making progress.
- Record every check with timestamp, worktree state, recent commits, changed areas, lane status, correction queue, gates, completion signal, open blockers, and no-change streak.
- Convert reviewer findings into blocking corrections when they can affect behavior, security, data integrity, parity, or release gates.
- Treat Done as pending until gates and final review pass.

## Checks

### <timestamp> Check 1

- `git status --short --branch`:
- Recent commits:
- Changed areas:
- Lane evidence/status:
- Correction queue:
- Gates:
- Completion signal:
- Open blockers:
- No-change streak:
- Codex action:

