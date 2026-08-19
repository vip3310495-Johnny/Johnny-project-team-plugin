"""Record a PM-verified, ticket-scoped Johnny role dispatch."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import STATE_DIR, atomic_json, git_root, is_enabled, read_json, state_lock


ROLE_PROFILES = {
    "architect": "johnny-architect.toml",
    "engineer": "johnny-engineer.toml",
    "tdd-dqa": "johnny-tdd-dqa.toml",
    "sdd-dqa": "johnny-sdd-dqa.toml",
    "security-dqa": "johnny-security-dqa.toml",
    "log-agent": "johnny-log-agent.toml",
    "te": "johnny-te.toml",
}


def required_documents(ticket: str) -> dict[str, str]:
    return {
        "milestone_prd": f"PM/Milestones/{ticket}_PRD.md",
        "flow": f"PM/Flows/{ticket}_Flow.md",
        "data_flow": f"PM/DataFlows/{ticket}_Data_Flow.md",
        "context_pack": f"PM/Context/{ticket}.md",
    }


def readable_file(project: Path, relative: str, label: str) -> tuple[str, str]:
    path = (project / relative).resolve()
    try:
        path.relative_to(project.resolve())
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"{label} is missing or unreadable: {relative}") from error
    if not content.strip() or "<" in content and ">" in content:
        raise ValueError(f"{label} is empty or still contains a placeholder: {relative}")
    return relative, hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_acceptance_criteria(project: Path, relative: str) -> None:
    """Require an actionable, row-based acceptance section in every milestone PRD."""
    content = (project / relative).read_text(encoding="utf-8")
    marker = "## Acceptance Criteria"
    if marker not in content:
        raise ValueError(f"milestone_prd is missing required {marker}: {relative}")
    section = content.split(marker, 1)[1].split("\n## ", 1)[0]
    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(rows) < 3:
        raise ValueError(
            "milestone_prd Acceptance Criteria requires a header, separator, and at least one criterion row"
        )
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 7 or any(not cell or "<" in cell or "[ ]" in cell for cell in cells):
            raise ValueError(
                "every Acceptance Criteria row requires ID, target, steps, expected result, "
                "tolerance, evidence command, and responsible DQA"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="在 PM 派出 Johnny 子代理前驗證角色設定與 Milestone 文件。"
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--role", required=True, choices=sorted(ROLE_PROFILES))
    parser.add_argument("--approval", default="")
    args = parser.parse_args()

    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    ticket = args.ticket.strip()
    if not ticket:
        parser.error("ticket is required")
    state_path = project / STATE_DIR / "state.json"
    with state_lock(project):
        state = read_json(state_path, {}) or {}
        policy = str((state.get("execution_policy") or {}).get("mode", ""))
        if policy not in {"SUPERVISED", "AUTONOMOUS"}:
            parser.error("Phase 2 execution policy is missing or invalid")
        profile_relative = f".codex/agents/{ROLE_PROFILES[args.role]}"
        profile_path = project / profile_relative
        if not profile_path.is_file():
            parser.error(f"required role profile is missing: {profile_relative}")

        documents: dict[str, dict[str, str]] = {}
        for label, relative in required_documents(ticket).items():
            path, digest = readable_file(project, relative, label)
            if label == "milestone_prd":
                validate_acceptance_criteria(project, path)
            documents[label] = {"path": path, "sha256": digest}

        approval = args.approval.strip()
        if policy == "SUPERVISED" and approval != "/approve":
            parser.error("SUPERVISED dispatch requires explicit --approval /approve")
        record = {
            "schema_version": 1,
            "ticket": ticket,
            "role": args.role,
            "profile": profile_relative,
            "execution_policy": policy,
            "approval": approval if policy == "SUPERVISED" else "phase2-delegation",
            "documents": documents,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        dispatch_dir = project / STATE_DIR / "dispatch-authorizations"
        dispatch_dir.mkdir(parents=True, exist_ok=True)
        target = dispatch_dir / f"{ticket}-{args.role}.json"
        atomic_json(target, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
