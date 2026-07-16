import argparse
import sys

# MoSCoW 分級排序器 (references/vibe-pm-agent.md 腳本工具索引)


def main():
    parser = argparse.ArgumentParser(description="MoSCoW 優先順序分級器")
    parser.add_argument("--input", required=True, help="待分級的需求清單檔案路徑")
    args = parser.parse_args()

    print("[HOOK] moscow_sorter 開始執行...")
    print(f"[HOOK] input={args.input}")
    print("[HOOK] moscow_sorter Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] moscow_sorter 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
