import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
import os

# Git Commit 阻擋器 (Pre-commit Hook)

def main():
    parser = argparse.ArgumentParser(description="Git Commit 守門員 (Git Guard)")
    args = parser.parse_args()

    print("[HOOK] git_guard.py 開始執行...")

    # 在 Antigravity 中，如果是 Engineer 或 DQA 在跑 run_command("git commit")，通常不會帶特殊環境變數
    # 如果是 PM (透過 Phase Gate 等正式流程)，我們允許。
    # 這裡實作一個物理限制：預設全面禁止直接使用 git commit
    # 除非設定了 ALLOW_COMMIT=1 (這只有 PM 或發布腳本才知道)
    
    if os.environ.get("ALLOW_COMMIT") != "1":
        print(f"\n[FAIL] 🛑 物理限制攔截 (git_guard):")
        print("您目前受到【禁止 git commit】的鐵律物理限制。")
        print("子代理人 (Engineer/DQA) 絕對禁止私自進行 Commit 或 Push 操作。")
        print("請將變更保留在工作區，並回報給 PM，由 PM 或專屬 CI/CD 進行版本控制操作。\n")
        sys.exit(1)

    print("[GREEN LIGHT] git_guard 驗證通過 (具備管理員寫入權限)。")
    sys.exit(0)

if __name__ == '__main__':
    main()
