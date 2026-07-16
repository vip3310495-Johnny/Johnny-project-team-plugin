import argparse
import sys

# 教訓提案審核 Hook，喚醒 Lesson Verifier 子代理人 (references/lesson-learnt-registry.md)


def main():
    parser = argparse.ArgumentParser(description="Lesson Verifier 審核 Hook")
    parser.add_argument("--role", required=True, help="提出教訓的角色，例如 Engineer / PM / DQA")
    parser.add_argument("--proposal", required=True, help="具體的教訓與防呆 SOP 提案內容")
    args = parser.parse_args()

    print("[HOOK] verify_lesson_hook 開始執行...")
    
    # 驗證角色合法性
    allowed_roles = ["Engineer", "PM", "DQA", "Architect", "TE"]
    if args.role not in allowed_roles:
        print(f"[FAIL] 🛑 教訓提案拒絕：角色 '{args.role}' 未獲授權。")
        sys.exit(1)
        
    # 驗證提案內容
    proposal = args.proposal.strip()
    if len(proposal) < 30:
        print("[FAIL] 🛑 教訓提案拒絕：內容過短 (小於 30 字元)。請詳細說明發生了什麼問題以及未來的防呆 SOP。")
        sys.exit(1)
        
    # 簡單特徵檢查：是否有防呆或 SOP 字眼
    keywords = ["防呆", "SOP", "應對", "解決", "防範", "規則", "避免"]
    if not any(k in proposal for k in keywords):
        print("[FAIL] 🛑 教訓提案拒絕：缺乏具體的防護機制 (未包含防呆/SOP/防範等關鍵字)。")
        print("我們不僅需要紀錄錯誤，更需要紀錄『未來如何避免』。")
        sys.exit(1)
        
    print("[GREEN LIGHT] 教訓提案驗證通過。準備寫入 lessons_learned.md。")
    sys.exit(0)


if __name__ == "__main__":
    main()
