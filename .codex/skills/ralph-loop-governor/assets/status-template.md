# <Feature> Ralph Loop Status

Started: <timestamp>
Repository: `<repo path>`
Branch: `<branch>`
Monitor: `<monitor path>`
Monitor interval: 5 minutes unless overridden
Completion signal: RALPH_DONE

## Current State

Status: planned | running | correction | final-review | done | blocked
Current lane: <lane id>
Current HEAD: <sha>
No-change streak: 0
Ralph active: yes | no
Final stabilization wait: not-started | running | reset | complete
Clean stabilization cycles: 0/5
Stabilization started:
Stabilization last check:

## Lane Status

| Lane | Owner | Status | Commit(s) | Evidence |
| --- | --- | --- | --- | --- |
| 01 | Ralph | open | | evidence/lane-01.md |

## Out-Of-Sequence Work

Use this section when exploratory or downstream work exists before its prerequisite lane is accepted. Do not count it as lane evidence until blockers are closed and the governor reclassifies it.

| Area | Status | Why Not Accepted | Next Action |
| --- | --- | --- | --- |

## Open Blocking Corrections

| ID | Severity | Owner | Summary |
| --- | --- | --- | --- |

## Latest Gates

| Command | Result | Notes |
| --- | --- | --- |

## Final Stabilization Wait

| Cycle | Timestamp | Result | Reset Reason | Notes |
| --- | --- | --- | --- | --- |
| 1 | | clean | | |

## Decisions

- <timestamp>: <decision>
