from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[3] / "hooks"


def run_hook(name: str, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def enabled_repo(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    git(tmp_path, "init")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / ".johnny").mkdir()
    (tmp_path / ".johnny/enabled.json").write_text(
        json.dumps({"enabled": True, "scope": str(tmp_path.resolve())}),
        encoding="utf-8",
    )
    (tmp_path / ".johnny/state.json").write_text(
        json.dumps({"phase": 3}), encoding="utf-8"
    )
    return tmp_path


def test_tool_guard_blocks_write_on_main(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    git(repo, "switch", "-c", "main")
    result = run_hook(
        "johnny_tool_guard.py",
        {
            "cwd": str(repo),
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": "*** Begin Patch"},
        },
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_session_context_is_read_only_and_reports_phase(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )
    (repo / "JOHNNY_PROJECT_RULES.md").write_text("Read the task pack.\n", encoding="utf-8")
    before = sorted(path.relative_to(repo) for path in repo.rglob("*"))
    result = run_hook(
        "johnny_session_context.py",
        {
            "cwd": str(repo),
            "hook_event_name": "SessionStart",
            "source": "startup",
        },
    )
    output = json.loads(result.stdout)
    assert "Current Phase: 3" in output["hookSpecificOutput"]["additionalContext"]
    after = sorted(path.relative_to(repo) for path in repo.rglob("*"))
    assert before == after


def test_session_context_resolves_one_enabled_child_repository(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path / "Project")
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )
    (repo / "JOHNNY_PROJECT_RULES.md").write_text("Rules.\n", encoding="utf-8")

    result = run_hook("johnny_session_context.py", {"cwd": str(tmp_path)})

    output = json.loads(result.stdout)
    assert str(repo) in output["hookSpecificOutput"]["additionalContext"]


def test_tool_guard_resolves_enabled_child_repository(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path / "Project")
    git(repo, "switch", "-c", "main")

    result = run_hook(
        "johnny_tool_guard.py",
        {
            "cwd": str(tmp_path),
            "tool_name": "apply_patch",
            "tool_input": {"command": "*** Begin Patch"},
        },
    )

    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_session_context_reports_ambiguous_enabled_children(tmp_path: Path) -> None:
    enabled_repo(tmp_path / "first")
    enabled_repo(tmp_path / "second")

    result = run_hook("johnny_session_context.py", {"cwd": str(tmp_path)})

    output = json.loads(result.stdout)
    assert "ambiguous" in output["hookSpecificOutput"]["additionalContext"]


def test_session_context_can_succeed_after_repository_is_enabled(tmp_path: Path) -> None:
    before = run_hook("johnny_session_context.py", {"cwd": str(tmp_path)})
    assert before.stdout == ""

    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )
    (repo / "JOHNNY_PROJECT_RULES.md").write_text("Rules.\n", encoding="utf-8")
    after = run_hook("johnny_session_context.py", {"cwd": str(repo)})

    assert "Current Phase: 3" in json.loads(after.stdout)["hookSpecificOutput"][
        "additionalContext"
    ]


def test_windows_hooks_use_portable_python_runner() -> None:
    hooks = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
    runner = (HOOKS / "johnny_python_runner.cmd").read_text(encoding="utf-8")

    for event in ("SessionStart", "SubagentStart", "PreToolUse"):
        command = hooks["hooks"][event][0]["hooks"][0]["commandWindows"]
        assert "johnny_python_runner.cmd" in command
        assert "py -3" not in command
    assert "CODEX_PYTHON" in runner
    assert "where py" in runner
    assert "where python3" in runner
    assert "where python" in runner
