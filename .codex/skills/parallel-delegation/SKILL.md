---
name: parallel-delegation
description: Use when non-trivial work can be split across native subagents for parallel exploration, implementation, or verification.
---

# Parallel Delegation

Use native subagents when a non-trivial task has independent lanes that can run without blocking the parent's immediate critical path.

## Policy

- Decompose first, then delegate independent side lanes early when subagents are available.
- Keep the immediate blocking path in the parent agent.
- Use native client subagents only. Do not shell out to detached agent processes.
- The parent agent owns decomposition, coordination, integration, validation, and the final response.
- Shared-checkout mutations such as edits, generated output updates, staging, committing, rebasing, branch switching, and pushing must be serialized under one owner.

## Good Parallel Lanes

- Code exploration by subsystem, entrypoint, or risk area.
- Read-only reviews by security, data integrity, API/CLI/UI parity, or test coverage.
- Verification such as focused test runs, log inspection, CI analysis, or regression review.
- Implementation split by disjoint file ownership or clearly separated responsibilities.

## Do Not Parallelize

- Tiny requests where delegation overhead dominates.
- Destructive operations or external mutations that need one ordered decision.
- Closely coupled edits to the same files, generated outputs, or migrations.
- Work that lacks a clear ownership boundary or expected output.

## Subagent Prompt Contract

Every delegated task should state:

- exact objective;
- owned files, modules, repos, or responsibility;
- first action to take;
- limits and actions to avoid;
- that other agents may be editing nearby work;
- expected final output or changed paths.

