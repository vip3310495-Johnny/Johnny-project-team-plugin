"""Fast, read-only PreToolUse protection for Johnny protected branches."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from johnny_context_resolution import resolve_project


def deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


def git(project: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    payload = json.load(sys.stdin)
    project = resolve_project(Path(payload.get("cwd", "."))).project
    if not project:
        return 0
    try:
        enabled = json.loads(
            (project / ".johnny" / "enabled.json").read_text(encoding="utf-8")
        )
        state = json.loads((project / ".johnny" / "state.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return 0
    if enabled.get("enabled") is not True or int(state.get("phase", 0)) < 3:
        return 0
    branch = git(project, "branch", "--show-current")
    protected = branch == "main" or branch.startswith("feature/")
    if not protected:
        return 0
    tool_name = payload.get("tool_name")
    command = str((payload.get("tool_input") or {}).get("command", ""))
    if tool_name == "apply_patch":
        return deny(
            f"Johnny blocks direct edits on protected branch {branch!r}; "
            "switch to codex/milestone-Mxx."
        )
    if tool_name == "Bash" and re.search(r"\bgit\s+(commit|push)\b", command):
        return deny(
            f"Johnny blocks direct git commit/push on protected branch {branch!r}; "
            "use the controlled Milestone and PM merge workflow."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
