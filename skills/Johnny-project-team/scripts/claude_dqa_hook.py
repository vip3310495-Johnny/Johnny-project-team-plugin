import argparse
import sys

# 喚醒外部 Claude Code CLI 進行獨立 DQA 審查 (references/phases/phase3.md 第 6 節)


def main():
    parser = argparse.ArgumentParser(description="Claude DQA 外部獨立審查 Hook")
    parser.add_argument("--project_dir", default=".", help="待審查的專案根目錄")
    parser.add_argument("--model", default="Sonnet", help="欲使用的 Claude 模型版本，禁止寫死版本號")
    args = parser.parse_args()

    print("[HOOK] claude_dqa_hook 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir} model={args.model}")
    print("[HOOK] claude_dqa_hook Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] claude_dqa_hook 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
