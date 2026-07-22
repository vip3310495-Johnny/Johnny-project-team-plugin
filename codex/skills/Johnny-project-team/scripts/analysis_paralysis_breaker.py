import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# 偵測 CEO 重複提問/過度規劃迴圈，強制終止規劃進入開發 (references/phases/phase0.md 第 7 節, vibe-pm-agent.md)

def main():
    parser = argparse.ArgumentParser(description="突破決斷力癱瘓的防呆逃生門")
    parser.add_argument("--project_dir", default=".", help="專案根目錄")
    parser.add_argument("--context", default="", help="當前卡住的決策上下文")
    args = parser.parse_args()

    print("\n🚨 [HOOK] analysis_paralysis_breaker 啟動！偵測到決策癱瘓。")
    print("================================================================")
    print("CEO，專案不能無限期停滯。根據反通靈與強勢提案鐵律，我們必須立刻做出決定。")
    
    if args.context:
        print(f"針對當前困境：{args.context}")
        
    print("\n💡 【系統強勢裁決】")
    print("我們已為您收斂出兩個最安全的選項。請直接回答 A 或 B：\n")
    print("選項 [A]: 採用最保守、開發最快的主流方案 (MVP 優先)。")
    print("選項 [B]: 採用架構最乾淨、擴展性最強的方案 (犧牲短期速度)。\n")
    print("👉 (強烈推薦) 如果您還是無法決定，請直接輸入 'A'，我們將自動採用 MVP 方案推進。")
    print("================================================================\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
