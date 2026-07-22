"""Phase 4 相容 Gate：僅驗證既有三重 DQA，不會執行 Claude。"""
import argparse
import subprocess
import sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description="驗證既有 Phase 4 DQA 證據。")
    parser.add_argument("--project_dir", default=".")
    args, _unknown = parser.parse_known_args()
    command = [sys.executable, str(Path(__file__).with_name("verify_all_dqa_passed_hook.py")), "--project_dir", args.project_dir, "--phase", "4"]
    return subprocess.run(command).returncode

if __name__ == "__main__":
    sys.exit(main())