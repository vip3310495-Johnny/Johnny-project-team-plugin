"""Merge one approved Milestone through the auditable PM-controlled path."""

from __future__ import annotations

import argparse
import subprocess
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


def _git_result(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--push",
        action="store_true",
        help="push the merged target to origin through this controlled command",
    )
    args = parser.parse_args()
    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    ticket = args.ticket.strip()
    if not ticket:
        parser.error("ticket must be non-empty")
    target = args.target.strip()
    source = run_git(project, "branch", "--show-current")
    if not source.startswith("codex/milestone-"):
        parser.error("controlled merge must start on codex/milestone-Mxx")
    if source != f"codex/milestone-{ticket}":
        parser.error("source Milestone branch ID must match --ticket")
    if target != "main" and not target.startswith("feature/"):
        parser.error("merge target must be main or feature/*")
    if run_git(project, "status", "--porcelain", "--untracked-files=no"):
        parser.error("tracked working tree must be clean before controlled merge")

    milestone = read_json(project / STATE_DIR / "milestone-status.json", {}) or {}
    if (
        milestone.get("status") != "APPROVED"
        or milestone.get("ticket") != ticket
        or milestone.get("source_commit") != run_git(project, "rev-parse", "HEAD")
    ):
        parser.error("Milestone approval is missing, stale, or belongs to another ticket")
    dqa = read_json(project / STATE_DIR / "dqa-status.json", {}) or {}
    if (dqa.get("escalation") or {}).get("active", False):
        parser.error("Milestone is frozen pending CEO conflict resolution")
    if run_git(project, "rev-parse", "--verify", target, check=False) == "":
        parser.error(f"merge target does not exist: {target}")
    preflight = _git_result(project, "merge-tree", "--write-tree", target, source)
    if preflight.returncode != 0:
        parser.error("controlled merge preflight found conflicts: " + preflight.stderr.strip())

    switched = _git_result(project, "switch", target)
    if switched.returncode != 0:
        parser.error(switched.stderr.strip() or f"could not switch to {target}")
    merged = _git_result(
        project,
        "merge",
        "--no-ff",
        "--no-verify",
        source,
        "-m",
        f"merge({ticket}): approved Johnny Milestone",
    )
    if merged.returncode != 0:
        parser.error(merged.stderr.strip() or "controlled merge failed")

    push_error = ""
    if args.push:
        pushed = _git_result(project, "push", "--no-verify", "origin", target)
        if pushed.returncode != 0:
            push_error = pushed.stderr.strip() or "controlled push failed"
    record = {
        "schema_version": 1,
        "ticket": ticket,
        "status": "MERGED",
        "source_branch": source,
        "source_commit": milestone["source_commit"],
        "target_branch": target,
        "merge_commit": run_git(project, "rev-parse", "HEAD"),
        "commit_tree": run_git(project, "rev-parse", "HEAD^{tree}"),
        "dqa_subject_tree": milestone.get("subject_tree"),
        "milestone_approval_source": milestone.get("approval_source"),
        "push_requested": args.push,
        "push_status": "FAILED" if push_error else ("PUSHED" if args.push else "NOT_REQUESTED"),
        "merged_at": datetime.now(timezone.utc).isoformat(),
    }
    with state_lock(project):
        atomic_json(project / STATE_DIR / "merge-status.json", record)
        append_jsonl(
            project / STATE_DIR / "merge-history.jsonl",
            {"event": "controlled-pm-merge", **record},
        )
    if push_error:
        parser.error(
            "Milestone was merged locally but controlled push failed: " + push_error
        )
    print(f"{ticket} merged from {source} to {target} through controlled PM merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
