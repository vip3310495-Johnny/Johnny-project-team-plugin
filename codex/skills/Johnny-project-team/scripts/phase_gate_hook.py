"""舊版 Phase Gate 相容入口；新版驗證由 project_governance.py 執行。"""
import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="相容入口：轉交至 fail-closed project_governance gate。")
    parser.add_argument("--from_phase", required=True)
    parser.add_argument("--to_phase", required=True)
    parser.add_argument("--ceo_signature", default="")
    parser.add_argument("--milestone", dest="small_milestone")
    parser.add_argument("--project_dir", default=".")
    parser.add_argument("--test_catalog", default="TDD_DQA/test_catalog.json")
    parser.add_argument("--auto", action="store_true")
    args, _unknown = parser.parse_known_args()
    command = [sys.executable, str(Path(__file__).with_name("project_governance.py")), "gate", "--project-dir", args.project_dir, "--from-phase", args.from_phase, "--to-phase", args.to_phase, "--signature", args.ceo_signature, "--test-catalog", args.test_catalog]
    if args.small_milestone:
        command += ["--small-milestone", args.small_milestone]
    if args.auto:
        command.append("--auto")
    return subprocess.run(command).returncode


if __name__ == "__main__":
    sys.exit(main())
