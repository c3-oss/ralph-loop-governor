# Ralph Loop Correction Restart

Restart Ralph on the correction queue.

This requires the Anthropic-verified Ralph Loop plugin installed in Claude Code: https://claude.com/plugins/ralph-loop.

Use this executor command shape:

```text
/ralph-loop:ralph-loop "Read @docs/roadmap/<feature>/ralph-loop-prompt.md, @docs/roadmap/<feature>/correction-queue.md, and @docs/roadmap/<feature>/gates.md. Close every blocking correction with code, tests, and evidence. If no blocking correction remains, run the mandatory final stabilization wait: five clean cycles of sleep 180 seconds, then reread correction queue, gates, status, git status, and recent commits. Any change, open blocker, failed gate, stale evidence, new commit, or unexplained dirty worktree resets the five-cycle count to zero. Output RALPH_DONE only after all five cycles stay clean." --max-iterations 20 --completion-promise RALPH_DONE
```

If Claude Code exposes the plugin command as `/ralph-loop`, use that command name with the same prompt and flags.

Before restart, make sure every blocking correction has an ID, severity, risk, required fix, acceptance criteria, and evidence fields. The correction prompt must also preserve the five-cycle final stabilization wait requirement.
