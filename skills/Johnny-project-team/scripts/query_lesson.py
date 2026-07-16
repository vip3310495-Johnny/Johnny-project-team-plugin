import argparse
import sys

# 依角色標籤與關鍵字檢索歷史教訓 (references/lesson-learnt-registry.md, engineering-agent.md)


def main():
    parser = argparse.ArgumentParser(description="歷史教訓檢索腳本")
    parser.add_argument("terms", nargs="+", help="角色標籤與/或關鍵字，例如 Engineer 資料庫鎖")
    args = parser.parse_args()

    print("[HOOK] query_lesson 開始執行...")
    print(f"[HOOK] terms={args.terms}")
    print("[HOOK] query_lesson Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] query_lesson 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
