import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Phase 3 物理餵食測試合約")
    parser.add_argument("--specs_dir", default="specs", help="specs 資料夾相對路徑")
    args = parser.parse_args()

    print(f"[HOOK] inject_specs_hook 開始執行...")
    
    if not os.path.exists(args.specs_dir):
        print(f"[WARNING] 找不到 {args.specs_dir} 目錄，本次可能無測試合約可餵食。")
        sys.exit(0)
    
    spec_files = [f for f in os.listdir(args.specs_dir) if f.endswith('.md')]
    if not spec_files:
        print(f"[WARNING] {args.specs_dir} 內沒有 .md 檔案。")
        sys.exit(0)

    print("\n=========================================")
    print(" 🚨 [SYSTEM PAYLOAD: INTENT CONTRACTS] 🚨")
    print("=========================================\n")
    print("請將以下內容，物理性地附加到 Engineer 的喚醒 Prompt 中：\n")
    
    for f_name in spec_files:
        f_path = os.path.join(args.specs_dir, f_name)
        print(f"--- 檔案: {f_path} ---")
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"[讀取失敗] {e}")
        print("-----------------------------------------\n")
    
    print("[GREEN LIGHT] 物理餵食載荷產出完畢。")
    sys.exit(0)

if __name__ == '__main__':
    main()
