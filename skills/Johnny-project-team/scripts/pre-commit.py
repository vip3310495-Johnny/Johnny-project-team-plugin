import argparse
import os
import sys

# 在 Engineer 或 PM 嘗試 git commit 前觸發，通常掛載 black, flake8 等 Linter (references/hooks-system.md)


def main():
    parser = argparse.ArgumentParser(description="pre-commit 生命週期 Hook")
    parser.add_argument("--project_dir", required=True, help="專案根目錄")
    args = parser.parse_args()

    print("[HOOK] pre-commit 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir}")

    src_dir = os.path.join(args.project_dir, "src")
    if not os.path.exists(src_dir):
        print("[HOOK] 沒有 src 目錄，跳過檢查。")
        sys.exit(0)

    print("[HOOK] pre-commit Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] pre-commit 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
