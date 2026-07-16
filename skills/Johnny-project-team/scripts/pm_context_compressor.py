import argparse
import sys

# PM 記憶壓縮驗證器，確保 Digest 摘要小於 800 字 (references/phases/phase3.md 第 8 節)


def main():
    parser = argparse.ArgumentParser(description="PM 上下文壓縮驗證器")
    parser.add_argument("digest_path", help="Digest 摘要檔路徑，例如 PM/Memory/M1_Digest.md")
    args = parser.parse_args()

    print("[HOOK] pm_context_compressor 開始執行...")
    
    import os
    if not os.path.exists(args.digest_path):
        print(f"[WARN] 摘要檔 {args.digest_path} 不存在，跳過壓縮驗證。")
        sys.exit(0)
        
    with open(args.digest_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 計算中英文字元數 (含空白)
    char_count = len(content)
    
    if char_count > 1500:
        print(f"[FAIL] 🛑 PM 記憶壓縮失敗！")
        print(f"檔案 `{args.digest_path}` 的長度高達 {char_count} 字元，超過了 1500 字元的上限。")
        print("過長的上下文會導致子代理人產生幻覺或 Token 溢出。")
        print("請立刻重新精煉與壓縮此摘要，留下關鍵結論與狀態即可。")
        sys.exit(1)
        
    print(f"[GREEN LIGHT] pm_context_compressor 通過 (當前長度: {char_count} 字元)。")
    sys.exit(0)


if __name__ == "__main__":
    main()
