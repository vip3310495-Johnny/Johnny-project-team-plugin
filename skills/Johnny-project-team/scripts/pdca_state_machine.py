import argparse
import sys

# 狀態機鎖定 (PLAN -> DO -> CHECK -> ACT)，防止 Agent 跳過規劃直接寫 Code (references/vibe-pm-agent.md 腳本工具索引)


def main():
    parser = argparse.ArgumentParser(description="PDCA 狀態機")
    parser.add_argument("--state", choices=["PLAN", "DO", "CHECK", "ACT"], required=True, help="欲切換的狀態")
    args = parser.parse_args()

    print("[HOOK] pdca_state_machine 開始執行...")
    print(f"[HOOK] state={args.state}")
    print("[HOOK] pdca_state_machine Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] pdca_state_machine 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
