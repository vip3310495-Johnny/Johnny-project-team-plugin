import argparse
import sys

# 產生 lessons_learned 的 DIGEST.md 摘要層 (references/phases/phase0.md 第 3 節)


def main():
    parser = argparse.ArgumentParser(description="Lessons Learned Digest 產生器")
    parser.add_argument("--lessons_dir", default=".agents/lessons_learned", help="教訓知識庫目錄")
    args = parser.parse_args()

    print("[HOOK] generate_digest 開始執行...")
    print(f"[HOOK] lessons_dir={args.lessons_dir}")
    print("[HOOK] generate_digest Stub 執行完畢 (尚未實作完整商業邏輯)。")
    print("[GREEN LIGHT] generate_digest 通過。")
    sys.exit(0)


if __name__ == "__main__":
    main()
