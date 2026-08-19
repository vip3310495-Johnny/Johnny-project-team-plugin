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

MAX_CONTEXT_CHARS = 5600
RULES_MARKER = "<!-- johnny-project-contract-v4:start -->"


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def limit_context(context: str) -> str:
    """Keep output below the host limit and make any omission explicit."""
    if len(context) <= MAX_CONTEXT_CHARS:
        return context
    warning = (
        "\n[WARNING] SessionStart context exceeded the 5600-character plugin limit. "
        "The tail was omitted; read JOHNNY_PROJECT_RULES.md, the active Task Context "
        "Pack, and the ECC routes directly before acting."
    )
    return context[: MAX_CONTEXT_CHARS - len(warning)] + warning


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
                    ensure_ascii=True,
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
    model_matrix = project / "PM" / "Planning" / "Model_Recommendation_Matrix.md"
    try:
        phase = int(state.get("phase", 0))
    except (TypeError, ValueError):
        phase = -1
    required_files = ["JOHNNY_PROJECT_RULES.md", ".agents/context-manifest.json"]
    if phase >= 1:
        required_files.append("PM/Planning/Model_Recommendation_Matrix.md")
    missing = [value for value in required_files if not (project / value).is_file()]
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
        f"Model Matrix: {'present' if model_matrix.is_file() else 'missing'}. "
        f"{escalation_text}"
        "Before acting, run johnny_project_hooks.py status and read the active Phase, "
        "role, and Task Context Pack routes. "
    )
    if not model_matrix.is_file() and phase == 0:
        context += "Model Matrix may be absent only while Phase 0 is creating it. "
    if rules.is_file():
        rules_text = rules.read_text(encoding="utf-8")
        context += rules_text
        if RULES_MARKER not in rules_text:
            context += (
                " [WARNING] JOHNNY_PROJECT_RULES.md is outdated or unmanaged; "
                "run johnny_project_hooks.py migrate before Phase work."
            )
    try:
        context += " " + format_context(load_or_select_rules(project))
    except (OSError, RuntimeError) as error:
        context += f" ECC rule routing unavailable: {error}."
    if missing:
        context += (
            " [WARNING] Missing required context files: "
            + ", ".join(missing)
            + ". Stop affected role dispatch until restored."
        )
    context = limit_context(context)
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
