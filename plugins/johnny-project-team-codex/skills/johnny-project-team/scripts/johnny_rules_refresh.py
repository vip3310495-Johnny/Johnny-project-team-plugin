"""Validate context routing inputs and write one auditable session manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import STATE_DIR, atomic_json, git_root, read_json
from johnny_ecc_rules import select_rules


def refresh(project_arg: Path, paths: list[str] | None = None) -> dict:
    """Refresh the auditable ECC selection and return the session context."""
    project = git_root(project_arg)
    manifest_path = project / ".agents" / "context-manifest.json"
    manifest = read_json(manifest_path, {})
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise RuntimeError(".agents/context-manifest.json is missing or unsupported")
    required = manifest.get("required", [])
    missing = [value for value in required if not (project / value).exists()]
    if missing:
        raise RuntimeError("missing required context files: " + ", ".join(missing))
    state = read_json(project / ".johnny" / "state.json", {})
    ecc_rules = select_rules(project, paths)
    atomic_json(project / STATE_DIR / "ecc-selection.json", ecc_rules)
    context = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_version": manifest.get("rules_version"),
        "phase": state.get("phase"),
        "required": required,
        "routes": manifest.get("routes", {}),
        "ecc_rules": ecc_rules,
    }
    atomic_json(project / ".agents" / "session-context.json", context)
    return context


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--paths", nargs="*")
    args = parser.parse_args()
    try:
        context = refresh(args.project, args.paths)
    except RuntimeError as error:
        parser.error(str(error))
    print(
        "Johnny session context refreshed and validated; "
        f"ECC selection {context['ecc_rules']['selection_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
