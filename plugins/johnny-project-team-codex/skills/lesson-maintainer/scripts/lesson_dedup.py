"""Find duplicate structured lessons and optionally merge metadata without deletion."""

from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path


def load_entries(project: Path) -> list[tuple[Path, dict]]:
    entries = project / ".agents" / "lessons_learned" / "entries"
    loaded = []
    for path in sorted(entries.glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict) and value.get("status", "active") == "active":
            loaded.append((path, value))
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.86)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not 0.5 <= args.threshold <= 1:
        parser.error("threshold must be between 0.5 and 1")
    entries = load_entries(args.project.resolve())
    candidates: list[tuple[Path, dict, Path, dict, float]] = []
    for index, (left_path, left) in enumerate(entries):
        left_text = f"{left.get('issue', '')}\n{left.get('cause', '')}".casefold()
        for right_path, right in entries[index + 1 :]:
            right_text = f"{right.get('issue', '')}\n{right.get('cause', '')}".casefold()
            score = SequenceMatcher(None, left_text, right_text).ratio()
            if score >= args.threshold:
                candidates.append((left_path, left, right_path, right, score))
    for master_path, master, duplicate_path, duplicate, score in candidates:
        print(f"{master_path.stem} <- {duplicate_path.stem}: {score:.3f}")
        if args.apply:
            master["occurrence_count"] = int(master.get("occurrence_count", 1)) + int(
                duplicate.get("occurrence_count", 1)
            )
            related = set(master.get("related_ids", []))
            related.add(str(duplicate.get("id", duplicate_path.stem)))
            master["related_ids"] = sorted(related)
            duplicate["status"] = "merged"
            duplicate["merged_into"] = master.get("id", master_path.stem)
            master_path.write_text(
                json.dumps(master, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            duplicate_path.write_text(
                json.dumps(duplicate, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    print(f"Duplicate candidates: {len(candidates)}; applied={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
