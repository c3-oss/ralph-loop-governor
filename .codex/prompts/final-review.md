# Ralph Loop Final Review

Run final governor review for `<feature>`.

Check:

- every lane has evidence;
- no blocking correction remains open;
- gates are green or explicitly classified;
- final stabilization wait evidence shows five consecutive clean cycles of `sleep 180 seconds`;
- security and data-integrity reviewers have no critical unresolved findings;
- the worktree state is documented;
- direct governor fixes, if any, are labeled `Architect intervention`.

Reject `RALPH_DONE` if any critical blocker remains or if the final stabilization wait is missing, shorter than 15 minutes, or ignored reset conditions such as open blockers, failed gates, stale evidence, new commits, or unexplained dirty worktree state.
