# Hermes Negotiator Bridge

The Hermes negotiator bridge makes Hermes optional in a Ralph Loop run. When Hermes is available and a webhook URL is configured, Claude/Ralph and Codex hooks can send attention-worthy events to Hermes. When Hermes is absent, the hook script exits successfully and the manual workflow is unchanged.

Hermes is a passive TUI unblocker, not a second active coding governor. Its job is to keep the existing Claude/Ralph executor and Codex governor able to run when a user-like TUI action is required. It should make the smallest safe unblock action, preserve the intended completeness of the work, and hand control back to the normal governor/executor loop.

## Flow

```text
Codex governor prepares the run
  -> user starts Claude/Ralph executor
  -> Claude/Codex hooks call ralph-loop-hermes-bridge.py on rare attention events
  -> bridge classifies the event and suppresses duplicates
  -> if a Hermes webhook is configured, POST a compact negotiator payload
  -> Hermes performs the minimum safe unblock action when the TUI flow is blocked
  -> executor and governor continue; final acceptance still belongs to the governor
```

Hermes may answer a blocking TUI prompt, retry after a usage/rate limit, restart or continue Ralph after an iteration limit, or notify Codex when the executor is stopped and Codex can still govern the next step. It must not proactively review or correct code, choose the next implementation slice merely because a commit landed, accept `RALPH_DONE`, close corrections without evidence, or silently replace Codex/governor steering and final gates.

## What the bridge alerts on

The bridge only forwards events that usually need TUI-level unblocking:

- Claude/Ralph `Stop` without `RALPH_DONE`, especially max-iteration or early-stop cases that need a continue/restart handoff.
- Claude Code `Notification`, `PermissionRequest`, `PostToolUseFailure`, or `SubagentStop` when the TUI is waiting for user input.
- Codex `agent-turn-complete` or stop-like events that contain blocked/stuck/waiting language.
- Usage, rate, quota, or retry-limit messages that require waiting and trying again later.
- Messages containing decision markers such as `blocked`, `waiting for`, `need input`, `needs governor`, `accept or reject`, or `COMANDO_RALPH`.

Normal progress, routine tool use, newly landed commits, closed corrections, and a proper `<promise>RALPH_DONE</promise>` stop are silent.

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

Hermes should use the payload as a bounded TUI-unblock prompt:

1. Inspect only enough status, correction queue, gates, and recent transcript context to understand why the TUI flow stopped.
2. Decide whether a user-like unblock action is required now, or whether Codex/Ralph can continue without Hermes.
3. Produce one of:
   - an answer to the blocking TUI prompt, choosing the most complete safe delivery option when the prompt asks for scope;
   - a retry/continue action after a usage/rate/quota limit and appropriate wait;
   - a restart/continue handoff for Ralph after max iterations or early stop;
   - a concise notification to Codex when Codex can govern the next executor step;
   - a concise user-facing multiple-choice question only when the decision cannot be made safely;
   - a no-op if the event is stale, already resolved, or merely normal progress.
4. Avoid recursion. Do not trigger another hook storm from the negotiation output.
5. Do not use the bridge to perform code review, open new corrections, select the next implementation slice, or otherwise replace Codex governance.

## Safety guardrails

- Duplicate idempotency keys are suppressed for 10 minutes by default.
- Webhook delivery failures are recorded locally and do not fail the executor hook.
- Missing Hermes configuration is a successful no-op.
- The bridge is passive TUI-unblock infrastructure. It does not replace correction evidence, gates, final stabilization, active Codex governance, or final governor acceptance.
