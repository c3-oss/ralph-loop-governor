# Ralph Loop Governor

Reusable agent workflow assets for running a long implementation loop with an executor agent while a governor agent plans, reviews, steers, and gates the work.

The workflow is intentionally tool-light:

- Codex owns planning, governance, reviewer subagents, correction queues, and final gates.
- Claude/Ralph owns long-running implementation throughput.
- Reviewer agents inspect the work during the run, not only after the executor claims Done.
- Blocking findings become correction queue items with acceptance criteria and evidence.
- Done requires lane evidence, closed corrections, and gate results.

## What Is Included

```text
.codex/
  agents/                         # Codex reviewer subagents
  prompts/                        # Reusable kickoff/restart/review prompts
  skills/
    ralph-loop-governor/          # Main workflow skill and templates
    repo-commit-and-push/         # Generic commit/push policy
    parallel-delegation/          # Subagent decomposition policy
    sync-claude-md/               # Keep Claude-facing guidance aligned
.claude/
  agents/                         # Claude Code mirrors of the reviewer agents
docs/
  ralph-loop-governor.md          # Full operating model
  examples/generic-feature-run.md # Sanitized example run
```

## Install In Another Repository

Copy the `.codex/`, `.claude/`, `AGENTS.md`, and `CLAUDE.md` files into a target repository, then adjust the target repo guidance and gate commands.

## Prerequisites

- Claude Code must have the Anthropic-verified [Ralph Loop plugin](https://claude.com/plugins/ralph-loop) installed.
- The plugin provides the iterative Claude command used by this workflow. These docs use the `/ralph-loop:ralph-loop` command shape; if your Claude Code installation exposes the command as `/ralph-loop`, use that local command name with the same prompt and flags.

Minimum copy:

```text
.codex/skills/ralph-loop-governor/
.codex/agents/ralph-loop-*.toml
.claude/agents/ralph-loop-*.md
```

Recommended copy:

```text
.codex/
.claude/
AGENTS.md
CLAUDE.md
docs/ralph-loop-governor.md
```

## Quick Start

In Codex:

```text
$ralph-loop-governor implement <feature goal>
```

Codex should create:

```text
docs/roadmap/<feature>/
  ralph-loop-prompt.md
  status.md
  correction-queue.md
  gates.md
  evidence/
    lane-01.md
```

Then run the executor in Claude/Ralph:

```text
/ralph-loop:ralph-loop "@docs/roadmap/<feature>/ralph-loop-prompt.md" --max-iterations 30 --completion-promise RALPH_DONE
```

This command requires the [Ralph Loop plugin](https://claude.com/plugins/ralph-loop) in Claude Code.

When corrections are needed:

```text
/ralph-loop:ralph-loop "Read @docs/roadmap/<feature>/ralph-loop-prompt.md, @docs/roadmap/<feature>/correction-queue.md, and @docs/roadmap/<feature>/gates.md. Close every blocking correction with evidence, wait 5 minutes, reread the correction queue, and repeat until no blocking correction remains open." --max-iterations 20 --completion-promise RALPH_DONE
```

## Adaptation Checklist

- Replace placeholder gates in `gates.md` with the target repository's real install, build, test, lint, security, and E2E commands.
- Add domain specialists only when the target repository has domain-specific invariants.
- Keep reviewer agents read-only by default.
- Keep `.codex/skills/` as the canonical skill home. `.claude/agents/` mirrors specialists for Claude Code.
- Do not treat an executor's Done signal as sufficient. The governor must verify evidence and gates.
