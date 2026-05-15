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
