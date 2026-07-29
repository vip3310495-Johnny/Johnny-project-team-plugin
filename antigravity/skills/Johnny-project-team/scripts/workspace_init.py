import os
import sys
import shutil

# [AUTO-IMPLEMENTED] workspace_init
# Automatically scaffolds the workspace with the necessary hooks and scripts for the Johnny Project Team Plugin.

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("[HOOK] 🚀 執行 SessionStart 初始化：自動佈署專案級防護網...")

    workspace_dir = os.getcwd()
    plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    
    # Define paths
    src_skills = os.path.join(plugin_dir, "skills")
    src_rules = os.path.join(plugin_dir, "rules")
    src_agents_md = os.path.join(plugin_dir, "AGENTS.md")
    src_hooks_json = os.path.join(plugin_dir, "skills", "Johnny-project-team", "references", "templates", "hooks.json")
    
    dest_agents_dir = os.path.join(workspace_dir, ".agents")
    dest_skills = os.path.join(dest_agents_dir, "skills")
    dest_rules = os.path.join(dest_agents_dir, "rules")
    dest_agents_md = os.path.join(workspace_dir, "AGENTS.md")
    dest_hooks_json = os.path.join(dest_agents_dir, "hooks.json")

    if not os.path.exists(dest_agents_dir):
        os.makedirs(dest_agents_dir, exist_ok=True)
        print(f"[INFO] 建立目錄: {dest_agents_dir}")

    # Copy skills folder
    if os.path.exists(src_skills):
        shutil.copytree(src_skills, dest_skills, dirs_exist_ok=True)
        print(f"[INFO] 佈署 skills 至: {dest_skills}")
        
    # Copy AGENTS.md (Layer 1 Global Rules)
    dest_dot_agents_md = os.path.join(dest_agents_dir, "AGENTS.md")
    if os.path.exists(src_agents_md):
        shutil.copy2(src_agents_md, dest_agents_md)
        shutil.copy2(src_agents_md, dest_dot_agents_md)
        print(f"[INFO] 佈署 Layer 1 全域鐵律 (AGENTS.md) 至專案根目錄與 .agents/")

    # Copy hooks.json
    if os.path.exists(src_hooks_json):
        shutil.copy2(src_hooks_json, dest_hooks_json)
        print(f"[INFO] 佈署 Hooks 設定檔: {dest_hooks_json}")
    else:
        print(f"[ERROR] 找不到 Hooks 範本: {src_hooks_json}")

    # Generate or overwrite .gitignore for strict src/ whitelist
    gitignore_path = os.path.join(workspace_dir, ".gitignore")
    gitignore_content = """# Antigravity Native Gitignore - Only allow src/
*
!*/
!src/
!src/**
!.gitignore
"""
    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print(f"[INFO] 建立 Git 白名單隔離: {gitignore_path} (僅允許提交 src/)")
    except Exception as e:
        print(f"[WARN] 無法建立 .gitignore: {e}")

    print("[GREEN LIGHT] 專案防護網自動佈署完成。")
    sys.exit(0)

if __name__ == '__main__':
    main()
