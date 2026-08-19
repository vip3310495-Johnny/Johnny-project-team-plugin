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
from johnny_phase_prerequisites import (
    validate_phase3_completion_evidence,
    validate_phase_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--to-phase", type=int, required=True, choices=range(0, 6))
    parser.add_argument("--approval", required=True)
    parser.add_argument("--evidence", type=Path)
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
    if args.to_phase == 3 and args.execution_policy is None:
        parser.error(
            "Phase 2 completion requires --execution-policy SUPERVISED or AUTONOMOUS"
        )
    if args.to_phase == 4:
        try:
            prerequisite = validate_phase3_completion_evidence(project, args.evidence)
        except ValueError as error:
            parser.error(str(error))
    else:
        try:
            prerequisite = validate_phase_evidence(args.to_phase, args.evidence, project)
        except ValueError as error:
            parser.error(str(error))

    # Only the short state transaction is locked. No external process runs here.
    with state_lock(project):
        path = project / STATE_DIR / "state.json"
        state = read_json(path, {"phase": 0, "revision": 0})
        current = int(state.get("phase", 0))
        reentering_phase0 = current == 5 and args.to_phase == 0
        if not reentering_phase0 and args.to_phase != current + 1:
            parser.error(
                "only one-step forward transitions are allowed "
                f"({current} -> {current + 1}); the only restart transition is 5 -> 0"
            )
        if args.to_phase == 3 and args.execution_policy is None:
            parser.error(
                "Phase 2 completion requires --execution-policy "
                "SUPERVISED or AUTONOMOUS"
            )
        if args.to_phase != 3 and args.execution_policy is not None:
            parser.error("--execution-policy is only valid when advancing to Phase 3")
        if reentering_phase0:
            state.pop("execution_policy", None)
            state.pop("phase4_execution", None)
            state.pop("prerequisite_evidence", None)
            state["round"] = int(state.get("round", 1)) + 1
        state.update(
            {
                "phase": args.to_phase,
                "revision": int(state.get("revision", 0)) + 1,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "approval": args.approval.strip(),
                **({"prerequisite_evidence": prerequisite} if prerequisite else {}),
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
                "round": state.get("round", 1),
                "reentry_from_phase5": reentering_phase0,
                **({"prerequisite_evidence": prerequisite} if prerequisite else {}),
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
