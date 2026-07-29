"""Enable, inspect, or disable repository-local Johnny physical Git gates."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import STATE_DIR, atomic_json, git_root, is_enabled, read_json, run_git


def hook_text(guard: Path, event: str, prior_hook: Path | None) -> str:
    python = Path(sys.executable).resolve().as_posix()
    guard_path = guard.resolve().as_posix()
    lines = ["#!/bin/sh\n"]
    if prior_hook and prior_hook.is_file():
        prior_path = prior_hook.resolve().as_posix()
        lines.append(f'if [ -x "{prior_path}" ]; then\n')
        lines.append(f'  "{prior_path}" "$@" || exit $?\n')
        lines.append("fi\n")
    lines.append(
        f'exec "{python}" "{guard_path}" --project '
        '"$(git rev-parse --show-toplevel)" '
        f'--event "{event}"\n'
    )
    return "".join(lines)


def canonical(path: Path) -> Path:
    return path.resolve()


def install_agent_templates(project: Path) -> None:
    source_dir = Path(__file__).resolve().parents[1] / "assets" / "agents"
    target_dir = project / ".codex" / "agents"
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in source_dir.glob("*.toml"):
        target = target_dir / source.name
        content = source.read_text(encoding="utf-8")
        if target.exists() and target.read_text(encoding="utf-8") != content:
            raise RuntimeError(f"refusing to overwrite existing custom agent: {target}")
        if not target.exists():
            target.write_text(content, encoding="utf-8", newline="\n")


def install_project_rules(project: Path) -> None:
    templates = Path(__file__).resolve().parents[1] / "assets" / "templates"
    rules_source = templates / "JOHNNY_PROJECT_RULES.md"
    rules_target = project / "JOHNNY_PROJECT_RULES.md"
    if not rules_target.exists():
        rules_target.write_text(
            rules_source.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
    manifest_source = templates / "context-manifest.json"
    manifest_target = project / ".agents" / "context-manifest.json"
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_target.exists():
        manifest_target.write_text(
            manifest_source.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )


def enable(project_arg: Path) -> None:
    project = git_root(project_arg)
    if run_git(project, "rev-parse", "--verify", "HEAD", check=False) == "":
        raise RuntimeError(
            "create a clean initial commit before enabling Johnny; "
            "the initial commit must not contain .johnny gate state"
        )
    install_agent_templates(project)
    install_project_rules(project)
    state_dir = project / STATE_DIR
    hooks_dir = state_dir / "git-hooks"
    state_dir.mkdir(exist_ok=True)
    hooks_dir.mkdir(exist_ok=True)

    prior = run_git(project, "config", "--local", "--get", "core.hooksPath", check=False)
    own_hooks = canonical(hooks_dir)
    if prior:
        candidate = Path(prior)
        if not candidate.is_absolute():
            candidate = project / candidate
        if canonical(candidate) == own_hooks:
            prior = ""
    prior_file = state_dir / "previous-hooks-path.json"
    if not prior_file.exists():
        atomic_json(prior_file, {"value": prior or None})

    config_path = state_dir / "config.json"
    config = read_json(config_path, {}) or {}
    config.setdefault("claude_dqa", {})
    config["claude_dqa"].setdefault("enabled", False)
    config["claude_dqa"].setdefault("required", False)
    config["claude_dqa"].setdefault("manual_allowed", True)
    config.setdefault("allowed_code_roots", ["src/", "tests/", "TDD_DQA/", "SDD_DQA/"])
    config.setdefault(
        "product_paths",
        [
            "src/",
            "tests/",
            "app/",
            "lib/",
            "ui/",
            "config/",
            "package.json",
            "pyproject.toml",
        ],
    )
    config.setdefault(
        "evidence_paths",
        ["TDD_DQA/", "SDD_DQA/", "Claude DQA/", "PM/", "Architect/"],
    )
    config.setdefault("dqa_required_from_phase", 3)
    config.setdefault("dqa_required_phases", [3, 4])
    config.setdefault("te_orchestration", {})
    config["te_orchestration"].setdefault("enabled", True)
    config["te_orchestration"].setdefault("max_concurrent_per_dqa", 2)
    config["te_orchestration"].setdefault("fallback_session_total_slots", 4)
    config.setdefault("scope_contract", {})
    config["scope_contract"].setdefault(
        "levels", ["FIXED", "CONTROLLED", "DISCRETIONARY"]
    )
    config["scope_contract"].setdefault("classification_owner", "PM")
    config["scope_contract"].setdefault("classification_challenges_per_item", 1)
    config["scope_contract"].setdefault("dqa_intervenes_in_phase3", True)
    config["scope_contract"].setdefault("controlled_requires_approval", False)
    config["scope_contract"].setdefault("phase4_tests_compatibility", True)
    config.setdefault("ticket_flow", {})
    config["ticket_flow"].setdefault("style", "tracer-bullet")
    config["ticket_flow"].setdefault("milestone_ticket_cardinality", "one-to-one")
    config["ticket_flow"].setdefault("max_active_phase3_tickets", 1)
    config["ticket_flow"].setdefault("requires_dependency_edges", True)
    config["ticket_flow"].setdefault("required_dqa_order", ["tdd", "sdd"])
    config["ticket_flow"].setdefault("claude_dqa_mode", "manual")
    config["ticket_flow"]["execution_policy_choices"] = [
        "SUPERVISED",
        "AUTONOMOUS",
    ]
    config["ticket_flow"]["execution_policy_selected_at_phase"] = 2
    config["ticket_flow"]["requires_user_review_each_ticket"] = "by-policy"
    config["ticket_flow"]["unlock_next_after_approval"] = "by-policy"
    config["ticket_flow"].pop("unlock_next_after_user_approval", None)
    config.setdefault("dqa_escalation", {})
    config["dqa_escalation"].setdefault(
        "max_rejections_per_role_per_milestone", 5
    )
    config["dqa_escalation"].setdefault("count_scope", "milestone-and-dqa-role")
    config["dqa_escalation"].setdefault("action", "freeze-and-escalate-to-ceo")
    atomic_json(config_path, config)

    atomic_json(
        state_dir / "state.json",
        read_json(state_dir / "state.json", {"phase": 0, "revision": 0}),
    )
    atomic_json(
        state_dir / "enabled.json",
        {
            "enabled": True,
            "scope": str(project),
            "enabled_at": datetime.now(timezone.utc).isoformat(),
            "format": 1,
        },
    )

    guard = Path(__file__).with_name("johnny_guard.py")
    if prior:
        prior_hooks_dir = Path(prior)
        if not prior_hooks_dir.is_absolute():
            prior_hooks_dir = project / prior_hooks_dir
    else:
        git_hooks = run_git(project, "rev-parse", "--git-path", "hooks")
        prior_hooks_dir = Path(git_hooks)
        if not prior_hooks_dir.is_absolute():
            prior_hooks_dir = project / prior_hooks_dir
    for event in ("pre-commit", "pre-push"):
        hook = hooks_dir / event
        prior_hook = prior_hooks_dir / event
        if canonical(prior_hook) == canonical(hook):
            prior_hook = None
        hook.write_text(
            hook_text(guard, event, prior_hook), encoding="utf-8", newline="\n"
        )
        hook.chmod(hook.stat().st_mode | 0o111)

    run_git(project, "config", "--local", "core.hooksPath", f"{STATE_DIR}/git-hooks")
    print(f"Johnny gates enabled only for: {project}")


def disable(project_arg: Path) -> None:
    project = git_root(project_arg)
    prior = read_json(project / STATE_DIR / "previous-hooks-path.json", {})
    value = prior.get("value") if prior else None
    if value:
        run_git(project, "config", "--local", "core.hooksPath", value)
    else:
        run_git(project, "config", "--local", "--unset", "core.hooksPath", check=False)
    marker = read_json(project / STATE_DIR / "enabled.json", {}) or {}
    marker["enabled"] = False
    marker["disabled_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(project / STATE_DIR / "enabled.json", marker)
    print(f"Johnny gates disabled for: {project}; evidence preserved")


def status(project_arg: Path) -> None:
    project = git_root(project_arg)
    data = {
        "project": str(project),
        "enabled": is_enabled(project),
        "hooksPath": run_git(
            project, "config", "--local", "--get", "core.hooksPath", check=False
        )
        or None,
        "config": read_json(project / STATE_DIR / "config.json", {}),
        "state": read_json(project / STATE_DIR / "state.json", {}),
        "context_manifest": read_json(
            project / ".agents" / "context-manifest.json", {}
        ),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("enable", "disable", "status"))
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    {"enable": enable, "disable": disable, "status": status}[args.action](args.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
