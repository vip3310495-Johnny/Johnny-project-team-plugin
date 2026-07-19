import os
import sys
import argparse
import re

# Force UTF-8 encoding for stdout on Windows to prevent UnicodeEncodeError with emojis
sys.stdout.reconfigure(encoding='utf-8')

def print_error(msg):
    print(f"🔴 [REJECTED] {msg}")
    sys.exit(1)

def print_success(msg):
    print(f"🟢 [PASSED] {msg}")

def main():
    parser = argparse.ArgumentParser(description="Verify the As-Built Architecture Report.")
    parser.add_argument(
        "--report-path", 
        type=str, 
        default="Architect/As_Built_Architecture.md",
        help="Path to the architecture report markdown file."
    )
    args = parser.parse_args()

    filepath = args.report_path

    print(f"🔍 正在檢查完工架構報告 (As-Built Architecture Report) ...")
    print(f"📂 目標路徑: {filepath}")

    # 1. Check File Existence
    if not os.path.exists(filepath):
        print_error(f"找不到檔案 '{filepath}'。請 Architect 產生該架構報告！")

    # 2. Check File Size (Anti-laziness)
    min_size_bytes = 800
    file_size = os.path.getsize(filepath)
    if file_size < min_size_bytes:
        print_error(f"檔案過小 ({file_size} bytes)。要求至少 {min_size_bytes} bytes。請勿偷工減料，必須產出完整的系統架構報告！")

    # 3. Check Required Content/Sections
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define mandatory keywords or section titles that must exist
    required_keywords = [
        r"(架構|Architecture)",
        r"(目錄|結構|Structure|Directory)",
        r"(模組|元件|Module|Component)"
    ]

    missing_keywords = []
    for pattern in required_keywords:
        if not re.search(pattern, content, re.IGNORECASE):
            missing_keywords.append(pattern)

    if missing_keywords:
        print_error(
            f"報告內容缺乏關鍵元素。請確保報告內包含以下相關字眼的章節或描述：\n"
            f"缺失項目：{', '.join(missing_keywords)}\n"
            "這是一份給未來看的架構說明，必須包含系統架構、目錄結構與模組說明。"
        )

    print_success("完工架構報告檢查通過！內容充實且包含必要章節。")
    sys.exit(0)

if __name__ == "__main__":
    main()
