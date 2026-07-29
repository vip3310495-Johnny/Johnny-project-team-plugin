import argparse
import sys
import os
import datetime

# 將 Log Agent 產出的暫存 Markdown 安全彙整寫入 Logs/Master_Log.md (references/log-agent.md)

def main():
    parser = argparse.ArgumentParser(description="Master Log 彙整器")
    parser.add_argument("--input", required=True, help="待彙整的暫存 Markdown 檔路徑")
    parser.add_argument("--master_log", default="Logs/Master_Log.md", help="目標主控日誌檔路徑")
    args = parser.parse_args()

    print("[HOOK] log_aggregator 開始執行...")
    
    if not os.path.exists(args.input):
        print(f"[ERROR] 找不到輸入檔案: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("[WARN] 輸入內容為空，略過寫入。")
        sys.exit(0)

    # 確保目錄存在
    os.makedirs(os.path.dirname(args.master_log), exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"\n## [{timestamp}] 系統紀錄\n\n{content}\n\n---\n"

    with open(args.master_log, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"[GREEN LIGHT] log_aggregator 已成功將日誌寫入 {args.master_log}。")
    sys.exit(0)

if __name__ == "__main__":
    main()
