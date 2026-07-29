"""Validate a DQA checklist against project-configured Phase limits."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from johnny_common import STATE_DIR, git_root, read_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--target-file", type=Path, required=True)
    args = parser.parse_args()
    project = git_root(args.project)
    target = args.target_file.resolve()
    if project not in target.parents or target.suffix.lower() != ".md":
        parser.error("target-file must be a Markdown file inside the project")
    config = read_json(project / STATE_DIR / "config.json", {})
    phase = int(read_json(project / STATE_DIR / "state.json", {}).get("phase", 0))
    limits = config.get("dqa_test_limits", {"3": 30, "4": 50})
    limit = limits.get(str(phase))
    if limit is None:
        print(f"No DQA checklist limit configured for Phase {phase}")
        return 0
    content = target.read_text(encoding="utf-8")
    count = len(re.findall(r"^\s*-\s*\[[ xX]\]\s+", content, re.MULTILINE))
    if count > int(limit):
        parser.error(f"DQA checklist has {count} items; configured limit is {limit}")
    print(f"DQA checklist count {count}/{limit}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
