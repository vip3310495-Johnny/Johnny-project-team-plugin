"""Generate a concise digest from promoted, frequent, or critical lessons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    root = args.project.resolve() / ".agents" / "lessons_learned"
    selected = []
    for path in sorted((root / "entries").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("status", "active") in ("merged", "archived"):
            continue
        if (
            value.get("status") == "promoted-to-rule"
            or int(value.get("occurrence_count", 1)) >= 3
            or str(value.get("severity", "")).casefold() == "critical"
        ):
            selected.append(value)
    lines = [
        "# Lesson Learnt Digest",
        "",
        "> Generated from promoted, frequent, or critical structured lessons.",
        "",
    ]
    for value in selected:
        lines.append(
            f"- [{value.get('id', 'unknown')}] {value.get('issue', '')} — "
            f"{value.get('prevention', '')}"
        )
    target = root / "DIGEST.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"Digest entries: {len(selected)}; wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
