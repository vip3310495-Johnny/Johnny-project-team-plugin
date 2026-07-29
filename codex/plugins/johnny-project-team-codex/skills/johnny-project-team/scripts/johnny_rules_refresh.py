"""Validate context routing inputs and write one auditable session manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import STATE_DIR, atomic_json, git_root, read_json
from johnny_ecc_rules import select_rules


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--paths", nargs="*")
    args = parser.parse_args()
    project = git_root(args.project)
    manifest_path = project / ".agents" / "context-manifest.json"
    manifest = read_json(manifest_path, {})
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        parser.error(".agents/context-manifest.json is missing or unsupported")
    required = manifest.get("required", [])
    missing = [value for value in required if not (project / value).exists()]
    if missing:
        parser.error("missing required context files: " + ", ".join(missing))
    state = read_json(project / ".johnny" / "state.json", {})
    ecc_rules = select_rules(project, args.paths)
    atomic_json(project / STATE_DIR / "ecc-selection.json", ecc_rules)
    atomic_json(
        project / ".agents" / "session-context.json",
        {
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "manifest_version": manifest.get("rules_version"),
            "phase": state.get("phase"),
            "required": required,
            "routes": manifest.get("routes", {}),
            "ecc_rules": ecc_rules,
        },
    )
    print(
        "Johnny session context refreshed and validated; "
        f"ECC selection {ecc_rules['selection_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
