"""Give Johnny subagents the active task routing without copying full project history."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RULE_SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "johnny-project-team"
    / "scripts"
)
sys.path.insert(0, str(RULE_SCRIPT_DIR))

from johnny_ecc_rules import format_context, select_rules


def main() -> int:
    payload = json.load(sys.stdin)
    cwd = Path(payload.get("cwd", "."))
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return 0
    project = Path(result.stdout.strip()).resolve()
    try:
        enabled = json.loads(
            (project / ".johnny" / "enabled.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (project / ".agents" / "context-manifest.json").read_text(encoding="utf-8")
        )
        state = json.loads(
            (project / ".johnny" / "state.json").read_text(encoding="utf-8")
        )
        dqa_path = project / ".johnny" / "dqa-status.json"
        dqa = (
            json.loads(dqa_path.read_text(encoding="utf-8"))
            if dqa_path.is_file()
            else {}
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        return 0
    if enabled.get("enabled") is not True:
        return 0
    agent_type = payload.get("agent_type", "unknown")
    policy = (state.get("execution_policy") or {}).get("mode", "not-selected")
    escalation = dqa.get("escalation") or {}
    freeze = (
        f" Milestone {dqa.get('ticket')} is frozen for CEO resolution."
        if escalation.get("active", False)
        else ""
    )
    context = (
        f"Johnny subagent profile: {agent_type}. Read only the role route and active "
        f"Task Context Pack declared by context manifest v{manifest.get('schema_version')}. "
        f"Execution policy: {policy}.{freeze} "
        "Do not infer Phase, ticket, scope, or approval from conversation memory. "
        "Return evidence to the parent role; do not advance Phase or write DQA verdicts."
    )
    try:
        context += " " + format_context(select_rules(project))
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        context += f" ECC rule routing unavailable: {error}."
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
