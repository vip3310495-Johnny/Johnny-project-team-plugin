import os
import subprocess
import sys

import pytest


SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
PATH_GUARD = os.path.join(SCRIPTS_DIR, "path_guard.py")
GIT_GUARD = os.path.join(SCRIPTS_DIR, "git_guard.py")


def run_guard(command, **kwargs):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1", **kwargs.pop("env", {})}
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, **kwargs)


@pytest.fixture
def mock_git_repo(tmp_path):
    repo_dir = tmp_path / "mock_project"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    return repo_dir


def test_git_guard_blocks_without_allow_commit():
    env = os.environ.copy()
    env.pop("ALLOW_COMMIT", None)
    result = run_guard([sys.executable, GIT_GUARD], env=env)
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout


def test_git_guard_allows_with_allow_commit():
    result = run_guard([sys.executable, GIT_GUARD], env={"ALLOW_COMMIT": "1"})
    assert result.returncode == 0
    assert "[GREEN LIGHT]" in result.stdout


def test_path_guard_allows_src_modifications(mock_git_repo):
    (mock_git_repo / "src").mkdir()
    (mock_git_repo / "src/main.py").write_text("print('hello')", encoding="utf-8")
    subprocess.run(["git", "add", "src/main.py"], cwd=mock_git_repo, check=True)
    result = run_guard([sys.executable, PATH_GUARD], cwd=mock_git_repo)
    assert result.returncode == 0
    assert "[GREEN LIGHT]" in result.stdout


def test_path_guard_allows_dqa_modifications(mock_git_repo):
    (mock_git_repo / "TDD_DQA").mkdir()
    (mock_git_repo / "TDD_DQA/test_report.py").write_text("assert True", encoding="utf-8")
    subprocess.run(["git", "add", "TDD_DQA/test_report.py"], cwd=mock_git_repo, check=True)
    result = run_guard([sys.executable, PATH_GUARD], cwd=mock_git_repo)
    assert result.returncode == 0
    assert "[GREEN LIGHT]" in result.stdout


def test_path_guard_blocks_root_modifications(mock_git_repo):
    (mock_git_repo / "main.py").write_text("print('hack')", encoding="utf-8")
    subprocess.run(["git", "add", "main.py"], cwd=mock_git_repo, check=True)
    result = run_guard([sys.executable, PATH_GUARD], cwd=mock_git_repo)
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout
    assert "main.py" in result.stdout
