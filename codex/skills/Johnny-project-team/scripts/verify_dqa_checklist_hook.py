import os
import sys
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description="Phase 3 驗證 DQA TO-DO 清單是否全數驗收")
    parser.add_argument("--specs_dir", default="specs", help="specs 資料夾相對路徑")
    args = parser.parse_args()

    print(f"[HOOK] verify_dqa_checklist_hook 開始執行...")
    
    if not os.path.exists(args.specs_dir):
        print(f"[WARNING] 找不到 {args.specs_dir} 目錄，預設通過。")
        sys.exit(0)
    
    spec_files = [f for f in os.listdir(args.specs_dir) if f.endswith('.md')]
    if not spec_files:
        print(f"[WARNING] {args.specs_dir} 內沒有 .md 檔案。")
        sys.exit(0)

    unchecked_pattern = re.compile(r'^\s*-\s*\[\s\]\s+', re.MULTILINE)
    has_error = False

    for f_name in spec_files:
        f_path = os.path.join(args.specs_dir, f_name)
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = unchecked_pattern.finditer(content)
                for match in matches:
                    if not has_error:
                        print(f"[RED LIGHT] 發現未完成的驗收項目 (Unchecked TO-DOs)：")
                        has_error = True
                    # 印出具體那一行
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1: line_end = len(content)
                    print(f"  ❌ [{f_name}] {content[line_start:line_end].strip()}")
        except Exception as e:
            print(f"[讀取失敗] {e}")

    if has_error:
        print("\n[ERROR] 驗收失敗！請 DQA 退回要求工程師修正，直到所有項目皆打勾 `[x]`。禁止提交報告！")
        sys.exit(1)
    else:
        print("\n[GREEN LIGHT] 所有 TO-DO 項目皆已驗收完畢，允許提交報告。")
        sys.exit(0)

if __name__ == '__main__':
    main()
