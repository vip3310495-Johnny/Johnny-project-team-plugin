import os
import sys
import argparse
import glob

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def main():
    parser = argparse.ArgumentParser(description="Auto Load Layer 2 Rules Hook")
    parser.add_argument("--project_dir", default=".", help="專案根目錄")
    parser.add_argument("--tech_stack", default="", help="要加載的技術棧規則名稱 (例如 python, react)")
    args = parser.parse_args()

    if not args.tech_stack:
        print("[INFO] 未指定 --tech_stack 參數，跳過 Layer 2 規則載入。")
        sys.exit(0)

    tech = args.tech_stack.lower().strip()
    project_dir = os.path.abspath(args.project_dir)
    plugin_base = os.path.join(project_dir, ".agents", "skills", "Johnny-project-team")
    
    # 搜尋技術棧規則路徑
    tech_dir = os.path.join(plugin_base, "references", "rules", tech)
    single_file = os.path.join(plugin_base, "references", "rules", f"{tech}.md")
    
    # Fallback to local plugin if running directly
    if not os.path.exists(tech_dir) and not os.path.exists(single_file):
        tech_dir = os.path.join(project_dir, "skills", "Johnny-project-team", "references", "rules", tech)
        single_file = os.path.join(project_dir, "skills", "Johnny-project-team", "references", "rules", f"{tech}.md")

    print(f"[HOOK] 🚀 執行 Layer 2 動態規則加載：技術棧 = {tech}...")

    dev_contents = []
    review_contents = []

    review_keywords = ["testing", "review", "audit", "qa", "architecture"]

    if os.path.isdir(tech_dir):
        for file_path in sorted(glob.glob(os.path.join(tech_dir, "*.md"))):
            fname = os.path.basename(file_path).lower()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 如果內含 YAML frontmatter，剝離 Header
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                if any(kw in fname for kw in review_keywords):
                    review_contents.append(f"## [{fname}]\n\n{content}")
                else:
                    dev_contents.append(f"## [{fname}]\n\n{content}")
            except Exception as e:
                print(f"[WARN] 讀取規則檔 {file_path} 失敗: {e}")

    elif os.path.exists(single_file):
        try:
            with open(single_file, "r", encoding="utf-8") as f:
                content = f.read()
            dev_contents.append(content)
        except Exception as e:
            print(f"[WARN] 讀取規則單檔 {single_file} 失敗: {e}")
    else:
        print(f"[WARN] 找不到技術棧 [{tech}] 的對應規則目錄或檔案。")
        sys.exit(0)

    dest_rules_dir = os.path.join(project_dir, ".agents", "rules")
    os.makedirs(dest_rules_dir, exist_ok=True)

    # 1. 生成 dev_rules.md
    dev_header = f"""---
name: dev_rules
type: coding
tech_stack: {tech}
description: "Layer 2 - {tech.upper()} 開發與 Coding Style 指南"
---

# {tech.upper()} 開發寫 Code 規範 (Layer 2)

"""
    dev_file_path = os.path.join(dest_rules_dir, "dev_rules.md")
    with open(dev_file_path, "w", encoding="utf-8") as f:
        f.write(dev_header + "\n\n".join(dev_contents))
    print(f"[HOOK] 🟢 成功生成 Layer 2 開發規範: {dev_file_path} (帶 YAML Header)")

    # 2. 生成 review_rules.md
    review_header = f"""---
name: review_rules
type: review
tech_stack: {tech}
description: "Layer 2 - {tech.upper()} 代碼與架構 Review 指南"
---

# {tech.upper()} 審查與 Review 規範 (Layer 2)

"""
    review_file_path = os.path.join(dest_rules_dir, "review_rules.md")
    with open(review_file_path, "w", encoding="utf-8") as f:
        f.write(review_header + "\n\n".join(review_contents))
    print(f"[HOOK] 🟢 成功生成 Layer 2 審查規範: {review_file_path} (帶 YAML Header)")

    print("[SUCCESS] Layer 2 雙軌規則拆分加載完成，Layer 1 (AGENTS.md) 保持完全獨立！")

if __name__ == '__main__':
    main()
