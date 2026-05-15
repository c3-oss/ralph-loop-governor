# Repository Guidelines

This repository packages reusable AI workflow guidance. Keep the content generic, installable, and free of product-specific implementation assumptions.

## Project Structure

- `.codex/skills/` is the canonical home for reusable skills.
- `.codex/agents/` contains Codex specialist subagents.
- `.claude/agents/` mirrors the Codex specialists for Claude Code.
- `.codex/prompts/` contains reusable prompt fragments.
- `docs/` contains user-facing workflow documentation and examples.

## Editing Rules

- Write repo artifacts in English.
- Keep instructions direct, concrete, and easy to scan.
- Do not embed secrets, machine-local paths, customer names, or internal repository names.
- Do not add product-specific gates as defaults. Use placeholders and tell users to replace them with local commands.
- When changing `.codex/skills/`, `.codex/agents/`, `.claude/agents/`, or this file, update `CLAUDE.md` if Claude-facing guidance changes.
- Do not duplicate skills under `.claude/skills/`.

## Commit Guidelines

Use Conventional Commits with imperative summaries and explanatory bodies. Split unrelated work by responsibility. Push only when explicitly authorized.

For commit work, follow `.codex/skills/repo-commit-and-push/SKILL.md`.

## Validation

Before publishing a change, check:

```text
git status --short
git diff --check
```

When possible, also validate:

- Markdown links point to existing files.
- TOML agent files parse.
- YAML metadata files parse.
- Generic assets do not contain source-project names or domain-specific assumptions.
