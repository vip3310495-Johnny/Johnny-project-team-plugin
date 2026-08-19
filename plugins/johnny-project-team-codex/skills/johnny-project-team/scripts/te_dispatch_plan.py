"""Calculate a safe DQA-to-TE dispatch plan without spawning agents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from johnny_common import git_root, state_lock


def calculate_plan(
    requested: int,
    active_agents: int,
    session_limit: int = 4,
    per_dqa_limit: int = 2,
) -> dict[str, int]:
    if min(requested, active_agents, session_limit, per_dqa_limit) < 0:
        raise ValueError("counts and limits must be non-negative")
    free_slots = max(0, session_limit - active_agents)
    spawn = min(requested, free_slots, per_dqa_limit)
    return {
        "requested": requested,
        "active_agents": active_agents,
        "session_limit": session_limit,
        "per_dqa_limit": per_dqa_limit,
        "free_slots": free_slots,
        "spawn_now": spawn,
        "queue": requested - spawn,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--requested", type=int, required=True)
    parser.add_argument("--active-agents", type=int, required=True)
    parser.add_argument("--session-limit", type=int, default=4)
    parser.add_argument("--per-dqa-limit", type=int, default=2)
    args = parser.parse_args()
    project = git_root(args.project)

    # Verify lock availability, then release it before any agent may be spawned.
    with state_lock(project, timeout=0):
        pass
    print(
        json.dumps(
            calculate_plan(
                args.requested,
                args.active_agents,
                args.session_limit,
                args.per_dqa_limit,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
