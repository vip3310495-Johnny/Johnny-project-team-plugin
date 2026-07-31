"""Re-run the complete, auditable Johnny project initialization sequence."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HOOKS_DIR = SCRIPT_DIR.parents[2] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from johnny_context_resolution import resolve_project
from johnny_common import STATE_DIR, read_json
from johnny_project_hooks import migrate
from johnny_rules_refresh import refresh


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and refresh all managed Johnny initialization context."
    )
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--paths", nargs="*", help="Active product paths for ECC routing")
    args = parser.parse_args()

    resolution = resolve_project(args.project)
    if not resolution.project:
        parser.error(resolution.diagnostic or "no enabled Johnny repository was found")
    project = resolution.project
    enabled = read_json(project / STATE_DIR / "enabled.json", {}) or {}
    if enabled.get("enabled") is not True or enabled.get("scope") != str(project):
        parser.error(".johnny/enabled.json does not enable this exact repository")

    # Keep this command's stdout machine-readable even though migrate has a
    # human-facing success message when invoked directly.
    with contextlib.redirect_stdout(io.StringIO()):
        migrate(project)
    context = refresh(project, args.paths)
    state = read_json(project / STATE_DIR / "state.json", {}) or {}
    config = read_json(project / STATE_DIR / "config.json", {}) or {}
    agents = sorted(
        path.name for path in (project / ".codex" / "agents").glob("johnny-*.toml")
    )
    print(
        json.dumps(
            {
                "project": str(project),
                "phase": state.get("phase"),
                "approval_state": state.get("approval") or state.get("execution_policy"),
                "config_schema": config.get("schema_version"),
                "required_files": context["required"],
                "routes": context["routes"],
                "managed_agents": agents,
                "ecc_selection_sha256": context["ecc_rules"]["selection_sha256"],
                "ecc_rule_files": context["ecc_rules"]["rule_files"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
