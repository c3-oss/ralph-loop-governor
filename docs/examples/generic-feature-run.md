# Generic Feature Run Example

This example shows how to adapt the workflow for a feature named `team-audit-log`.

## Request

```text
$ralph-loop-governor implement team audit log: record important user actions, expose searchable admin history, and retain enough evidence for support investigations.
```

## Generated Workspace

```text
docs/roadmap/team-audit-log/
  ralph-loop-prompt.md
  status.md
  correction-queue.md
  gates.md
  evidence/
    lane-01.md
    lane-02.md
    lane-03.md
```

## Example Lanes

1. Event contract and persistence
2. Write-path instrumentation
3. Admin read surface and filters
4. E2E evidence and final gates

## Example Product Contract

- Every security-sensitive action records actor, target, timestamp, action type, request context, and result.
- The read surface enforces the same admin authorization as other admin tools.
- Audit writes must not block the primary action unless the action explicitly requires durable audit evidence.
- Search and filters must be consistent across API and UI.

## Example Corrections

```markdown
### CQ-001: Audit read route does not enforce admin authorization

Severity: critical
Blocking: yes
Status: open
Owner: Ralph

Problem:
The read route returns audit events to any authenticated user.

Risk:
Users can inspect actions from other users or privileged operators.

Required fix:
- Enforce admin authorization on every audit read path.
- Add tests for member, admin, and unauthenticated callers.

Acceptance:
- [ ] Member caller is rejected.
- [ ] Unauthenticated caller is rejected.
- [ ] Admin caller can filter events.

Evidence:
- Commit:
- Tests:
```

## Example Final Review

Final review should reject Done if:

- an audit event can be read without admin authorization;
- write paths silently skip required events;
- filters differ across API and UI;
- E2E evidence does not show a real action flowing into the read surface;
- the correction queue has any open blocking item;
- the executor did not document five consecutive clean stabilization cycles of `sleep 180 seconds` before Done.
