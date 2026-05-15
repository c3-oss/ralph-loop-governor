# Contributing

Keep this repository generic and reusable.

## Adding Or Changing Skills

- Put reusable skills under `.codex/skills/<skill-name>/SKILL.md`.
- Keep `SKILL.md` concise and move templates into `assets/`.
- Use small-letter hyphenated skill names.
- Add `agents/openai.yaml` for UI metadata when useful.
- Update `CLAUDE.md` if Claude Code needs to know about the change.

## Adding Or Changing Agents

- Add Codex agents under `.codex/agents/`.
- Mirror Claude Code agents under `.claude/agents/` when the role is useful in Claude Code.
- Keep reviewers read-only unless the agent is explicitly an implementation or refactor integrator.
- Avoid product-specific names, paths, commands, and domain assumptions.

## Review Checklist

- No source-project names or internal paths leaked.
- Commits use Conventional Commits.
- Placeholder commands are clearly marked for replacement.
- TOML agent files parse.
- YAML metadata files parse when a parser is available.
- Markdown links point to existing files.
- `git diff --check` passes.
