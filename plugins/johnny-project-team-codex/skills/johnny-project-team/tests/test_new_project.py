from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import johnny_new_project


def run_script(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "johnny_new_project.py"), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )


def git(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_new_project_creates_owned_layout_and_initializes_git(tmp_path: Path) -> None:
    project = tmp_path / "new-product"

    result = run_script("--project", str(project), "--name", "New Product")

    assert "Johnny 全新專案已初始化" in result.stdout
    expected_directories = {
        "src/app",
        "src/tests/unit",
        "src/tests/integration",
        "src/tests/regression",
        "src/tests/fixtures",
        "src/config",
        "src/migrations",
        "src/scripts",
        "TDD_DQA/tool",
        "TDD_DQA/evidence",
        "SDD_DQA/tool",
        "SDD_DQA/evidence",
        "Claude DQA/tool",
        "Claude DQA/evidence",
        "PM/Planning",
        "PM/PRD",
        "PM/Flows",
        "PM/DataFlows",
        "PM/Contracts",
        "PM/Context",
        "PM/Milestones",
        "PM/Changes",
        "PM/Approvals",
        "PM/tests",
        "Engineer",
        "Architect",
        "Logs",
        ".johnny",
        ".agents",
    }
    for relative in expected_directories:
        assert (project / relative).is_dir(), relative

    manifest = json.loads(
        (project / "src/delivery-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest == {
        "schema_version": 1,
        "product_name": "New Product",
        "delivery_root": "src/",
    }
    assert (project / "src/README.md").is_file()
    assert (project / ".gitignore").is_file()
    assert git(project, "branch", "--show-current").stdout.strip() == "main"
    assert git(project, "rev-parse", "--verify", "HEAD", check=False).returncode != 0

    visible = git(project, "status", "--short").stdout.splitlines()
    assert "?? .gitignore" in visible
    assert "?? src/" in visible
    assert all("TDD_DQA" not in line for line in visible)
    assert all("SDD_DQA" not in line for line in visible)
    assert all("PM/" not in line for line in visible)
    assert all("Engineer/" not in line for line in visible)


def test_new_project_refuses_nonempty_target(tmp_path: Path) -> None:
    project = tmp_path / "existing"
    project.mkdir()
    sentinel = project / "keep.txt"
    sentinel.write_text("do not overwrite\n", encoding="utf-8")

    result = run_script(
        "--project", str(project), "--name", "Existing", check=False
    )

    assert result.returncode != 0
    assert "目標必須不存在或為空目錄" in result.stderr
    assert sentinel.read_text(encoding="utf-8") == "do not overwrite\n"
    assert not (project / ".git").exists()


def test_new_project_refuses_blank_product_name(tmp_path: Path) -> None:
    project = tmp_path / "blank-name"

    result = run_script("--project", str(project), "--name", "   ", check=False)

    assert result.returncode != 0
    assert "產品名稱不得空白" in result.stderr
    assert not project.exists()


def test_new_project_cleans_staging_when_git_initialization_fails(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "failed-init"
    project.mkdir()

    def fail_git(_: Path) -> None:
        raise RuntimeError("simulated git failure")

    monkeypatch.setattr(johnny_new_project, "initialize_git", fail_git)

    with pytest.raises(RuntimeError, match="simulated git failure"):
        johnny_new_project.create_project(project, "Failed")

    assert project.is_dir()
    assert list(project.iterdir()) == []
    assert list(tmp_path.glob(".failed-init.johnny-*")) == []


def test_new_project_cleans_staging_when_interrupted(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "interrupted"

    def interrupt(_: Path) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(johnny_new_project, "initialize_git", interrupt)

    with pytest.raises(KeyboardInterrupt):
        johnny_new_project.create_project(project, "Interrupted")

    assert not project.exists()
    assert list(tmp_path.glob(".interrupted.johnny-*")) == []
