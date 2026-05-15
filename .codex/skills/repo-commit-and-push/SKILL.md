---
name: repo-commit-and-push
description: Use when preparing, splitting, staging, writing, reviewing, pushing, or publishing git commits for repository work.
---

# Repo Commit And Push

Use this skill when commits are part of a task.

## Policy

- Use Conventional Commits for every commit: `<type>(<optional-scope>): <imperative summary>`.
- Never collapse unrelated work into one commit.
- Every commit must represent one complete, coherent delivery slice.
- Group files into a commit only when they share one purpose and can be described by one subject and one body.
- Before writing a commit message, inspect repo-local guidance and recent git history to determine preferred types and scopes.
- If the type or scope is ambiguous after checking guidance and history, choose the closest standard Conventional Commit type and omit scope when no honest scope exists.
- Split commits by coherent responsibility: implementation, tests, documentation, skills, agent instructions, configuration, dependency metadata, or cleanup.
- Prefer gradual commits over one large commit when there are multiple real delivery slices.
- Push only when the user explicitly asks for it or has confirmed an execution envelope that includes publishing.

## Commit Format

- Subject line uses Conventional Commits: `<type>(<optional-scope>): <imperative summary>`.
- Prefer standard types such as `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`, `style`, `perf`, and `revert`.
- Use imperative mood.
- Keep the subject concise.
- Include a short explanatory body that states what changed, why it changed, and validation performed or skipped.

Preferred template:

```text
<type>(<optional-scope>): <imperative summary>

<One short paragraph explaining the change set and its purpose.>

Validation: <commands or "not run: reason">
```

## Workflow

1. Review `git status --short` and identify distinct delivery slices.
2. Inspect repo-local guidance and recent git history to determine preferred Conventional Commit types and scopes.
3. If the scope is unclear, omit it instead of inventing a misleading scope.
4. Stage only one coherent group at a time.
5. Review `git diff --cached` before committing.
6. Commit with a subject and explanatory body that describe that one slice completely.
7. Repeat for remaining groups in a logical order.
8. Push only when explicitly authorized.

## Guardrails

- Do not rewrite or squash existing commits unless explicitly asked.
- Do not mix unrelated user changes into your commits.
- Do not make a "commit everything" commit just to clean the worktree.
- If one staged set cannot be explained as one complete change, split it again.
