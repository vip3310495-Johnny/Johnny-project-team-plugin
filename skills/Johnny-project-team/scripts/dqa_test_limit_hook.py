import sys
import os
import argparse
import json
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# DQA Test Count Limit Hook (AfterTool Hook)
# 限制 Phase 3 測試項目 <= 30 條，Phase 4 測試項目 <= 50 條

def main():
    parser = argparse.ArgumentParser(description="DQA Test Item Count Limit Guard")
    parser.add_argument("--target_file", default=None, help="目標測試規格檔案路徑")
    args = parser.parse_args()

    target_file = args.target_file
    if not target_file:
        try:
            if not sys.stdin.isatty():
                input_data = sys.stdin.read()
                if input_data:
                    payload = json.loads(input_data)
                    target_file = payload.get("TargetFile") or payload.get("target_file") or payload.get("path")
        except Exception:
            pass

    if not target_file:
        sys.exit(0)

    norm_target = os.path.normpath(target_file).replace("\\", "/")
    # 僅針對 specs/ 目錄下的 .md 測試合約檔案進行檢驗
    if "specs/" not in norm_target and not norm_target.startswith("specs"):
        sys.exit(0)

    if not norm_target.endswith(".md"):
        sys.exit(0)

    if not os.path.exists(target_file):
        sys.exit(0)

    # 讀取當前階段
    lock_file = os.path.join(".agents", ".current_phase.lock")
    current_phase = "3" # 預設預防性以 Phase 3 計算
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                current_phase = f.read().strip()
        except Exception:
            current_phase = "3"

    # 設定不同階段的限制門檻
    max_allowed = None
    if current_phase == "3":
        max_allowed = 30
    elif current_phase == "4":
        max_allowed = 50
    else:
        # 非 Phase 3 / Phase 4 暫不限制
        sys.exit(0)

    # 計算 Markdown checklist 項目數量 (- [ ] 或 - [x])
    checkbox_pattern = re.compile(r'^\s*-\s*\[[\s xX]\]\s+', re.MULTILINE)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            item_count = len(checkbox_pattern.findall(content))
    except Exception as e:
        print(f"[WARN] 讀取測試規格檔失敗: {e}")
        sys.exit(0)

    print(f"[HOOK] 🔍 DQA 測試數量檢查 (檔案: {os.path.basename(target_file)} | 階段: Phase {current_phase}) ...")
    print(f"[HOOK] 目前測試項目總計: {item_count} 條 (階段上限: {max_allowed} 條)")

    if item_count > max_allowed:
        pm_approval_token = os.path.join("specs", ".pm_exceed_approved")
        if os.path.exists(pm_approval_token):
            print(f"[GREEN LIGHT] 🟢 DQA 測試項目超出上限 ({item_count}/{max_allowed})，但已取得 PM 審核放行 Token。放行！")
            sys.exit(0)
            
        print(f"\n[FAIL] 🛑 DQA 測試項目數量超標 (dqa_test_limit_hook):")
        print(f"專案在 Phase {current_phase} 預設單一合約測試項目不得超過 {max_allowed} 條！")
        print(f"實際提出: {item_count} 條 (已超出 {item_count - max_allowed} 條)")
        print("若 DQA 評估有必要超過 30 項，必須提交 PM 進行審核授權（最多允許提交 1 次），審核通過生成 specs/.pm_exceed_approved 後放行！\n")
        sys.exit(1)

    print(f"[GREEN LIGHT] 🟢 測試項目數量符合規範 ({item_count}/{max_allowed})。放行！")
    sys.exit(0)

if __name__ == '__main__':
    main()
