# Claude Notes

Read `AGENTS.md` first. It is the canonical instruction layer for this repository.

## Claude Code Specifics

- Install the Anthropic-verified Ralph Loop plugin before running executor loops: https://claude.com/plugins/ralph-loop.
- Use Claude Code's native subagent feature when session policy allows it.
- Specialists live under `.claude/agents/` and mirror `.codex/agents/`.
- Skills are canonical under `.codex/skills/`; do not duplicate them under `.claude/skills/`.
- Ralph Loop executor runs must complete five consecutive clean stabilization cycles of `sleep 180 seconds`, at least 15 minutes total, before `RALPH_DONE`.
- Shared-checkout mutations such as edits, generated output updates, staging, committing, rebasing, branch switching, and pushing should be serialized under one owner.
- Commit messages must use Conventional Commits.
- If guidance changes in `.codex/skills/`, `.codex/agents/`, `.claude/agents/`, or `AGENTS.md`, keep this file aligned.

## Common Skills

- `.codex/skills/ralph-loop-governor/SKILL.md` prepares, monitors, steers, and gates Ralph Loop implementation runs.
- `.codex/skills/repo-commit-and-push/SKILL.md` handles focused commits and explicit push policy.
- `.codex/skills/parallel-delegation/SKILL.md` describes safe subagent decomposition.
- `.codex/skills/sync-claude-md/SKILL.md` keeps Claude-facing guidance aligned.
