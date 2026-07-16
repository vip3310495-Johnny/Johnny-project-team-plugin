import argparse
import sys

# 專案所有模組 (Milestone) 開發與單體驗收完畢後觸發 (references/hooks-system.md)


def main():
    parser = argparse.ArgumentParser(description="post-phase3 生命週期 Hook")
    parser.add_argument("--project_dir", required=True, help="專案根目錄")
    args = parser.parse_args()

    print("[HOOK] post-phase3 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir}")
    print("[HOOK] post-phase3 Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] post-phase3 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
