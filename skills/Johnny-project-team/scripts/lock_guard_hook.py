import sys
import os
import argparse
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Lock File Protection Hook (BeforeTool Hook for Phase 1~6 Gate Security)
# 確保 Phase 1~6 任何 Agent 試圖修改 .agents/.current_phase.lock 時，必須已過 phase_gate_hook.py 驗證

def main():
    parser = argparse.ArgumentParser(description="Lock File Guard Hook")
    parser.add_argument("--target_file", default=None, help="目標修改檔案路徑")
    args = parser.parse_args()

    # 從參數或標準輸入讀取 target_file (相容不同的 BeforeTool JSON  payload)
    target_file = args.target_file
    if not target_file:
        try:
            if not sys.stdin.isatty():
                input_data = sys.stdin.read()
                if input_data:
                    payload = json.loads(input_data)
                    # 相容 write_to_file / replace_file_content 參數結構
                    target_file = payload.get("TargetFile") or payload.get("target_file") or payload.get("path")
        except Exception:
            pass

    if not target_file:
        sys.exit(0)

    norm_target = os.path.normpath(target_file).replace("\\", "/")
    if not norm_target.endswith(".agents/.current_phase.lock"):
        # 不是在寫入鎖檔，直接放行
        sys.exit(0)

    print(f"[HOOK] 🛡️ 偵測到試圖修改階段鎖檔: {norm_target}")

    lock_file = ".agents/.current_phase.lock"
    token_file = os.path.join(".agents", ".phase_gate_verified")

    current_phase = "0"
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                current_phase = f.read().strip()
        except Exception:
            current_phase = "0"

    # Phase 0 跳轉 Phase 1 屬於傳統腳本模式特例放行
    if current_phase == "0":
        print("[HOOK] 🟢 目前處於 Phase 0，允許通過階段閘門鎖檔更新。")
        sys.exit(0)

    # Phase 1~6 必須檢驗是否有有效的驗證 Token (.phase_gate_verified)
    if os.path.exists(token_file):
        print("[HOOK] 🟢 偵測到有效的 phase_gate_hook 驗證 Token！放行鎖檔修改。")
        try:
            os.remove(token_file) # 消費權杖
        except Exception:
            pass
        sys.exit(0)

    print("\n[FAIL] 🛑 系統層級防護攔截 (BeforeTool Hook - lock_guard_hook):")
    print(f"目前專案處於 Phase {current_phase}。任何跳轉或狀態修改必須先過 `phase_gate_hook.py` 驗證！")
    print("拒絕非法的黑箱修改或手動竄改 `.current_phase.lock` 狀態檔！\n")
    sys.exit(1)

if __name__ == '__main__':
    main()
