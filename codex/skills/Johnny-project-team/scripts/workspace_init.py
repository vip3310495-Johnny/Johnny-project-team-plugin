"""建立治理所需目錄；不初始化 Git、不複製 Plugin、不覆寫內容。"""
import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="建立 Johnny Project Team 的最小治理目錄。")
    parser.add_argument("--project_dir", default=".")
    args = parser.parse_args()
    project = Path(args.project_dir).resolve()
    if not project.is_dir():
        print(f"[REJECTED] 專案不存在：{project}")
        return 1
    for relative in (".agents", "PM", "Architect", "Logs", "SDD_DQA", "TDD_DQA", "specs"):
        (project / relative).mkdir(parents=True, exist_ok=True)
    print("[PASS] 已建立最小治理目錄；未執行 Git 操作或覆寫既有檔案。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
