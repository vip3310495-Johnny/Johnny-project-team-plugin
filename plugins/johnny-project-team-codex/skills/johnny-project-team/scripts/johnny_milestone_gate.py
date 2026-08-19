"""Record a tree-bound Milestone approval under the Phase 2 execution policy."""

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
    run_git,
    state_lock,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument(
        "--approval",
        help="explicit CEO approval; required only under SUPERVISED policy",
    )
    args = parser.parse_args()
    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    ticket = args.ticket.strip()
    if not ticket:
        parser.error("ticket must be non-empty")

    with state_lock(project):
        state = read_json(project / STATE_DIR / "state.json", {}) or {}
        policy = (state.get("execution_policy") or {}).get("mode")
        if policy not in ("SUPERVISED", "AUTONOMOUS"):
            parser.error("Phase 3 execution policy has not been selected")
        phase = int(state.get("phase", 0))
        if phase not in {3, 4}:
            parser.error("Milestone approval is only valid during Phase 3 or Phase 4")
        if phase == 4 and not ticket.startswith("P4-M"):
            parser.error("Phase 4 Milestone ticket must use P4-Mxx")
        if phase == 4 and (state.get("phase4_execution") or {}).get("status") != "APPROVED":
            parser.error("Phase 4 construction has not received CEO approval")
        dqa = read_json(project / STATE_DIR / "dqa-status.json", {}) or {}
        if dqa.get("schema_version") != 2 or dqa.get("scope") != "ticket":
            parser.error("current ticket DQA evidence is missing or invalid")
        if dqa.get("ticket") != ticket:
            parser.error("current DQA evidence belongs to a different ticket")
        escalation = dqa.get("escalation") or {}
        if escalation.get("active", False):
            parser.error("Milestone is frozen pending CEO conflict resolution")
        missing = [
            role
            for role in dqa.get("workflow", ["tdd", "sdd"])
            if role in dqa.get("required_roles", []) or dqa.get("results", {}).get(role) != "PASS"
        ]
        if missing:
            parser.error("required DQA did not pass: " + ", ".join(dict.fromkeys(missing)))
        head_tree = run_git(project, "rev-parse", "HEAD^{tree}", check=False)
        if not head_tree or head_tree != dqa.get("commit_tree"):
            parser.error(
                "HEAD tree does not match the DQA-approved commit tree; "
                "commit the approved staged tree before recording Milestone approval"
            )

        if policy == "SUPERVISED":
            approval = (args.approval or "").strip()
            if not approval:
                parser.error("SUPERVISED policy requires explicit CEO approval")
            approval_source = "milestone-ceo-approval"
        else:
            if args.approval:
                parser.error(
                    "AUTONOMOUS policy uses the Phase 2 delegation; "
                    "do not manufacture a new CEO approval"
                )
            approval = state["execution_policy"]["approval"]
            approval_source = "phase2-ceo-delegation"

        record = {
            "schema_version": 1,
            "phase": phase,
            "ticket": ticket,
            "status": "APPROVED",
            "execution_policy": policy,
            "approval_source": approval_source,
            "approval": approval,
            "approved_at": utc_now(),
            "source_commit": run_git(project, "rev-parse", "HEAD"),
            "commit_tree": head_tree,
            "subject_tree": dqa.get("subject_tree"),
            "dqa_review_cycle": dqa.get("review_cycle"),
        }
        atomic_json(project / STATE_DIR / "milestone-status.json", record)
        append_jsonl(
            project / STATE_DIR / "milestone-history.jsonl",
            {"event": "milestone-approved", **record},
        )
    print(
        f"{ticket} approved under {policy} policy "
        f"({approval_source}); dependent Milestones may unlock"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
