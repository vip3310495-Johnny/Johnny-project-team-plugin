import sys
import os
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# SessionStart Hook: Check LLM Model Recommendation Matrix Readiness
# 當 Session 啟動時，檢查工作區是否已包含 PM/Model_Recommendation_Matrix.md

def main():
    parser = argparse.ArgumentParser(description="Check LLM Model Recommendation Matrix Readiness")
    parser.add_argument("--project_dir", default=".", help="目標專案根目錄")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    matrix_path = os.path.join(project_dir, "PM", "Model_Recommendation_Matrix.md")

    print("[HOOK] 🚀 執行 SessionStart 防線檢查：LLM 模型推薦矩陣適配性...")

    if os.path.exists(matrix_path) and os.path.getsize(matrix_path) > 100:
        print(f"[HOOK] 🟢 偵測到團隊 AI 模型推薦矩陣 ({matrix_path}) 已就緒。")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("💡 [SessionStart 提醒通知]：")
        print(f"未偵測到團隊 AI 模型適配矩陣 `PM/Model_Recommendation_Matrix.md`！")
        print("請 PM 於專案初始化 (Phase 0) 時引導設定：")
        print(" 1. 複製 `.agents/skills/Johnny-project-team/references/templates/Model_Recommendation_Matrix.md`")
        print(" 2. 在工作區產出實體檔案 `PM/Model_Recommendation_Matrix.md`，列表推薦各角色適用模型，並確實填寫「單次預算」與「允許時間」。")
        print("="*70 + "\n")
        # SessionStart 拋出提示訊息但不強制硬性死鎖 session 建立
        sys.exit(0)

if __name__ == '__main__':
    main()
