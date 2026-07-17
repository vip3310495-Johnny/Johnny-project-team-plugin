import argparse
import subprocess
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
import os

# 目錄隔離防線 (Pre-commit Hook)

def main():
    parser = argparse.ArgumentParser(description="目錄隔離守門員 (Path Guard)")
    args = parser.parse_args()

    print("[HOOK] path_guard.py 開始執行...")
    
    # 取得 staged files
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        print("[WARN] 非 git 專案或無法取得 staged files，跳過 path_guard 檢查。")
        sys.exit(0)
    
    if not files:
        sys.exit(0)
        
    code_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.cpp', '.c', '.rs', '.php', '.rb')
    allowed_dirs = ('src/', 'tests/', 'TDD_DQA/', 'SDD_DQA/', 'scripts/', '.agents/')
    
    allowed_root_files = ('setup.py', 'manage.py', 'run.py', 'test.py')
    
    for f in files:
        if f.endswith(code_extensions):
            # 檢查是否在允許的目錄內
            is_allowed = any(f.startswith(d) for d in allowed_dirs)
            is_root_allowed = "/" not in f and f in allowed_root_files
            
            # 若不在允許目錄，且不是特例
            if not is_allowed and not is_root_allowed:
                print(f"\n[FAIL] 🛑 物理限制攔截 (path_guard):")
                print(f"發現業務代碼 `{f}` 試圖被寫入 `src/` 之外！")
                print("Engineer 被物理限制只能在 `src/` 目錄下進行開發。")
                print("請遵守【目錄隔離】鐵律，將代碼移至合法的目錄內。\n")
                sys.exit(1)

    print("[GREEN LIGHT] path_guard 驗證通過。未發現越界代碼。")
    sys.exit(0)

if __name__ == '__main__':
    main()
