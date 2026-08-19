"""Unlock Phase 4 construction after plan evidence and explicit CEO approval."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import STATE_DIR, append_jsonl, atomic_json, git_root, is_enabled, read_json, state_lock
from johnny_phase_prerequisites import validate_phase_evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--approval", required=True)
    args = parser.parse_args()
    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    if not args.approval.strip():
        parser.error("explicit CEO approval is required")
    try:
        evidence = validate_phase_evidence(4, args.evidence, project)
    except ValueError as error:
        parser.error(str(error))
    with state_lock(project):
        state_path = project / STATE_DIR / "state.json"
        state = read_json(state_path, {}) or {}
        if int(state.get("phase", 0)) != 4:
            parser.error("Phase 4 construction can be unlocked only during Phase 4 planning")
        approved_at = datetime.now(timezone.utc).isoformat()
        record = {
            "schema_version": 1,
            "status": "APPROVED",
            "approval": args.approval.strip(),
            "approved_at": approved_at,
            "plan_evidence": evidence,
        }
        state["phase4_execution"] = record
        state["revision"] = int(state.get("revision", 0)) + 1
        atomic_json(state_path, state)
        append_jsonl(project / STATE_DIR / "approval-history.jsonl", {"event": "phase4-construction-approved", **record})
    print("Phase 4 construction unlocked by CEO approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
