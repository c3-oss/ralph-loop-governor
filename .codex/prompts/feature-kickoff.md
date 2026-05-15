# Ralph Loop Feature Kickoff

Prepare a governed Ralph Loop for `<feature>`.

Before returning the Claude command, state that Claude Code must have the Anthropic-verified Ralph Loop plugin installed: https://claude.com/plugins/ralph-loop.

Create `docs/roadmap/<feature>/` with:

- `ralph-loop-prompt.md`
- `status.md`
- `correction-queue.md`
- `gates.md`
- `evidence/lane-N.md`

Derive lanes from the feature goal, local repository guidance, matched domain docs, and tests. Keep the executor prompt specific enough that Ralph can implement lane by lane without reinterpreting the product goal. Return the exact `/ralph-loop:ralph-loop` command to run, and note that some Claude Code installations expose the plugin command as `/ralph-loop`.

The generated executor prompt must require a final stabilization wait before `RALPH_DONE`: five consecutive clean cycles of `sleep 180 seconds`, then reread correction queue, gates, status, `git status --short --branch`, and recent commits. Any open blocker, failed gate, stale evidence, new commit, or unexplained dirty worktree resets the counter to zero.
