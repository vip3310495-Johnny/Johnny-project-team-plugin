"""Atomically advance the Johnny phase after explicit user approval."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import (
    STATE_DIR,
    append_jsonl,
    atomic_json,
    git_root,
    is_enabled,
    read_json,
    state_lock,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--to-phase", type=int, required=True, choices=range(0, 7))
    parser.add_argument("--approval", required=True)
    parser.add_argument(
        "--execution-policy",
        choices=("SUPERVISED", "AUTONOMOUS"),
        help="required when advancing from Phase 2 to Phase 3",
    )
    args = parser.parse_args()
    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    if not args.approval.strip():
        parser.error("explicit user approval text is required")

    # Only the short state transaction is locked. No external process runs here.
    with state_lock(project):
        path = project / STATE_DIR / "state.json"
        state = read_json(path, {"phase": 0, "revision": 0})
        current = int(state.get("phase", 0))
        if args.to_phase != current + 1:
            parser.error(f"only one-step forward transitions are allowed ({current} -> {current + 1})")
        if args.to_phase == 3 and args.execution_policy is None:
            parser.error(
                "Phase 2 completion requires --execution-policy "
                "SUPERVISED or AUTONOMOUS"
            )
        if args.to_phase != 3 and args.execution_policy is not None:
            parser.error("--execution-policy is only valid when advancing to Phase 3")
        state.update(
            {
                "phase": args.to_phase,
                "revision": int(state.get("revision", 0)) + 1,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "approval": args.approval.strip(),
            }
        )
        if args.to_phase == 3:
            state["execution_policy"] = {
                "mode": args.execution_policy,
                "delegated_by": "CEO",
                "delegated_at": state["approved_at"],
                "approval": args.approval.strip(),
            }
        atomic_json(path, state)
        append_jsonl(
            project / STATE_DIR / "approval-history.jsonl",
            {
                "event": "phase-transition",
                "from_phase": current,
                "to_phase": args.to_phase,
                "approval": args.approval.strip(),
                "approved_at": state["approved_at"],
                "revision": state["revision"],
                **(
                    {"execution_policy": args.execution_policy}
                    if args.to_phase == 3
                    else {}
                ),
            },
        )
    print(f"Johnny phase advanced: {current} -> {args.to_phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
