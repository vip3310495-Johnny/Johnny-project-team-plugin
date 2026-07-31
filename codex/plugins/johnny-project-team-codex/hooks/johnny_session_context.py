"""Return concise, read-only Johnny context at supported SessionStart events."""

from __future__ import annotations

import json
import sys
from pathlib import Path

RULE_SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "johnny-project-team"
    / "scripts"
)
sys.path.insert(0, str(RULE_SCRIPT_DIR))

from johnny_ecc_rules import format_context, load_or_select_rules
from johnny_context_resolution import resolve_project


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def main() -> int:
    payload = json.load(sys.stdin)
    resolution = resolve_project(Path(payload.get("cwd", ".")))
    project = resolution.project
    if not project:
        if resolution.diagnostic:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": resolution.diagnostic,
                        }
                    },
                    ensure_ascii=False,
                )
            )
        return 0
    enabled = read_json(project / ".johnny" / "enabled.json")
    if enabled.get("enabled") is not True or enabled.get("scope") != str(project):
        return 0
    state = read_json(project / ".johnny" / "state.json")
    dqa = read_json(project / ".johnny" / "dqa-status.json")
    manifest = read_json(project / ".agents" / "context-manifest.json")
    rules = project / "JOHNNY_PROJECT_RULES.md"
    missing = [
        value
        for value in ("JOHNNY_PROJECT_RULES.md", ".agents/context-manifest.json")
        if not (project / value).is_file()
    ]
    policy = (state.get("execution_policy") or {}).get("mode", "not-selected")
    escalation = dqa.get("escalation") or {}
    escalation_text = (
        f"CEO escalation is OPEN for {dqa.get('ticket')} "
        f"{escalation.get('role')} DQA after "
        f"{escalation.get('rejection_count')} rejections. "
        if escalation.get("active", False)
        else "No DQA rejection escalation is open. "
    )
    context = (
        f"Johnny is enabled for {project}. Current Phase: {state.get('phase', 'unknown')}; "
        f"Phase 3 execution policy: {policy}; "
        f"context manifest schema: {manifest.get('schema_version', 'missing')}. "
        f"{escalation_text}"
        "Before acting, run johnny_project_hooks.py status and read the active Phase, "
        "role, and Task Context Pack routes. "
    )
    if rules.is_file():
        context += rules.read_text(encoding="utf-8")[:4000]
    try:
        context += " " + format_context(load_or_select_rules(project))
    except (OSError, RuntimeError) as error:
        context += f" ECC rule routing unavailable: {error}."
    if missing:
        context += " Missing required context files: " + ", ".join(missing)
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
