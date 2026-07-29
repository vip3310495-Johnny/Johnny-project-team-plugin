import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
import os
import time

# 通用階段閘門腳本：驗證 CEO 簽核後才放行 Phase 跳轉 (references/phases/phase0.md ~ phase4.md)
# 【Phase 0 特例規範】：
# Phase 0 為專案初始與甦醒恢復點 (Resumed Project Gateway)。
# 根據 Save_State.md 復甦點，Phase 0 支援動態任意跳轉 (如 from_phase=0 -> to_phase=1/2/3/4)。
# 因此 Phase 0 的階段跳轉維持「顯式腳本呼叫」，由本腳本驗證後核發解鎖 Token 並建立初始鎖檔。
# 進入 Phase 1~6 後，系統層級之 BeforeTool Hook (lock_guard_hook.py) 將全面啟動硬性防禦。


def main():
    parser = argparse.ArgumentParser(description="通用階段閘門腳本 (Phase Gate Hook)")
    parser.add_argument("--from_phase", required=True, help="目前所在的 Phase 編號")
    parser.add_argument("--to_phase", required=True, help="欲跳轉的目標 Phase 編號")
    parser.add_argument("--ceo_signature", default=None, help="CEO 簽核指令，例如 /approve")
    parser.add_argument("--prd_path", default=None, help="對應的 PRD 或 Milestone_PRD.md 路徑")
    parser.add_argument("--auto", action="store_true", help="是否為全自動模式 (/goal)")
    parser.add_argument("--milestone", default=None, help="Milestone 編號 (例如 M1)")
    args = parser.parse_args()

    print("[HOOK] phase_gate_hook 開始執行...")
    print(f"[HOOK] from_phase={args.from_phase} to_phase={args.to_phase} milestone={args.milestone}")
    print(f"[HOOK] ceo_signature={args.ceo_signature} auto={args.auto} prd_path={args.prd_path}")

    # 1. 驗證實際階段與聲稱階段是否相符 (防造假跳關)
    lock_file = ".agents/.current_phase.lock"
    current_phase = "0"
    if os.path.exists(lock_file):
        with open(lock_file, "r", encoding="utf-8") as f:
            current_phase = f.read().strip()
    
    if args.from_phase != current_phase:
        print(f"[FAIL] 拒絕存取：您聲稱處於 Phase {args.from_phase}，但系統記錄目前處於 Phase {current_phase}。禁止造假跳關！")
        sys.exit(1)

    # 2. 驗證產出物新鮮度
    if args.prd_path:
        if not os.path.exists(args.prd_path):
            print(f"[FAIL] 拒絕存取：找不到產出物 {args.prd_path}。")
            sys.exit(1)
        mtime = os.path.getmtime(args.prd_path)
        # 方案 A 升級：移除不合理的 7 天效期限制，改為溫馨提醒以避免長時間 Milestone 卡死
        if time.time() - mtime > 7 * 24 * 3600:
            print(f"💡 [WARN] 提醒：產出物 {args.prd_path} 距離上次修改已超過 7 天，請確認這是否是本階段最新鮮的產出。")

    # 2.5 Phase 3 專屬跳轉檢查 (Visual Report Gatekeeper)
    if args.from_phase == "3":
        if not args.milestone:
            print("[FAIL] 拒絕存取：從 Phase 3 跳轉必須提供 --milestone 參數 (例如 M1)。")
            sys.exit(1)
            
        sys_flow_path = os.path.join("PM", f"{args.milestone}_System_Flow.md")
        data_flow_path = os.path.join("PM", f"{args.milestone}_Data_Flow.md")
        
        missing_reports = []
        for path in [sys_flow_path, data_flow_path]:
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                missing_reports.append(path)
                
        if missing_reports:
            print(f"[FAIL] 拒絕存取：找不到必備的視覺化報告，或檔案過小。缺失清單：{missing_reports}")
            sys.exit(1)
            
        print(f"💡 [WARN] 請 PM 再次確認圖面 ({sys_flow_path}, {data_flow_path}) 正確無誤，是否已完全與剛通過 DQA 的最新程式碼現狀相符？")

    # 3. 驗證 CEO 簽核
    if not args.auto:
        if not args.ceo_signature or not args.ceo_signature.endswith("approve"):
            print("[FAIL] 拒絕存取：缺少 CEO 簽核或無效指令。必須包含 'approve'。")
            sys.exit(1)

    # 4. 核發驗證 Token 供 BeforeTool lock_guard放行 Phase 1~6 鎖檔變更
    token_file = os.path.join(".agents", ".phase_gate_verified")
    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    with open(token_file, "w", encoding="utf-8") as f:
        f.write(f"TOKEN_VERIFIED:{args.from_phase}->{args.to_phase}")

    # 更新階段狀態檔
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write(args.to_phase)

    print("[GREEN LIGHT] phase_gate_hook 驗證通過。系統已進入 Phase " + args.to_phase)
    sys.exit(0)


if __name__ == "__main__":
    main()
