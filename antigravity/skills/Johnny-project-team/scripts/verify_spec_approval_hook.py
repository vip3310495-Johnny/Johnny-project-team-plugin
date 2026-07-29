import argparse
import sys
import datetime
import os

def main():
    parser = argparse.ArgumentParser(description="Phase 3 驗證 CEO 測試合約簽核")
    parser.add_argument("--ceo_signature", default="", help="CEO 簽核指令 (必須是 /approve)")
    parser.add_argument("--auto", action="store_true", help="是否為自動通行模式")
    
    args = parser.parse_args()

    print(f"[HOOK] verify_spec_approval_hook 開始執行...")
    
    if args.auto:
        print("[WARNING] 目前為全自動模式，跳過 CEO 簽核驗證。")
        print(f"[GREEN LIGHT] 允許進入實作迴圈。")
        sys.exit(0)

    if args.ceo_signature.strip() == "/approve":
        print(f"[SUCCESS] 偵測到有效的 CEO 簽核: {args.ceo_signature}")
        print(f"[GREEN LIGHT] 允許進入實作迴圈。")
        sys.exit(0)
    else:
        print(f"[ERROR] 簽核無效。預期: /approve, 實際: '{args.ceo_signature}'")
        print("[RED LIGHT] 禁止進入實作迴圈！請 PM 退回並向 CEO 取得授權。")
        sys.exit(1)

if __name__ == '__main__':
    main()
