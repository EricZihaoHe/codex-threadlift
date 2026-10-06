"""Check that the CLI helper only reports a verified receiver as successful."""

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "start-cli-receiver.py"
SPEC = importlib.util.spec_from_file_location("start_cli_receiver", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CliReceiverTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)
        self.private = self.cwd / ".codex-handoff"
        self.private.mkdir()
        self.handoff = self.private / "handoff.md"
        self.handoff.write_text("handoff", encoding="utf-8")
        self.prompt = self.private / "receiver-prompt.md"
        self.prompt.write_text("Receive the handoff.", encoding="utf-8")
        self.receipt = self.private / "ready.md"

    def invoke(self, fake_run):
        argv = ["start-cli-receiver.py", "--cwd", str(self.cwd),
                "--prompt-file", str(self.prompt), "--handoff", str(self.handoff),
                "--receipt", str(self.receipt)]
        stream = io.StringIO()
        with patch.object(sys, "argv", argv), patch.object(MODULE.subprocess, "run", fake_run):
            with contextlib.redirect_stdout(stream):
                code = MODULE.main()
        return code, stream.getvalue()

    def test_success_requires_matching_receipt_and_workspace_write(self):
        def fake_run(command, **kwargs):
            self.assertEqual(command[:5], ["codex", "exec", "-C", str(self.cwd.resolve()), "-s"])
            self.assertIn("workspace-write", command)
            self.assertEqual(kwargs["cwd"], self.cwd.resolve())
            self.receipt.write_text(str(self.handoff.resolve()) + "\n接收完成，等待用户指令\n",
                                    encoding="utf-8")
            return subprocess.CompletedProcess(command, 0,
                                               '{"type":"thread.started","thread_id":"test-thread"}\n'
                                               '{"type":"turn.completed"}\n', "")

        code, output = self.invoke(fake_run)
        self.assertEqual(code, 0)
        self.assertIn('"ok": true', output)
        self.assertIn('"thread_id": "test-thread"', output)

    def test_completed_turn_without_receipt_is_failure(self):
        fake_result = subprocess.CompletedProcess(["codex"], 0,
                                                  '{"type":"thread.started","thread_id":"test-thread"}\n'
                                                  '{"type":"turn.completed"}\n', "")
        code, output = self.invoke(lambda *args, **kwargs: fake_result)
        self.assertEqual(code, 1)
        self.assertIn('"receipt_verified": false', output)

    def test_receipt_for_different_handoff_is_failure(self):
        fake_result = subprocess.CompletedProcess(["codex"], 0,
                                                  '{"type":"thread.started","thread_id":"test-thread"}\n'
                                                  '{"type":"turn.completed"}\n', "")
        def fake_run(*args, **kwargs):
            self.receipt.write_text("/other/handoff.md\n接收完成，等待用户指令\n",
                                    encoding="utf-8")
            return fake_result

        code, output = self.invoke(fake_run)
        self.assertEqual(code, 1)
        self.assertIn('"receipt_verified": false', output)


if __name__ == "__main__":
    unittest.main()
