# Hermes Negotiator Bridge

The Hermes negotiator bridge makes Hermes optional in a Ralph Loop run. When Hermes is available and a webhook URL is configured, Claude/Ralph and Codex hooks can send attention-worthy events to Hermes. When Hermes is absent, the hook script exits successfully and the manual workflow is unchanged.

## Flow

```text
Codex governor prepares the run
  -> user starts Claude/Ralph executor
  -> Claude/Codex hooks call ralph-loop-hermes-bridge.py on rare attention events
  -> bridge classifies the event and suppresses duplicates
  -> if a Hermes webhook is configured, POST a compact negotiator payload
  -> Hermes inspects roadmap state and negotiates the next unblock step
  -> executor and governor continue; final acceptance still belongs to the governor
```

Hermes is a negotiator, not the final judge. It may translate a stuck executor message into a concrete governor decision, or translate a governor correction into a bounded executor instruction. It must not accept `RALPH_DONE`, close corrections without evidence, or silently replace the final Codex/governor gate.

## What the bridge alerts on

The bridge only forwards events that usually need attention:

- Claude/Ralph `Stop` without `RALPH_DONE`.
- Claude Code `Notification`, `PermissionRequest`, `PostToolUseFailure`, or `SubagentStop`.
- Codex `agent-turn-complete` or stop-like events that contain blocked/stuck/waiting language.
- Messages containing decision markers such as `blocked`, `waiting for`, `need input`, `needs governor`, `accept or reject`, or `COMANDO_RALPH`.

Normal progress, routine tool use, and a proper `<promise>RALPH_DONE</promise>` stop are silent.

## Files

```text
.codex/skills/ralph-loop-governor/scripts/ralph-loop-hermes-bridge.py
.codex/skills/ralph-loop-governor/assets/hermes-bridge-claude-settings.fragment.json
.codex/skills/ralph-loop-governor/assets/hermes-bridge-codex-notify.fragment.toml
```

## Configure Hermes

Create a Hermes webhook subscription for the run. Pick a route name that is unique enough for the repository or feature.

```bash
hermes webhook subscribe ralph-loop-<feature>
```

Then put the resulting webhook URL in one of these locations:

```bash
export RALPH_HERMES_WEBHOOK_URL="https://<hermes-host>/webhooks/ralph-loop-<feature>"
# or
mkdir -p .ralph-loop
printf '%s\n' "https://<hermes-host>/webhooks/ralph-loop-<feature>" > .ralph-loop/hermes-webhook-url
```

If no webhook URL is configured, the bridge exits 0. If a `hermes` binary exists but no webhook URL exists, the bridge records local JSONL events in `.ralph-loop/hermes-bridge/events.jsonl` for later inspection.

## Configure Claude Code hooks

Merge the JSON fragment from `assets/hermes-bridge-claude-settings.fragment.json` into the target repository or user Claude Code settings. Replace `<feature>`, `<tmux-session-or-pane>`, and roadmap paths.

The command intentionally uses only local files and environment variables. If `RALPH_HERMES_WEBHOOK_URL` is unset and `.ralph-loop/hermes-webhook-url` is absent, Claude/Ralph continues exactly as before.

## Configure Codex notify

Merge the TOML fragment from `assets/hermes-bridge-codex-notify.fragment.toml` into the target Codex config for the run. This is useful for the governor side: if Codex stops with a blocked decision or emits a `COMANDO_RALPH:` handoff, Hermes can turn that into a bounded executor instruction.

## Payload contract

The bridge posts JSON shaped like this:

```json
{
  "schema_version": "ralph-loop-hermes-bridge/v1",
  "role": "negotiator",
  "source": "claude-code",
  "event": "Stop",
  "project": "example-repo",
  "session": "tmux:ralph-example",
  "workdir": "/repo/path",
  "status_file": "docs/roadmap/<feature>/status.md",
  "correction_queue": "docs/roadmap/<feature>/correction-queue.md",
  "gates_file": "docs/roadmap/<feature>/gates.md",
  "summary": "Ralph stopped before RALPH_DONE and is waiting for a decision.",
  "attention_required": true,
  "reasons": ["stop_without_completion", "blocked_language"],
  "idempotency_key": "sha256...",
  "created_at": "2026-01-01T00:00:00Z"
}
```

Hermes should use the payload as a bounded triage prompt:

1. Inspect the status, correction queue, gates, and recent transcript if available.
2. Decide whether the blocker belongs to the executor, the governor, or the human user.
3. Produce one of:
   - an exact executor steering message;
   - an exact governor/Codex decision request;
   - a concise user-facing multiple-choice question;
   - a no-op if the event is stale or already resolved.
4. Avoid recursion. Do not trigger another hook storm from the negotiation output.

## Safety guardrails

- Duplicate idempotency keys are suppressed for 10 minutes by default.
- Webhook delivery failures are recorded locally and do not fail the executor hook.
- Missing Hermes configuration is a successful no-op.
- The bridge is alert/negotiation infrastructure. It does not replace correction evidence, gates, final stabilization, or final governor acceptance.
