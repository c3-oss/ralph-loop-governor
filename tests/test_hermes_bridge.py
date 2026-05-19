import json
import tempfile
import unittest
from pathlib import Path

import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / ".codex" / "skills" / "ralph-loop-governor" / "scripts" / "ralph-loop-hermes-bridge.py"
spec = importlib.util.spec_from_file_location("ralph_loop_hermes_bridge", SCRIPT)
assert spec is not None
assert spec.loader is not None
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class HermesBridgeTests(unittest.TestCase):
    def test_stop_without_ralph_done_requires_attention(self):
        payload = bridge.build_payload(
            source="claude-code",
            event="Stop",
            summary="Ralph stopped after asking whether to accept a re-scope.",
            stdin_event={},
            project="demo",
            session="tmux:demo",
            workdir=Path.cwd(),
            status_file="docs/roadmap/demo/status.md",
            correction_queue="docs/roadmap/demo/correction-queue.md",
            gates_file="docs/roadmap/demo/gates.md",
        )

        self.assertTrue(payload["attention_required"])
        self.assertIn("stop_without_completion", payload["reasons"])
        self.assertEqual(payload["role"], "negotiator")

    def test_ralph_done_stop_is_not_an_attention_alert(self):
        payload = bridge.build_payload(
            source="claude-code",
            event="Stop",
            summary="<promise>RALPH_DONE</promise>",
            stdin_event={},
            project="demo",
            session="tmux:demo",
            workdir=Path.cwd(),
            status_file=None,
            correction_queue=None,
            gates_file=None,
        )

        self.assertFalse(payload["attention_required"])
        self.assertEqual(payload["reasons"], [])

    def test_blocked_language_requires_attention_for_turn_complete(self):
        payload = bridge.build_payload(
            source="codex",
            event="agent-turn-complete",
            summary="I am blocked waiting for the governor to choose option A or B.",
            stdin_event={},
            project="demo",
            session="codex:demo",
            workdir=Path.cwd(),
            status_file=None,
            correction_queue=None,
            gates_file=None,
        )

        self.assertTrue(payload["attention_required"])
        self.assertIn("blocked_language", payload["reasons"])

    def test_duplicate_key_is_suppressed_until_ttl_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            payload = {"idempotency_key": "same", "created_at": "2026-01-01T00:00:00Z"}

            self.assertFalse(bridge.is_duplicate(state_path, payload, now=1_000, ttl_seconds=60))
            bridge.remember_event(state_path, payload, now=1_000)
            self.assertTrue(bridge.is_duplicate(state_path, payload, now=1_030, ttl_seconds=60))
            self.assertFalse(bridge.is_duplicate(state_path, payload, now=1_061, ttl_seconds=60))

    def test_missing_webhook_is_successful_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = bridge.parse_args([
                "--source", "claude-code",
                "--event", "Stop",
                "--summary", "Stopped early",
                "--state-dir", tmp,
                "--dry-run",
            ])
            code = bridge.run(args, stdin_text="{}")

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
