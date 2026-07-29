import argparse
import sys
import json
import datetime
import os
import subprocess

def scan_codebase(root_dir="."):
    """簡易的 Codebase 掃描，回傳前 10 個核心檔案與專案特徵"""
    print(f"[SCAN] 正在掃描專案: {os.path.abspath(root_dir)}")
    features = []
    
    if os.path.exists(os.path.join(root_dir, "package.json")):
        features.append("Node.js 專案")
    if os.path.exists(os.path.join(root_dir, "requirements.txt")) or os.path.exists(os.path.join(root_dir, "pyproject.toml")):
        features.append("Python 專案")
        
    core_files = []
    try:
        # 使用 git ls-files 抓取受控檔案
        result = subprocess.run(["git", "ls-files"], cwd=root_dir, capture_output=True, text=True, check=True)
        files = result.stdout.splitlines()
        
        for f in files:
            if f.startswith("src/") or f.endswith(".py") or f.endswith(".ts") or f.endswith(".tsx"):
                core_files.append(f)
                if len(core_files) >= 10: break
    except Exception:
        pass
        
    return features, core_files

def main():
    parser = argparse.ArgumentParser(description="蘇格拉底拷問與技術可行性評估工具")
    parser.add_argument("--plan", default="", help="要評估的計畫內容或檔案路徑")
    parser.add_argument("--auto_scan", action="store_true", help="是否自動掃描當前專案")
    args = parser.parse_args()

    print(f"\n=========================================")
    print(" 🏛️ [Socratic Challenger & Tech Explorer] 🏛️")
    print("=========================================\n")
    
    print("【商業邏輯防禦】")
    print("- 正在檢視需求是否具備明確的商業價值與 MVP 精神...")
    print("- 是否有定義 Non-goals 防止 Scope Creep？")
    
    if args.auto_scan:
        print("\n【技術可行性探索 (類似 /opsx:explore)】")
        features, files = scan_codebase(".")
        print(f"專案特徵: {', '.join(features) if features else '未識別'}")
        if files:
            print("關鍵核心檔案掃描:")
            for f in files:
                print(f"  - {f}")
        print("\n[系統提示] 請 PM 根據上述 Codebase 現況，評估 CEO 計畫的技術可行性。")
        print("是否存在過度設計？有沒有更簡單的實作方案？請在回應中提出。")

    print("\n[GREEN LIGHT] 蘇格拉底拷問與探索程序執行完畢。請 PM 開始對 CEO 進行提問。")
    sys.exit(0)

if __name__ == '__main__':
    main()
