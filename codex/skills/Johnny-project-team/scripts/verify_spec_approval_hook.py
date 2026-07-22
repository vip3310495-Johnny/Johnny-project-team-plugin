"""相容入口：建立具內容指紋的 Milestone 規格核准。"""
import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="要求明確範圍與 artifact 的規格核准。")
    parser.add_argument("--ceo_signature", default="")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--project_dir", default=".")
    parser.add_argument("--phase", default="3")
    parser.add_argument("--milestone")
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--approver", default="CEO")
    args = parser.parse_args()
    if args.auto or not args.artifact:
        print("[REJECTED] 必須列出 artifact，且禁止 --auto。")
        return 1
    command = [sys.executable, str(Path(__file__).with_name("project_governance.py")), "approve", "--project-dir", args.project_dir, "--scope", "milestone_spec", "--phase", args.phase, "--approver", args.approver, "--gate", "spec_approval", "--signature", args.ceo_signature]
    if args.milestone:
        command += ["--small-milestone", args.milestone]
    for item in args.artifact:
        command += ["--artifact", item]
    return subprocess.run(command).returncode


if __name__ == "__main__":
    sys.exit(main())
