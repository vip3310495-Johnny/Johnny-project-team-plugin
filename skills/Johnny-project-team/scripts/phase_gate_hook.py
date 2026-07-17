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


def main():
    parser = argparse.ArgumentParser(description="通用階段閘門腳本 (Phase Gate Hook)")
    parser.add_argument("--from_phase", required=True, help="目前所在的 Phase 編號")
    parser.add_argument("--to_phase", required=True, help="欲跳轉的目標 Phase 編號")
    parser.add_argument("--ceo_signature", default=None, help="CEO 簽核指令，例如 /approve")
    parser.add_argument("--prd_path", default=None, help="對應的 PRD 或 Milestone_PRD.md 路徑")
    parser.add_argument("--auto", action="store_true", help="是否為全自動模式 (/goal)")
    args = parser.parse_args()

    print("[HOOK] phase_gate_hook 開始執行...")
    print(f"[HOOK] from_phase={args.from_phase} to_phase={args.to_phase}")
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
        # 若檔案修改時間超過 7 天，視為「非當前 Milestone 產物」而退件
        if time.time() - mtime > 7 * 24 * 3600:
            print(f"[FAIL] 拒絕存取：產出物 {args.prd_path} 過於老舊 (超過 7 天)，請確保您提交的是本階段最新鮮的產出！")
            sys.exit(1)

    # 3. 驗證 CEO 簽核
    if not args.auto:
        if not args.ceo_signature or not args.ceo_signature.endswith("approve"):
            print("[FAIL] 拒絕存取：缺少 CEO 簽核或無效指令。必須包含 'approve'。")
            sys.exit(1)

    # 更新階段狀態檔
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write(args.to_phase)

    print("[GREEN LIGHT] phase_gate_hook 驗證通過。系統已進入 Phase " + args.to_phase)
    sys.exit(0)


if __name__ == "__main__":
    main()
