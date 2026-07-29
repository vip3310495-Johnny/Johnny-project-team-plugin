import os
import subprocess
import sys
import pytest

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
PATH_GUARD = os.path.join(SCRIPTS_DIR, "path_guard.py")
GIT_GUARD = os.path.join(SCRIPTS_DIR, "git_guard.py")

@pytest.fixture
def mock_git_repo(tmp_path):
    """建立一個真實的 mock git 環境，並返回該路徑"""
    repo_dir = tmp_path / "mock_project"
    repo_dir.mkdir()
    
    # Initialize git
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    
    # Setup mock author
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    
    return repo_dir

def test_git_guard_blocks_without_allow_commit():
    """測試 git_guard.py 在沒有 ALLOW_COMMIT=1 時會被物理擋下"""
    env = os.environ.copy()
    if "ALLOW_COMMIT" in env:
        del env["ALLOW_COMMIT"]
        
    res = subprocess.run([sys.executable, GIT_GUARD], capture_output=True, text=True, env=env)
    assert res.returncode == 1
    assert "禁止 git commit" in res.stdout
    assert "物理限制攔截" in res.stdout

def test_git_guard_allows_with_allow_commit():
    """測試 git_guard.py 在有 ALLOW_COMMIT=1 時會放行 (PM 權限)"""
    env = os.environ.copy()
    env["ALLOW_COMMIT"] = "1"
        
    res = subprocess.run([sys.executable, GIT_GUARD], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "驗證通過" in res.stdout

def test_path_guard_allows_src_modifications(mock_git_repo):
    """測試 path_guard.py 允許 src/ 內的代碼變更"""
    src_dir = mock_git_repo / "src"
    src_dir.mkdir()
    
    test_file = src_dir / "main.py"
    test_file.write_text("print('hello')", encoding='utf-8')
    
    subprocess.run(["git", "add", "src/main.py"], cwd=mock_git_repo, check=True)
    
    # 執行 path_guard
    res = subprocess.run([sys.executable, PATH_GUARD], cwd=mock_git_repo, capture_output=True, text=True)
    assert res.returncode == 0
    assert "驗證通過" in res.stdout

def test_path_guard_allows_dqa_modifications(mock_git_repo):
    """測試 path_guard.py 允許 TDD_DQA/ 內的代碼變更"""
    dqa_dir = mock_git_repo / "TDD_DQA"
    dqa_dir.mkdir()
    
    test_file = dqa_dir / "test_report.py"
    test_file.write_text("assert True", encoding='utf-8')
    
    subprocess.run(["git", "add", "TDD_DQA/test_report.py"], cwd=mock_git_repo, check=True)
    
    res = subprocess.run([sys.executable, PATH_GUARD], cwd=mock_git_repo, capture_output=True, text=True)
    assert res.returncode == 0
    assert "驗證通過" in res.stdout

def test_path_guard_blocks_root_modifications(mock_git_repo):
    """測試 path_guard.py 攔截試圖寫在專案根目錄的業務邏輯代碼"""
    test_file = mock_git_repo / "main.py"
    test_file.write_text("print('hack')", encoding='utf-8')
    
    subprocess.run(["git", "add", "main.py"], cwd=mock_git_repo, check=True)
    
    res = subprocess.run([sys.executable, PATH_GUARD], cwd=mock_git_repo, capture_output=True, text=True)
    assert res.returncode == 1
    assert "物理限制攔截" in res.stdout
    assert "main.py" in res.stdout
