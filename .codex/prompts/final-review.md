# Ralph Loop Final Review

Run final governor review for `<feature>`.

Check:

- every lane has evidence;
- no blocking correction remains open;
- gates are green or explicitly classified;
- security and data-integrity reviewers have no critical unresolved findings;
- the worktree state is documented;
- direct governor fixes, if any, are labeled `Architect intervention`.

Reject `RALPH_DONE` if any critical blocker remains.

