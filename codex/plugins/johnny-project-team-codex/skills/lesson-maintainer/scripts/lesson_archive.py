"""Archive stale non-critical lessons by metadata; never delete entry files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_time(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.days < 1:
        parser.error("days must be positive")
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    entries = args.project.resolve() / ".agents" / "lessons_learned" / "entries"
    candidates = 0
    for path in sorted(entries.glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("status", "active") != "active":
            continue
        if str(value.get("severity", "")).casefold() == "critical":
            continue
        last_hit = parse_time(value.get("last_hit_date") or value.get("recorded_at"))
        if last_hit is None or last_hit >= cutoff:
            continue
        candidates += 1
        print(path.stem)
        if args.apply:
            value["status"] = "archived"
            value["archive_reason"] = f"not hit for at least {args.days} days"
            value["archived_at"] = datetime.now(timezone.utc).isoformat()
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    print(f"Archive candidates: {candidates}; applied={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
