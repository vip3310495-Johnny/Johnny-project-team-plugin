import os
import sys
import glob
import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def main():
    print("[HOOK] 🔍 執行 Log 更新狀態物理檢查 (AfterTool Inspector)...")

    workspace_dir = os.getcwd()
    logs_dir = os.path.join(workspace_dir, "Logs")
    pm_changes_dir = os.path.join(workspace_dir, "PM", "Changes")

    # 搜尋潛在的 Log 檔案
    log_files = []
    if os.path.exists(logs_dir):
        log_files.extend(glob.glob(os.path.join(logs_dir, "*.md")))
    if os.path.exists(pm_changes_dir):
        log_files.extend(glob.glob(os.path.join(pm_changes_dir, "*.md")))

    if not log_files:
        print("[WARN] ⚠️ 警告：專案中未找到任何 Logs/ 或 PM/Changes/ 紀錄檔！")
        print("[WARN] 👉 請 PM 確保在階段或 Milestone 切換時即時更新日誌。")
        sys.exit(0)

    # 檢查是否有今天/最近修改的 Log
    now = datetime.datetime.now()
    recently_updated = False

    for lf in log_files:
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(lf))
            # 判斷是否在 2 小時內有修改過
            if (now - mtime).total_seconds() < 7200:
                recently_updated = True
                print(f"[PASS] ✅ 發現最新更新的日誌檔: {os.path.basename(lf)} (修改時間: {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
                break
        except Exception:
            pass

    if not recently_updated:
        print("[WARN] ⚠️ 警告：檢測到工具執行，但近 2 小時內 Logs/ 或 PM/Changes/ 目錄無新修改痕跡！")
        print("[WARN] 👉 請 PM 在 Milestone / Phase 跳轉時，務必彙整寫入細部變更摘要或日誌。")
    else:
        print("[GREEN LIGHT] Log 狀態良好，驗證通過。")

    sys.exit(0)

if __name__ == '__main__':
    main()
