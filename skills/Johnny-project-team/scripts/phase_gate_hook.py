import argparse
import sys

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

    # 驗證 CEO 簽核
    if not args.auto:
        if not args.ceo_signature or not args.ceo_signature.endswith("approve"):
            print("[FAIL] 拒絕存取：缺少 CEO 簽核或無效指令。必須包含 'approve'。")
            sys.exit(1)

    print("[HOOK] phase_gate_hook Stub 執行完畢 (包含基礎簽核防呆驗證)。")
    print("[GREEN LIGHT] phase_gate_hook 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
