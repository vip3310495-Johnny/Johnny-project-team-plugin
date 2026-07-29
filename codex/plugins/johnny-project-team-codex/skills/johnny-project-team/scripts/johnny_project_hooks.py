"""Enable, inspect, or disable repository-local Johnny physical Git gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import (
    STATE_DIR,
    append_jsonl,
    atomic_json,
    git_root,
    is_enabled,
    read_json,
    run_git,
)

CONFIG_SCHEMA_VERSION = 3
PROCESS_ROOTS = (
    ".johnny/",
    ".agents/",
    ".codex/",
    "PM/",
    "Architect/",
    "TDD_DQA/",
    "SDD_DQA/",
    "Claude DQA/",
    "Logs/",
)
ROOT_NON_PRODUCT_FILES = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "JOHNNY_PROJECT_RULES.md",
    "LICENSE",
    "LICENSE.md",
    "README.md",
    "SECURITY.md",
}
NON_PRODUCT_ROOTS = (
    ".github/",
    "docs/",
)
LEGACY_MANAGED_AGENT_BLOBS = {
    "johnny-pm.toml": {"a3d3b70d1aee79dc53d2bd4ad01e956ce04d487f"},
    "johnny-engineer.toml": {"30e2dff5b4d20195a4c749a1914d438170c316d9"},
    "johnny-tdd-dqa.toml": {"13fd290f1c5f9ced1bb0aa9f0d638f39d27afbfc"},
    "johnny-sdd-dqa.toml": {"483ebd23d45beb1495dcd31b2d52f5d8936dda25"},
    "johnny-dqa.toml": {"109a69e6a8b7c9c35381f68987b5a8c9c53d0172"},
    "johnny-te.toml": {"10751c0ad22843edbf895668d4e06cbda77a6560"},
}


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


def install_git_hooks(project: Path, prior: str | None) -> None:
    """Regenerate local hooks so upgrades never retain a stale plugin path."""
    hooks_dir = project / STATE_DIR / "git-hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    if prior:
        prior_hooks_dir = Path(prior)
        if not prior_hooks_dir.is_absolute():
            prior_hooks_dir = project / prior_hooks_dir
    else:
        git_hooks = run_git(project, "rev-parse", "--git-path", "hooks")
        prior_hooks_dir = Path(git_hooks)
        if not prior_hooks_dir.is_absolute():
            prior_hooks_dir = project / prior_hooks_dir
    guard = Path(__file__).with_name("johnny_guard.py")
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


def canonical(path: Path) -> Path:
    return path.resolve()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_blob_oid(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def install_agent_templates(project: Path, *, preserve_existing: bool = False) -> None:
    source_dir = Path(__file__).resolve().parents[1] / "assets" / "agents"
    target_dir = project / ".codex" / "agents"
    target_dir.mkdir(parents=True, exist_ok=True)
    managed_path = target_dir / ".johnny-managed.json"
    managed = read_json(managed_path, {}) or {}
    if not isinstance(managed, dict):
        managed = {}
    for source in source_dir.glob("*.toml"):
        target = target_dir / source.name
        content = source.read_bytes()
        source_hash = sha256_bytes(content)
        if target.exists():
            current = target.read_bytes()
            if current == content:
                managed[source.name] = source_hash
                continue
            if not preserve_existing:
                raise RuntimeError(f"refusing to overwrite existing custom agent: {target}")
            current_hash = sha256_bytes(current)
            known_managed = current_hash == managed.get(source.name)
            known_legacy = git_blob_oid(current) in LEGACY_MANAGED_AGENT_BLOBS.get(
                source.name, set()
            )
            if known_managed or known_legacy:
                target.write_bytes(content)
                managed[source.name] = source_hash
            else:
                managed.pop(source.name, None)
        else:
            target.write_bytes(content)
            managed[source.name] = source_hash
    atomic_json(managed_path, managed)


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
    else:
        content = rules_target.read_text(encoding="utf-8")
        marker = "<!-- johnny-project-contract-v3 -->"
        if marker not in content:
            addition = (
                "\n\n"
                f"{marker}\n"
                "For every active ticket, run `johnny_rules_refresh.py --paths "
                "<active-product-paths>` and require Engineer, DQA, and external "
                "Claude review evidence to use the resulting "
                "`.johnny/ecc-selection.json` hash.\n"
                "Advance to Phase 1, 3, and 5 only with schema-valid `--evidence`; "
                "Phase 3 evidence must contain an approved AVAILABLE Model Matrix. "
                "After `johnny_milestone_gate.py`, merge only with "
                "`johnny_pm_merge.py`.\n"
                "所有產品交付檔案都放在 `src/`；Phase 3 commit 只能包含 "
                "`src/**`。Engineer 負責 `src/tests/` 永久測試。DQA 工具留在 "
                "對應的 `TDD_DQA/tool/`、`SDD_DQA/tool/` 或 "
                "`Claude DQA/tool/` 流程工作區且不得 stage。TE 維持唯讀。\n"
            )
            rules_target.write_text(content.rstrip() + addition, encoding="utf-8", newline="\n")
    manifest_source = templates / "context-manifest.json"
    manifest_target = project / ".agents" / "context-manifest.json"
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_target.exists():
        manifest_target.write_text(
            manifest_source.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
    else:
        current = read_json(manifest_target, {}) or {}
        template = read_json(manifest_source, {}) or {}
        if not isinstance(current, dict):
            raise RuntimeError(f"unsupported context manifest: {manifest_target}")
        current.setdefault("required", template.get("required", []))
        current.setdefault("routes", {})
        for key, value in template.get("routes", {}).items():
            current["routes"].setdefault(key, value)
        current["rules_version"] = template.get("rules_version")
        current["ecc_rules"] = template.get("ecc_rules", {})
        current["ecc_selection"] = ".johnny/ecc-selection.json"
        current["product_layout"] = template.get("product_layout", {})
        atomic_json(manifest_target, current)


def migrate_config(config: dict) -> dict:
    """Upgrade managed contracts while preserving unrelated project choices."""
    config["schema_version"] = CONFIG_SCHEMA_VERSION
    config["product_root"] = "src/"
    config["allowed_code_roots"] = ["src/"]
    config["product_paths"] = ["src/"]
    config["phase3_commit_roots"] = ["src/"]
    config["process_artifact_roots"] = [
        ".johnny/",
        ".agents/",
        ".codex/",
        "JOHNNY_PROJECT_RULES.md",
        "PM/",
        "Architect/",
        "TDD_DQA/",
        "SDD_DQA/",
        "Claude DQA/",
        "Logs/",
    ]
    config["dqa_workspaces"] = {
        "tdd": {
            "tool": "TDD_DQA/tool/",
            "report": "TDD_DQA/",
            "evidence": "TDD_DQA/evidence/",
        },
        "sdd": {
            "tool": "SDD_DQA/tool/",
            "report": "SDD_DQA/",
            "evidence": "SDD_DQA/evidence/",
        },
        "claude": {
            "tool": "Claude DQA/tool/",
            "report": "Claude DQA/",
            "evidence": "Claude DQA/evidence/",
        },
    }
    config.setdefault("dqa_escalation", {})
    config["dqa_escalation"]["max_rejections_per_role_per_milestone"] = 5
    config["dqa_escalation"]["count_scope"] = "milestone-and-dqa-role"
    config["dqa_escalation"]["action"] = "freeze-and-escalate-to-ceo"
    config.setdefault("phase_prerequisites", {})
    config["phase_prerequisites"].update(
        {
            "schema_version": 1,
            "required_for_transitions": [1, 3, 5],
            "model_matrix_required_for_phase3": True,
        }
    )
    config.setdefault("ecc_rules", {})
    config["ecc_rules"].update(
        {
            "enabled": True,
            "selector": "johnny_ecc_rules.py",
            "selection_schema_version": 2,
            "selection_manifest": ".johnny/ecc-selection.json",
            "common_always": True,
            "require_every_selected_file": True,
        }
    )
    return config


def validate_migration_layout(project: Path) -> None:
    """若仍有 tracked 產品檔案位於 src 外，拒絕嚴格的 v3 migration。"""
    tracked = run_git(project, "ls-files").splitlines()
    misplaced = []
    for raw in tracked:
        value = raw.strip().replace("\\", "/")
        if (
            not value
            or value.startswith("src/")
            or value.startswith(PROCESS_ROOTS)
            or value.startswith(NON_PRODUCT_ROOTS)
            or value in ROOT_NON_PRODUCT_FILES
        ):
            continue
        misplaced.append(value)
    if misplaced:
        preview = ", ".join(misplaced[:8])
        if len(misplaced) > 8:
            preview += f", ... (+{len(misplaced) - 8})"
        raise RuntimeError(
            "schema v3 migration 前，請將不屬於明確流程／根目錄 metadata 的 "
            f"tracked 產品交付檔案移入 src/：{preview}"
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
    config = migrate_config(config)
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
            "format": 2,
        },
    )

    install_git_hooks(project, prior)
    print(f"Johnny gates enabled only for: {project}")


def migrate(project_arg: Path) -> None:
    project = git_root(project_arg)
    if not is_enabled(project):
        raise RuntimeError("enable the project before running migration")
    config_path = project / STATE_DIR / "config.json"
    config = read_json(config_path, {}) or {}
    before = int(config.get("schema_version", 1))
    if before < 3:
        validate_migration_layout(project)
    install_agent_templates(project, preserve_existing=True)
    install_project_rules(project)
    atomic_json(config_path, migrate_config(config))
    marker_path = project / STATE_DIR / "enabled.json"
    marker = read_json(marker_path, {}) or {}
    marker["format"] = 2
    marker["migrated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(marker_path, marker)
    prior = read_json(project / STATE_DIR / "previous-hooks-path.json", {}) or {}
    install_git_hooks(project, prior.get("value"))
    append_jsonl(
        project / STATE_DIR / "migration-history.jsonl",
        {
            "event": "johnny-project-migration",
            "from_schema": before,
            "to_schema": CONFIG_SCHEMA_VERSION,
            "at": marker["migrated_at"],
        },
    )
    print(f"Johnny project migrated: schema {before} -> {CONFIG_SCHEMA_VERSION}")


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
    parser.add_argument("action", choices=("enable", "disable", "status", "migrate"))
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    {
        "enable": enable,
        "disable": disable,
        "status": status,
        "migrate": migrate,
    }[args.action](args.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
