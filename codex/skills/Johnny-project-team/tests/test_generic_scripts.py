import ast
import os
import subprocess
import glob
import sys
import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")

def get_dummy_args(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    tree = ast.parse(content)
    dummy_args = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'attr', '') == 'add_argument':
            arg_names = [arg.value for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
            if not arg_names:
                continue
                
            is_required = False
            is_positional = False
            
            if not arg_names[0].startswith('-'):
                is_positional = True
                is_required = True
                
            for keyword in node.keywords:
                if keyword.arg == 'required' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    is_required = True
            
            if is_required:
                arg_type = 'str'
                choices = None
                action_store_true = False
                for keyword in node.keywords:
                    if keyword.arg == 'type' and isinstance(keyword.value, ast.Name):
                        arg_type = keyword.value.id
                    elif keyword.arg == 'choices' and isinstance(keyword.value, ast.List):
                        choices = [elt.value for elt in keyword.value.elts if getattr(elt, 'value', None) is not None]
                    elif keyword.arg == 'action' and isinstance(keyword.value, ast.Constant) and keyword.value.value == 'store_true':
                        action_store_true = True
                
                if action_store_true:
                    if not is_positional:
                        dummy_args.append(arg_names[0])
                elif choices:
                    if not is_positional:
                        dummy_args.append(arg_names[0])
                    dummy_args.append(str(choices[0]))
                elif arg_type in ('int', 'float'):
                    if not is_positional:
                        dummy_args.append(arg_names[0])
                    dummy_args.append("1")
                else:
                    if not is_positional:
                        dummy_args.append(arg_names[0])
                    dummy_args.append("test_value")
    return dummy_args

# Discover all scripts
all_scripts = glob.glob(os.path.join(SCRIPTS_DIR, "*.py"))

# Exclude scripts that have dedicated complex tests
EXCLUDE_FROM_GENERIC = {
    'path_guard.py', 'git_guard.py', 'setup_hooks.py',
    'claude_dqa_hook.py', 'verify_all_dqa_passed_hook.py',
    'phase4_final_gate.py', 'dqa_status_manager.py',
    'phase_gate_hook.py',
    # 這些 CLI 需要具體的治理狀態與核准資料；由專屬治理測試覆蓋。
    'project_governance.py', 'verify_spec_approval_hook.py',
}

generic_scripts = [s for s in all_scripts if os.path.basename(s) not in EXCLUDE_FROM_GENERIC]

@pytest.mark.parametrize("script_path", generic_scripts, ids=lambda x: os.path.basename(x))
def test_generic_script_execution(script_path, tmp_path):
    basename = os.path.basename(script_path)
    
    # Phase 1: Help Check
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    res_help = subprocess.run([sys.executable, script_path, "--help"], cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    assert res_help.returncode == 0, f"Help check failed: {res_help.stderr}"
    
    # Phase 2: Parse dummy args
    dummy_args = get_dummy_args(script_path)
    
    # Phase 3: Execute
    cmd = [sys.executable, script_path] + dummy_args
    
    # Override dummy args for specific scripts
    if basename == 'log_aggregator.py':
        source_log = tmp_path / "input.md"
        source_log.write_text("測試記錄", encoding="utf-8")
        cmd = [sys.executable, script_path, "--input", str(source_log), "--master_log", str(tmp_path / "Logs" / "Master_Log.md")]
    elif basename == 'verify_architecture_report_hook.py':
        report = tmp_path / "Architect" / "As_Built_Architecture.md"
        report.parent.mkdir()
        report.write_text("Architecture\nStructure\nModule\n" + ("x" * 900), encoding="utf-8")
        cmd = [sys.executable, script_path, "--report-path", str(report)]
    elif basename == 'verify_spec_approval_hook.py':
        cmd = [sys.executable, script_path, "--ceo_signature", "/approve"]
    elif basename == 'verify_lesson_hook.py':
        cmd = [sys.executable, script_path, "--role", "PM", "--proposal", "這是一個很棒的測試教訓提案，我們必須遵守SOP防呆防範未來的錯誤發生"]
        
    res_exec = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    assert res_exec.returncode == 0, f"Execution failed: {res_exec.stderr or res_exec.stdout}"
