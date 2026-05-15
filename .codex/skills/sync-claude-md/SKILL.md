---
name: sync-claude-md
description: Use when editing AGENTS.md, local skills, Codex agents, or Claude agents to keep CLAUDE.md aligned with repository guidance.
---

# Sync Claude Md

Use this skill whenever work changes any local skill under `.codex/skills/`, any local subagent under `.codex/agents/`, any mirrored Claude agent under `.claude/agents/`, or `AGENTS.md`.

## Workflow

1. Review the changed instruction or agent update.
2. Identify what Claude Code needs to know.
3. Update `CLAUDE.md` in the same change set when Claude-facing guidance changes.
4. Keep `CLAUDE.md` concise and policy-oriented.

## Guardrails

- Do not leave skill, agent, or `AGENTS.md` guidance changes with stale Claude-facing instructions.
- Do not copy every skill into `CLAUDE.md`; point to canonical files.
- Do not duplicate skills under `.claude/skills/`.

