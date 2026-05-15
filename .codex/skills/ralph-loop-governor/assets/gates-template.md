# <Feature> Gates

## Base Commands

Replace placeholders with commands discovered from repository guidance, manifests, task runners, and CI.

| Command | Required | Last Result | Notes |
| --- | --- | --- | --- |
| `<install or setup command>` | yes | not-run | |
| `<build command>` | yes | not-run | |
| `<typecheck or static analysis command>` | yes | not-run | |
| `<test command>` | yes | not-run | |
| `<lint or format-check command>` | yes | not-run | |
| `<security or dependency audit command>` | yes | not-run | |
| `git diff --check` | yes | not-run | |

## Domain Commands

Add domain-specific gates required by local architecture, release, security, or data requirements.

| Command | Required | Last Result | Notes |
| --- | --- | --- | --- |
| `<end-to-end command>` | when-applicable | not-run | |

## Done Check

- [ ] Worktree state documented.
- [ ] All lanes have evidence.
- [ ] No open blocking corrections.
- [ ] Required domain gates passed or blockers are documented.
- [ ] Security/dependency audit output classified when applicable.
- [ ] Final Codex review completed.

