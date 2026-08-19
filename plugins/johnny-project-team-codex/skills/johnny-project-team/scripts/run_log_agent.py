"""Append a reviewed Log Agent artifact without inventing observability evidence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Log Agent evidence pipeline 協調器")
    parser.add_argument("--project_dir", type=Path, default=Path.cwd(), help="專案根目錄")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="已審查且具有實際證據的 Log Agent Markdown artifact",
    )
    args = parser.parse_args()

    project = args.project_dir.resolve()
    artifact = args.input.resolve()
    if not artifact.is_file():
        parser.error(f"找不到 Log Agent evidence artifact: {artifact}")
    if not artifact.read_text(encoding="utf-8").strip():
        parser.error(f"Log Agent evidence artifact 不得為空: {artifact}")

    aggregator = Path(__file__).with_name("log_aggregator.py")
    master_log = project / "Logs" / "Master_Log.md"
    result = subprocess.run(
        [
            sys.executable,
            str(aggregator),
            "--input",
            str(artifact),
            "--master_log",
            str(master_log),
        ],
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        return result.returncode

    print(f"[OK] 已彙整經審查的 Log Agent evidence：{artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
