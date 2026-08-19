"""Give Johnny subagents the active task routing without copying full project history."""

from __future__ import annotations

import json
import sys
import tomllib
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


ROLE_PROFILES = {
    "johnny_architect": "johnny-architect.toml",
    "johnny_engineer": "johnny-engineer.toml",
    "johnny_tdd_dqa": "johnny-tdd-dqa.toml",
    "johnny_sdd_dqa": "johnny-sdd-dqa.toml",
    "johnny_security_dqa": "johnny-security-dqa.toml",
    "johnny_log_agent": "johnny-log-agent.toml",
    "johnny_te": "johnny-te.toml",
}


def blocked_context(agent_type: str, reason: str) -> None:
    """Emit a fail-closed payload for a Johnny role with no valid profile."""
    message = (
        f"[BLOCKED_PROFILE] {agent_type} cannot begin work: {reason}. "
        "Stop immediately and ask the PM to run johnny_project_hooks.py migrate "
        "for this repository."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                    "additionalContext": message,
                }
            },
            ensure_ascii=True,
        )
    )


def load_role_profile(project: Path, agent_type: str) -> tuple[Path, str] | None:
    profile_name = ROLE_PROFILES.get(agent_type)
    if profile_name is None:
        return None
    profile_path = project / ".codex" / "agents" / profile_name
    try:
        content = profile_path.read_text(encoding="utf-8")
        parsed = tomllib.loads(content)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        blocked_context(agent_type, f"required profile is missing or unreadable: {profile_path}")
        return (Path(), "")
    if parsed.get("name") != agent_type:
        blocked_context(agent_type, f"profile name does not match: {profile_path}")
        return (Path(), "")
    return profile_path, content


def main() -> int:
    payload = json.load(sys.stdin)
    project = resolve_project(Path(payload.get("cwd", "."))).project
    if not project:
        return 0
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
    profile = load_role_profile(project, agent_type)
    if profile == (Path(), ""):
        return 0
    profile_context = ""
    if profile is not None:
        profile_path, profile_content = profile
        profile_context = (
            f" Required role profile verified and attached from {profile_path}:\n"
            f"```toml\n{profile_content}\n```\n"
        )
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
        + profile_context
    )
    try:
        context += " " + format_context(load_or_select_rules(project))
    except (OSError, RuntimeError) as error:
        context += f" ECC rule routing unavailable: {error}."
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
