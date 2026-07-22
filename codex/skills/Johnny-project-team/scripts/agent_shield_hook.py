import argparse
import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# AgentShield 安全護欄自檢 Hook，掃描危險指令與機密外洩 (references/phases/phase2.md, phase3.md)


def main():
    parser = argparse.ArgumentParser(description="AgentShield 安全護欄自檢 Hook")
    parser.add_argument("--project_dir", default=".", help="待掃描的專案根目錄")
    parser.add_argument("--policy", default="org_security_policy.json", help="組織安全規則檔路徑")
    args = parser.parse_args()

    print("[HOOK] agent_shield_hook 開始執行...")
    
    import os
    import glob

    project_dir = os.path.abspath(args.project_dir)
    print(f"[HOOK] 掃描目錄: {project_dir}")
    
    # 基礎的黑名單特徵碼
    # 注意：這些規則僅為示範防護，正式環境應替換為 Bandit 或 Semgrep 等專業掃描器
    blacklisted_patterns = [
        "rm -rf",
        "mkfs",
        "drop table",
        "os.system(",
        "eval("
    ]

    # 掃描涵蓋 path_guard.py 允許的所有目錄，消滅雷達死角
    scan_dirs = [
        os.path.join(project_dir, "src"), 
        os.path.join(project_dir, "scripts"),
        os.path.join(project_dir, "tests"),
        os.path.join(project_dir, "TDD_DQA"),
        os.path.join(project_dir, "SDD_DQA"),
        os.path.join(project_dir, ".agents")
    ]
    violations = []

    for d in scan_dirs:
        if not os.path.exists(d):
            continue
        for root, dirs, files in os.walk(d):
            for file in files:
                if not file.endswith(('.py', '.js', '.ts', '.sh', '.bash', '.sql')):
                    continue
                
                filepath = os.path.join(root, file)
                
                # 白名單過濾機制升級：必須精準匹配 scripts 目錄下的正牌腳本，杜絕工程師的同名偽裝攻擊
                rel_path = os.path.relpath(filepath, project_dir).replace("\\", "/")
                if rel_path == "scripts/agent_shield_hook.py":
                    continue
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line_num, line in enumerate(lines, 1):
                            line_lower = line.lower()
                            # 忽略註解
                            if line.strip().startswith('#') or line.strip().startswith('//'):
                                continue
                                
                            for pattern in blacklisted_patterns:
                                if pattern in line_lower:
                                    violations.append(f"檔案: {os.path.relpath(filepath, project_dir)} (行 {line_num}) -> 發現危險特徵碼: '{pattern}'")
                except Exception as e:
                    print(f"[WARN] 無法讀取檔案 {filepath}: {e}")

    if violations:
        print(f"\n[FAIL] 🛑 AgentShield 偵測到嚴重安全威脅！")
        print("發現以下具有高度破壞性的惡意代碼或高風險函數呼叫：")
        for v in violations:
            print(f"  - {v}")
        print("\n已強制攔截，請立刻修正代碼並移除這些高風險操作！")
        sys.exit(1)

    print("[GREEN LIGHT] agent_shield_hook 通過安全掃描。")
    sys.exit(0)


if __name__ == "__main__":
    main()
