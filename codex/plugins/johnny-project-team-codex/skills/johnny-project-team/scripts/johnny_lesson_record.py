"""Atomically validate and store one structured Johnny lesson."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import append_jsonl, atomic_json, git_root, state_lock


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--cause", required=True)
    parser.add_argument("--prevention", required=True)
    args = parser.parse_args()
    values = [args.role.strip(), args.issue.strip(), args.cause.strip(), args.prevention.strip()]
    if any(not value for value in values):
        parser.error("role, issue, cause, and prevention must be non-empty")
    project = git_root(args.project)
    digest = hashlib.sha256("\0".join(values).encode("utf-8")).hexdigest()[:16]
    record = {
        "schema_version": 1,
        "id": digest,
        "role": values[0],
        "issue": values[1],
        "cause": values[2],
        "prevention": values[3],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with state_lock(project):
        target = project / ".agents" / "lessons_learned" / "entries" / f"{digest}.json"
        atomic_json(target, record)
        append_jsonl(
            project / ".agents" / "lessons_learned" / "history.jsonl",
            {"event": "lesson-recorded", **record},
        )
    print(f"Lesson recorded: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
