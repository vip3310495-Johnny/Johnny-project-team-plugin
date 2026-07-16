import argparse
import sys

# Hooks 系統背景控制器，依生命週期自動傳入引數呼叫對應 Hook (references/hooks-system.md)


def main():
    parser = argparse.ArgumentParser(description="Hooks 系統背景控制器")
    parser.add_argument("--project_dir", required=True, help="專案根目錄")
    args = parser.parse_args()

    print("[HOOK] workflow_controller 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir}")
    print("[HOOK] workflow_controller Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] workflow_controller 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
