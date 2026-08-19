"""為全新專案建立 Johnny 標準目錄並初始化 Git。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PRODUCT_DIRECTORIES = (
    "src/app",
    "src/tests/unit",
    "src/tests/integration",
    "src/tests/regression",
    "src/tests/fixtures",
    "src/config",
    "src/migrations",
    "src/scripts",
)

PROCESS_DIRECTORIES = (
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
)

GITIGNORE = """# Johnny 開發流程產物（僅限本機，不屬於產品交付）
/.johnny/
/.agents/
/.codex/
/JOHNNY_PROJECT_RULES.md
/PM/
/Engineer/
/Architect/
/TDD_DQA/
/SDD_DQA/
/Claude DQA/
/Logs/

# 常見本機快取與機密
/.env
/.env.*
!.env.example
/.venv/
/venv/
/node_modules/
/.pytest_cache/
/__pycache__/
*.py[cod]
*.log
"""

SRC_README = """# 產品交付根目錄

建置、測試、設定、migration 與執行產品所需的一切都放在此目錄。
Engineer 負責此處的應用程式與永久自動測試。產品交付 commit 只包含 `src/`。
"""


def run_git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def initialize_git(project: Path) -> None:
    if shutil.which("git") is None:
        raise RuntimeError("需要 Git，但在 PATH 中找不到")
    result = run_git(project, "init", "--initial-branch", "main")
    if result.returncode != 0:
        fallback = run_git(project, "init")
        if fallback.returncode != 0:
            raise RuntimeError(f"git init 失敗：{fallback.stderr.strip()}")
        branch = run_git(project, "symbolic-ref", "HEAD", "refs/heads/main")
        if branch.returncode != 0:
            raise RuntimeError(
                f"無法將初始分支設為 main：{branch.stderr.strip()}"
            )


def populate_project(project: Path, product_name: str) -> None:
    for relative in PRODUCT_DIRECTORIES + PROCESS_DIRECTORIES:
        (project / relative).mkdir(parents=True, exist_ok=True)
    for relative in PRODUCT_DIRECTORIES:
        (project / relative / ".gitkeep").write_text("", encoding="utf-8")

    (project / ".gitignore").write_text(GITIGNORE, encoding="utf-8", newline="\n")
    (project / "src" / "README.md").write_text(
        SRC_README, encoding="utf-8", newline="\n"
    )
    (project / "src" / "delivery-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "product_name": product_name,
                "delivery_root": "src/",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    initialize_git(project)


def create_project(project: Path, product_name: str) -> None:
    project = project.resolve()
    if not product_name:
        raise ValueError("產品名稱不得空白")
    if project.exists() and any(project.iterdir()):
        raise RuntimeError(f"目標必須不存在或為空目錄：{project}")
    if shutil.which("git") is None:
        raise RuntimeError("需要 Git，但在 PATH 中找不到")

    target_was_empty_directory = project.exists()
    project.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{project.name}.johnny-", dir=project.parent)
    )
    try:
        populate_project(staging, product_name)
        if project.exists():
            project.rmdir()
        staging.replace(project)
    except BaseException:
        try:
            shutil.rmtree(staging)
        finally:
            if target_was_empty_directory and not project.exists():
                project.mkdir()
        raise

    print(f"Johnny 全新專案已初始化：{project}")
    print("Git 分支：main（尚未建立 commit）")
    print("下一步：檢查骨架，然後只提交 .gitignore 與 src/。")
    print("建立乾淨的初始 commit 後，再啟用 Johnny repository gates。")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="建立全新 Johnny 專案骨架並初始化 Git。"
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    create_project(args.project, args.name.strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"johnny_new_project：{exc}", file=sys.stderr)
        raise SystemExit(1)
