import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
import os
import shutil
import stat

# 安裝 Git Hooks (將 Guard 腳本綁定到專案的物理層)

def main():
    parser = argparse.ArgumentParser(description="Git Hooks 自動綁定腳本")
    parser.add_argument("--project_dir", default=".", help="目標專案根目錄 (必須包含 .git 資料夾)")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    git_hooks_dir = os.path.join(project_dir, ".git", "hooks")

    print("[HOOK] setup_hooks.py 開始執行...")
    
    if not os.path.exists(git_hooks_dir):
        print(f"[WARN] 專案目錄 {project_dir} 尚未初始化 Git (.git/hooks 不存在)。")
        print("請先執行 `git init`，然後再次執行此腳本。")
        sys.exit(0)

    # 目前腳本所在的絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_guard_path = os.path.join(current_dir, "path_guard.py")
    git_guard_path = os.path.join(current_dir, "git_guard.py")

    pre_commit_path = os.path.join(git_hooks_dir, "pre-commit")

    # 建立 pre-commit hook 內容
    # 執行順序: 先跑 git_guard (確認權限)，再跑 path_guard (確認目錄)
    hook_content = f"""#!/bin/sh
# Johnny-project-team Auto-generated Pre-commit Hook

echo "[Git Hook] 觸發 Antigravity 物理防線..."

# 1. 驗證 Git Commit 權限 (git_guard.py)
python "{git_guard_path}"
if [ $? -ne 0 ]; then
    exit 1
fi

# 2. 驗證目錄隔離 (path_guard.py)
python "{path_guard_path}"
if [ $? -ne 0 ]; then
    exit 1
fi

exit 0
"""

    try:
        with open(pre_commit_path, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # 賦予執行權限 (適用於 Linux/Mac/Git Bash)
        st = os.stat(pre_commit_path)
        os.chmod(pre_commit_path, st.st_mode | stat.S_IEXEC)
        
        print(f"[SUCCESS] 物理限制掛載完成！已綁定 pre-commit hook 至 {pre_commit_path}")
        print("[GREEN LIGHT] setup_hooks 執行完畢。")
        sys.exit(0)
    except Exception as e:
        print(f"[FAIL] 無法寫入 Hook 檔案：{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
