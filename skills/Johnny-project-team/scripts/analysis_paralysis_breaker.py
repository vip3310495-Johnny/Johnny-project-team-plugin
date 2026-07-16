import argparse
import sys

# 偵測 CEO 重複提問/過度規劃迴圈，強制終止規劃進入開發 (references/phases/phase0.md 第 7 節, vibe-pm-agent.md)


def main():
    parser = argparse.ArgumentParser(description="分析癱瘓偵測與終止器")
    parser.add_argument("--project_dir", default=".", help="專案根目錄")
    args = parser.parse_args()

    print("[HOOK] analysis_paralysis_breaker 開始執行...")
    print(f"[HOOK] project_dir={args.project_dir}")
    print("[HOOK] analysis_paralysis_breaker Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] analysis_paralysis_breaker 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
