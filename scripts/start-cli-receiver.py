#!/usr/bin/env python3
"""Start a fresh, persisted Codex CLI receiver and verify its handoff receipt."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, required=True, help="Original project/worktree directory")
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    args = parser.parse_args()

    cwd = args.cwd.resolve(strict=True)
    prompt_path = args.prompt_file.resolve(strict=True)
    handoff_path = args.handoff.resolve(strict=True)
    receipt_path = args.receipt.resolve()
    if not cwd.is_dir():
        parser.error("--cwd must be a directory")
    if not prompt_path.is_file() or not handoff_path.is_file():
        parser.error("prompt and handoff must be files")
    private_dir = cwd / ".codex-handoff"
    if not (prompt_path.is_relative_to(private_dir) and handoff_path.is_relative_to(private_dir)
            and receipt_path.is_relative_to(private_dir)):
        parser.error("prompt, handoff and receipt must be under <cwd>/.codex-handoff")
    if receipt_path.exists():
        parser.error("receipt already exists; inspect it before retrying")

    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        parser.error("prompt is empty")
    command = ["codex", "exec", "-C", str(cwd), "-s", "workspace-write",
               "--json", "--skip-git-repo-check", "-"]
    try:
        result = subprocess.run(command, input=prompt, text=True, capture_output=True,
                                cwd=cwd, check=False, timeout=300)
    except FileNotFoundError:
        print(json.dumps({"ok": False, "error": "codex CLI not found"}, ensure_ascii=False))
        return 2
    except subprocess.TimeoutExpired:
        print(json.dumps({"ok": False, "error": "receiver timed out after 300 seconds",
                          "receipt": str(receipt_path)}, ensure_ascii=False))
        return 1

    thread_id = None
    turn_completed = False
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            turn_completed = True

    receipt_ok = False
    if receipt_path.is_file():
        receipt = receipt_path.read_text(encoding="utf-8")
        receipt_ok = str(handoff_path) in receipt and "接收完成，等待用户指令" in receipt
    ok = result.returncode == 0 and turn_completed and receipt_ok
    output = {"ok": ok, "thread_id": thread_id, "receipt": str(receipt_path),
              "exit_code": result.returncode, "turn_completed": turn_completed,
              "receipt_verified": receipt_ok}
    if not ok:
        output["error"] = "Receiver did not complete; source chat and handoff must be retained"
        output["stderr_tail"] = result.stderr[-1200:]
    print(json.dumps(output, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
