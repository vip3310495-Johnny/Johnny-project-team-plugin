import argparse
import sys
import os
import subprocess
import tempfile

def main():
    parser = argparse.ArgumentParser(description="Log Agent Pipeline 協調器")
    parser.add_argument("--project_dir", default=".", help="專案根目錄")
    parser.add_argument("--status", choices=["PASS", "FAIL"], default="PASS", help="本次記錄的狀態")
    args = parser.parse_args()

    print("[HOOK] run_log_agent 開始執行...")
    
    # 決定紅綠燈燈號
    status_emoji = "🟢 順暢運行中" if args.status == "PASS" else "🔴 死結 (Stalemate) / 退件"
    
    # 準備要交給 aggregator 的 Log 內容 (Pointer-based)
    log_content = f"""
### 🚦 狀態報告 (Status Report)
- 🚦 **進度狀態**: {status_emoji}
- 📦 **上下文傳遞**: 🟢 資訊完整
- 💰 **效能成本**: 🟢 正常

> 備註：這是由 `run_log_agent.py` 自動產生的摘要紀錄。詳細執行軌跡與上下文請參閱 PM 的 `Memory/` 與對應的 DQA 報告。
"""

    # 寫入暫存檔
    fd, temp_path = tempfile.mkstemp(suffix=".md", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(log_content.strip())
        
    try:
        # 呼叫 log_aggregator.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        aggregator_script = os.path.join(script_dir, "log_aggregator.py")
        
        master_log_path = os.path.join(args.project_dir, "Logs", "Master_Log.md")
        
        print(f"[INFO] 呼叫 log_aggregator.py 寫入 {master_log_path}...")
        
        result = subprocess.run(
            [sys.executable, aggregator_script, "--input", temp_path, "--master_log", master_log_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"[ERROR] log_aggregator 執行失敗:\n{result.stderr}")
            sys.exit(1)
        else:
            print(result.stdout)
            
    finally:
        # 清理暫存檔
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("[GREEN LIGHT] run_log_agent 執行完畢。管線已順利打通！")
    sys.exit(0)

if __name__ == "__main__":
    main()
