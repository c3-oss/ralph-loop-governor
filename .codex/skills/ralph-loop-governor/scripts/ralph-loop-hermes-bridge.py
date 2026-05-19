#!/usr/bin/env python3
"""Optional Hermes negotiator bridge for Ralph Loop hooks.

The bridge is intentionally safe-by-default:
- if Hermes/webhook configuration is absent, it exits 0 and leaves the
  normal manual Ralph Loop workflow untouched;
- it only emits attention-worthy events;
- duplicate events are suppressed for a short TTL to prevent hook loops.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ATTENTION_EVENTS = {
    "notification",
    "permissionrequest",
    "posttoolusefailure",
    "subagentstop",
    "stop",
    "agent-turn-complete",
}

BLOCKED_TERMS = (
    "blocked",
    "stuck",
    "paused",
    "pause",
    "waiting for",
    "need input",
    "needs input",
    "needs codex",
    "needs governor",
    "needs user",
    "permission",
    "cannot continue",
    "can't continue",
    "failed",
    "error",
    "exception",
    "unclear",
    "question",
    "choose option",
    "accept or reject",
    "comando_ralph",
)

DONE_MARKERS = ("ralph_done", "<promise>ralph_done</promise>")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forward Ralph Loop attention events to Hermes when configured.")
    parser.add_argument("--source", default=os.getenv("RALPH_LOOP_SOURCE", "unknown"))
    parser.add_argument("--event", default=os.getenv("RALPH_LOOP_EVENT", "unknown"))
    parser.add_argument("--summary", default=os.getenv("RALPH_LOOP_SUMMARY", ""))
    parser.add_argument("--project", default=os.getenv("RALPH_LOOP_PROJECT"))
    parser.add_argument("--session", default=os.getenv("RALPH_LOOP_SESSION"))
    parser.add_argument("--workdir", default=os.getenv("RALPH_LOOP_WORKDIR", os.getcwd()))
    parser.add_argument("--status-file", default=os.getenv("RALPH_LOOP_STATUS_FILE"))
    parser.add_argument("--correction-queue", default=os.getenv("RALPH_LOOP_CORRECTION_QUEUE"))
    parser.add_argument("--gates-file", default=os.getenv("RALPH_LOOP_GATES_FILE"))
    parser.add_argument("--webhook-url", default=os.getenv("RALPH_HERMES_WEBHOOK_URL") or os.getenv("HERMES_WEBHOOK_URL"))
    parser.add_argument("--state-dir", default=os.getenv("RALPH_LOOP_BRIDGE_STATE_DIR"))
    parser.add_argument("--ttl-seconds", type=int, default=int(os.getenv("RALPH_LOOP_BRIDGE_TTL_SECONDS", "600")))
    parser.add_argument("--timeout-seconds", type=int, default=int(os.getenv("RALPH_LOOP_BRIDGE_TIMEOUT_SECONDS", "10")))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-payload", action="store_true")
    return parser.parse_args(argv)


def load_stdin_event(stdin_text: str) -> dict[str, Any]:
    text = stdin_text.strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    if isinstance(parsed, dict):
        return parsed
    return {"value": parsed}


def first_present(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def text_excerpt(data: dict[str, Any], fallback: str, limit: int = 2000) -> str:
    candidates = [
        fallback,
        first_present(data, "message", "summary", "text", "transcript", "last_message", "notification"),
        json.dumps(data, ensure_ascii=False, sort_keys=True) if data else "",
    ]
    joined = "\n".join(str(c) for c in candidates if c)
    return joined[:limit]


def infer_project(workdir: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    return workdir.resolve().name


def event_reasons(event: str, excerpt: str) -> list[str]:
    normalized_event = event.lower()
    normalized_excerpt = excerpt.lower()
    if any(marker in normalized_excerpt for marker in DONE_MARKERS):
        return []

    reasons: list[str] = []
    if normalized_event == "stop":
        reasons.append("stop_without_completion")
    elif normalized_event in ATTENTION_EVENTS:
        reasons.append(f"event:{event}")

    if any(term in normalized_excerpt for term in BLOCKED_TERMS):
        reasons.append("blocked_language")

    return sorted(set(reasons))


def stable_key(payload_core: dict[str, Any]) -> str:
    material = json.dumps(payload_core, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def build_payload(
    *,
    source: str,
    event: str,
    summary: str,
    stdin_event: dict[str, Any],
    project: str | None,
    session: str | None,
    workdir: Path,
    status_file: str | None,
    correction_queue: str | None,
    gates_file: str | None,
) -> dict[str, Any]:
    source = str(first_present(stdin_event, "source") or source)
    event = str(first_present(stdin_event, "event", "hook_event_name", "type") or event)
    summary = str(first_present(stdin_event, "summary", "message") or summary)
    project_name = infer_project(workdir, str(first_present(stdin_event, "project") or project or ""))
    session_name = str(first_present(stdin_event, "session", "tmux_session", "pane") or session or "")
    excerpt = text_excerpt(stdin_event, summary)
    reasons = event_reasons(event, excerpt)

    core = {
        "source": source,
        "event": event,
        "project": project_name,
        "session": session_name,
        "summary": summary,
        "excerpt": excerpt,
    }

    payload_summary = summary or (excerpt.splitlines()[0] if excerpt else "Ralph Loop attention event")

    return {
        "schema_version": "ralph-loop-hermes-bridge/v1",
        "role": "negotiator",
        "source": source,
        "event": event,
        "project": project_name,
        "session": session_name,
        "workdir": str(workdir),
        "status_file": status_file,
        "correction_queue": correction_queue,
        "gates_file": gates_file,
        "summary": payload_summary,
        "excerpt": excerpt,
        "attention_required": bool(reasons),
        "reasons": reasons,
        "negotiation_contract": {
            "goal": "Help the governor and executor unblock the run without replacing final human/governor acceptance.",
            "safe_actions": [
                "inspect roadmap status, correction queue, gates, and recent transcript",
                "summarize the blocker as a concrete executor instruction or governor decision",
                "ask for a binary or small multiple-choice decision when needed",
                "send a bounded steering message back to the appropriate pane only when configured",
            ],
            "guardrails": [
                "do not accept RALPH_DONE on behalf of the governor",
                "do not close corrections without evidence",
                "avoid hook-to-agent recursion with idempotency and rate limits",
            ],
        },
        "idempotency_key": stable_key(core),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def default_state_dir(workdir: Path) -> Path:
    return workdir / ".ralph-loop" / "hermes-bridge"


def load_state(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": {}}
    if not isinstance(data, dict):
        return {"events": {}}
    data.setdefault("events", {})
    return data


def is_duplicate(state_path: Path, payload: dict[str, Any], *, now: float | None = None, ttl_seconds: int = 600) -> bool:
    now = time.time() if now is None else now
    state = load_state(state_path)
    seen_at = state.get("events", {}).get(payload["idempotency_key"])
    return seen_at is not None and now - float(seen_at) < ttl_seconds


def remember_event(state_path: Path, payload: dict[str, Any], *, now: float | None = None) -> None:
    now = time.time() if now is None else now
    state = load_state(state_path)
    events = state.setdefault("events", {})
    events[payload["idempotency_key"]] = now
    cutoff = now - 24 * 60 * 60
    state["events"] = {key: value for key, value in events.items() if float(value) >= cutoff}
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")


def resolve_webhook_url(args: argparse.Namespace, workdir: Path) -> str | None:
    if args.webhook_url:
        return args.webhook_url
    for path in (
        workdir / ".ralph-loop" / "hermes-webhook-url",
        Path.home() / ".ralph-loop" / "hermes-webhook-url",
    ):
        try:
            value = path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            continue
        if value:
            return value
    return None


def post_json(url: str, payload: dict[str, Any], timeout_seconds: int) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "ralph-loop-hermes-bridge/1"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response.read()


def append_local_event(state_dir: Path, payload: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def run(args: argparse.Namespace, stdin_text: str | None = None) -> int:
    workdir = Path(args.workdir).resolve()
    stdin_event = load_stdin_event(sys.stdin.read() if stdin_text is None else stdin_text)
    payload = build_payload(
        source=args.source,
        event=args.event,
        summary=args.summary,
        stdin_event=stdin_event,
        project=args.project,
        session=args.session,
        workdir=workdir,
        status_file=args.status_file,
        correction_queue=args.correction_queue,
        gates_file=args.gates_file,
    )

    if args.print_payload:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    if not payload["attention_required"]:
        return 0

    state_dir = Path(args.state_dir).resolve() if args.state_dir else default_state_dir(workdir)
    state_path = state_dir / "state.json"
    if is_duplicate(state_path, payload, ttl_seconds=args.ttl_seconds):
        return 0

    webhook_url = resolve_webhook_url(args, workdir)
    if args.dry_run:
        append_local_event(state_dir, payload)
        remember_event(state_path, payload)
        return 0

    if webhook_url:
        try:
            post_json(webhook_url, payload, args.timeout_seconds)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            append_local_event(state_dir, {**payload, "delivery_error": str(exc)})
            return 0
        remember_event(state_path, payload)
        return 0

    if shutil.which("hermes"):
        append_local_event(state_dir, {**payload, "delivery": "no_webhook_configured"})
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
