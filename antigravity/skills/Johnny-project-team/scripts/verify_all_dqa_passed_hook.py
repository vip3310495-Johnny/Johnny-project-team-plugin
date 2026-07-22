import os
import sys
import json

# Force UTF-8 encoding for stdout on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

STATUS_FILE = os.path.join(".agents", ".dqa_status.json")

def print_error(msg):
    print(f"🔴 [REJECTED] {msg}")
    sys.exit(1)

def print_success(msg):
    print(f"🟢 [PASSED] {msg}")

def main():
    print("🔍 正在進行 DQA 三重鎖定檢查 (TDD, SDD, Claude) ...")
    
    if not os.path.exists(STATUS_FILE):
        print_error("找不到 DQA 狀態檔 (.agents/.dqa_status.json)。請確保有完整執行 Phase 3 的所有審查環節！")

    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print_error(f"無法讀取 DQA 狀態檔：{e}")

    required_roles = ["TDD", "SDD", "Claude"]
    missing = []
    failed = []

    for role in required_roles:
        status = data.get(role)
        if not status:
            missing.append(role)
        elif status != "PASS":
            failed.append(role)

    if missing or failed:
        error_msg = "DQA 流程未完整通過，嚴禁向 CEO 請求 /approve！\n"
        if missing:
            error_msg += f"  - 尚未執行的審查: {', '.join(missing)}\n"
        if failed:
            error_msg += f"  - 未通過 (FAIL) 的審查: {', '.join(failed)}\n"
        error_msg += "請確認 TDD、SDD、Claude 皆已回報綠燈。"
        print_error(error_msg)

    print_success("DQA 三重鎖定檢查通過！所有審查皆為 PASS，可以進入下一步或向 CEO 請求 /approve。")
    sys.exit(0)

if __name__ == "__main__":
    main()
