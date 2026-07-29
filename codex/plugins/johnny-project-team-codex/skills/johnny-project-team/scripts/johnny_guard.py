"""Single read-only dispatcher used by the physical Git hooks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

from johnny_common import (
    STATE_DIR,
    git_root,
    is_enabled,
    read_json,
    run_git,
    staged_tree,
    subject_tree,
)


def fail(message: str) -> None:
    print(f"[Johnny gate] BLOCKED: {message}", file=sys.stderr)
    raise SystemExit(1)


def staged_paths(project: Path) -> list[str]:
    output = run_git(project, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]


def validate_scope(project: Path) -> None:
    marker = read_json(project / STATE_DIR / "enabled.json", {})
    if not marker or marker.get("scope") != str(project):
        fail("activation marker scope does not match this repository")


def validate_paths(project: Path, paths: list[str], config: dict, state: dict) -> None:
    allowed_roots = tuple(config.get("allowed_code_roots", []))
    phase = int(state.get("phase", 0))
    phase3_roots = tuple(config.get("phase3_commit_roots", ["src/"]))
    for value in paths:
        path = PurePosixPath(value)
        if ".." in path.parts or path.is_absolute():
            fail(f"unsafe staged path: {value}")
        if phase == 3 and phase3_roots and not value.startswith(phase3_roots):
            fail(
                "Phase 3 commit 只能包含 src/ 產品交付檔案；"
                f"請取消 stage 流程產物：{value}"
            )
        if value.startswith(".johnny/") and value not in {
            ".johnny/config.json",
            ".johnny/state.json",
            ".johnny/dqa-status.json",
        }:
            fail(f"internal gate implementation may not be committed: {value}")
        if path.suffix.lower() in {
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".cs", ".cpp", ".c"
        } and allowed_roots and not value.startswith(allowed_roots):
            fail(f"code path is outside allowed roots: {value}")


def validate_dqa(project: Path, paths: list[str], config: dict, state: dict) -> None:
    phase = int(state.get("phase", 0))
    required_phases = config.get("dqa_required_phases")
    if required_phases is None:
        required = phase >= int(config.get("dqa_required_from_phase", 4))
    else:
        required = phase in {int(value) for value in required_phases}
    if not required or not paths:
        return
    required = ["tdd", "sdd"]
    claude = config.get("claude_dqa", {})
    if claude.get("enabled", False) and claude.get("required", False):
        required.append("claude")
    status = read_json(project / STATE_DIR / "dqa-status.json", {})
    if status.get("schema_version") != 2:
        fail("DQA status uses an obsolete schema; open a new review cycle")
    if status.get("subject_tree") != subject_tree(project, config.get("product_paths", [])):
        fail("DQA evidence is missing or stale for the product subject tree")
    if status.get("commit_tree") != staged_tree(project):
        fail("DQA evidence does not match the complete staged commit tree")
    selection = read_json(project / STATE_DIR / "ecc-selection.json", {}) or {}
    selection_hash = selection.get("selection_sha256")
    if not selection_hash or status.get("ecc_selection_sha256") != selection_hash:
        fail("DQA evidence is missing or stale for the active ECC selection")
    escalation = status.get("escalation") or {}
    if escalation.get("active", False):
        fail(
            "milestone is frozen pending CEO resolution after "
            f"{escalation.get('role')} DQA rejection "
            f"{escalation.get('rejection_count')}"
        )
    expected_scope = "phase4" if phase == 4 else "ticket"
    if status.get("scope", "ticket") != expected_scope:
        fail(f"DQA evidence scope must be {expected_scope}")
    results = status.get("results", {})
    missing = [name for name in required if results.get(name) != "PASS"]
    if missing:
        fail("required DQA did not pass: " + ", ".join(missing))
    reviews = status.get("reviews", {})
    stale_rules = [
        name
        for name in required
        if (reviews.get(name) or {}).get("ecc_selection_sha256") != selection_hash
    ]
    if stale_rules:
        fail("DQA review used a different ECC selection: " + ", ".join(stale_rules))


def validate_branch(project: Path, config: dict, state: dict, event: str) -> None:
    phase = int(state.get("phase", 0))
    if phase < 3:
        return
    branch = run_git(project, "branch", "--show-current", check=False)
    if branch == "main" or branch.startswith("feature/"):
        fail(
            f"direct {event} on protected branch {branch!r} is not allowed; "
            "use a controlled PM merge after approval"
        )
    if phase == 3 and not branch.startswith("codex/milestone-"):
        fail("Phase 3 work must use a codex/milestone-Mxx branch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--event", choices=("pre-commit", "pre-push"), required=True)
    args = parser.parse_args()
    project = git_root(args.project)

    # Fail open for repositories that never opted in.
    if not is_enabled(project):
        return 0
    validate_scope(project)
    config = read_json(project / STATE_DIR / "config.json", {})
    state = read_json(project / STATE_DIR / "state.json", {})
    if not isinstance(config, dict) or not isinstance(state, dict):
        fail("configuration or phase state is invalid")

    validate_branch(project, config, state, args.event)
    paths = staged_paths(project)
    validate_paths(project, paths, config, state)
    validate_dqa(project, paths, config, state)
    print(f"[Johnny gate] {args.event}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
