"""Codex 相容性保護：本 plugin 不會安裝或覆寫 Git hooks。"""

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="說明 Johnny Project Team 的非侵入式 hooks 政策"
    )
    parser.add_argument("--project_dir", default=".", help="僅供顯示的目標專案根目錄")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    print("[INFO] Codex 相容模式：未建立或修改任何 Git hook。")
    print(f"[INFO] 目標專案：{project_dir}")
    print("[INFO] 請依專案既有規範手動執行所需檢查；本 plugin 的診斷腳本不會自動掛載。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
