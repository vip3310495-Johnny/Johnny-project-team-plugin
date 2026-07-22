import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
import os

# 教訓提案審核 Hook，喚醒 Lesson Verifier 子代理人 (references/lesson-learnt-registry.md)

def increment_fail_count(lock_file):
    count = 0
    if os.path.exists(lock_file):
        with open(lock_file, "r", encoding="utf-8") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                pass
    count += 1
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write(str(count))
    return count

def check_lockout(lock_file):
    if os.path.exists(lock_file):
        with open(lock_file, "r", encoding="utf-8") as f:
            try:
                if int(f.read().strip()) >= 5:
                    print("🚨 [CRITICAL ALERT] 系統已鎖定！此教訓提案已經連續被退回 5 次。")
                    print("🚨 根據鐵律，代理人已陷入無限退件迴圈，強制終止提交，並立即呼叫 CEO！")
                    print("👉 CEO：請使用 /grill-me 介入了解情況，或手動刪除 .agents/.lesson_reject.count 狀態檔解鎖。")
                    sys.exit(1)
            except ValueError:
                pass

def main():
    parser = argparse.ArgumentParser(description="Lesson Verifier 審核 Hook")
    parser.add_argument("--role", required=True, help="提出教訓的角色，例如 Engineer / PM / DQA")
    parser.add_argument("--proposal", required=True, help="具體的教訓與防呆 SOP 提案內容")
    args = parser.parse_args()

    lock_file = ".agents/.lesson_reject.count"
    print("[HOOK] verify_lesson_hook 開始執行...")
    
    # 檢查是否已經處於鎖定狀態
    check_lockout(lock_file)

    # 驗證角色合法性
    allowed_roles = ["Engineer", "PM", "DQA", "Architect", "TE"]
    if args.role not in allowed_roles:
        fails = increment_fail_count(lock_file)
        print(f"[FAIL] ({fails}/5) 🛑 教訓提案拒絕：角色 '{args.role}' 未獲授權。")
        sys.exit(1)
        
    # 驗證提案內容
    proposal = args.proposal.strip()
    if len(proposal) < 30:
        fails = increment_fail_count(lock_file)
        print(f"[FAIL] ({fails}/5) 🛑 教訓提案拒絕：內容過短 (小於 30 字元)。請詳細說明發生了什麼問題以及未來的防呆 SOP。")
        sys.exit(1)
        
    # 簡單特徵檢查：是否有防呆或 SOP 字眼
    keywords = ["防呆", "SOP", "應對", "解決", "防範", "規則", "避免"]
    if not any(k in proposal for k in keywords):
        fails = increment_fail_count(lock_file)
        print(f"[FAIL] ({fails}/5) 🛑 教訓提案拒絕：缺乏具體的防護機制 (未包含防呆/SOP/防範等關鍵字)。")
        print("我們不僅需要紀錄錯誤，更需要紀錄『未來如何避免』。")
        sys.exit(1)
        
    # 通過後清空計數器
    if os.path.exists(lock_file):
        os.remove(lock_file)

    print("[GREEN LIGHT] 教訓提案驗證通過。準備寫入 lessons_learned.md。")
    sys.exit(0)

if __name__ == "__main__":
    main()
