import argparse
import sys

# 進入 Phase 1 (細節計畫) 之前觸發 (references/hooks-system.md)


def main():
    parser = argparse.ArgumentParser(description="pre-phase1 生命週期 Hook")
    parser.add_argument("--project_dir", required=True, help="專案根目錄")
    args = parser.parse_args()

    print("[HOOK] pre-phase1 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir}")
    print("[HOOK] pre-phase1 Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] pre-phase1 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
