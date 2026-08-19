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


def _process_artifact_roots(project: Path) -> tuple[str, ...]:
    config = read_json(project / STATE_DIR / "config.json", {}) or {}
    roots = config.get("process_artifact_roots")
    if not isinstance(roots, list) or not roots:
        raise ValueError(".johnny/config.json process_artifact_roots is missing or invalid")
    normalized: list[str] = []
    for root in roots:
        if not isinstance(root, str):
            raise ValueError(".johnny/config.json process_artifact_roots is missing or invalid")
        value = _normalize_relative_path(root.strip())
        if not value or value == "." or value.startswith("../") or value.startswith("/"):
            raise ValueError(".johnny/config.json process_artifact_roots is missing or invalid")
        normalized.append(value)
    return tuple(normalized)


def _normalize_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _is_process_artifact(path: str, roots: tuple[str, ...]) -> bool:
    normalized = _normalize_relative_path(path)
    return any(normalized == root or normalized.startswith(root + "/") for root in roots)


def _blocking_tracked_dirty_paths(project: Path) -> list[str]:
    """Return tracked dirty paths outside configured process artifact roots.

    Use NUL-delimited porcelain so path names are unquoted. Keep stdout raw:
    porcelain status columns may legitimately begin with a space for an unstaged
    modification (for example, `` M src/feature.py``).
    """
    roots = _process_artifact_roots(project)
    result = _git_result(project, "status", "--porcelain=v1", "-z", "--untracked-files=no")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "could not inspect working tree")
    raw_stdout = result.stdout
    if not raw_stdout:
        return []

    records = raw_stdout.split("\0")
    blockers: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise RuntimeError("could not parse tracked working-tree status")
        status, path = record[:2], record[3:]
        paths = [path]
        if "R" in status or "C" in status:
            if index >= len(records) or not records[index]:
                raise RuntimeError("could not parse tracked rename or copy status")
            paths.append(records[index])
            index += 1
        blockers.extend(path for path in paths if not _is_process_artifact(path, roots))
    return blockers


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
    state = read_json(project / STATE_DIR / "state.json", {}) or {}
    phase = int(state.get("phase", 0))
    if phase not in {3, 4}:
        parser.error("controlled Milestone merge is only valid during Phase 3 or Phase 4")
    source = run_git(project, "branch", "--show-current")
    expected_source = f"codex/milestone-{ticket}" if phase == 3 else f"codex/phase4-{ticket.removeprefix('P4-')}"
    if source != expected_source:
        parser.error("source Milestone branch ID must match --ticket")
    if target != "main" and not target.startswith("feature/"):
        parser.error("merge target must be main or feature/*")
    try:
        blocking_dirty_paths = _blocking_tracked_dirty_paths(project)
    except (RuntimeError, ValueError) as error:
        parser.error(str(error))
    if blocking_dirty_paths:
        parser.error(
            "tracked working tree has non-process changes blocking controlled merge: "
            + ", ".join(blocking_dirty_paths)
        )

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
        "phase": phase,
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
