from __future__ import annotations

import json
import os
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
    assert "Model Matrix: missing" in output["hookSpecificOutput"]["additionalContext"]
    assert "PM/Planning/Model_Recommendation_Matrix.md" in output["hookSpecificOutput"]["additionalContext"]
    after = sorted(path.relative_to(repo) for path in repo.rglob("*"))
    assert before == after


def test_session_context_reports_model_matrix_presence(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )
    (repo / "JOHNNY_PROJECT_RULES.md").write_text("Rules.\n", encoding="utf-8")
    (repo / "PM/Planning").mkdir(parents=True)
    (repo / "PM/Planning/Model_Recommendation_Matrix.md").write_text(
        "# Model recommendation matrix\n", encoding="utf-8"
    )

    result = run_hook("johnny_session_context.py", {"cwd": str(repo)})

    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Model Matrix: present" in context
    assert "Missing required context files: PM/Planning/Model_Recommendation_Matrix.md" not in context


def test_session_context_allows_matrix_creation_during_phase_zero(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".johnny/state.json").write_text(
        json.dumps({"phase": 0}), encoding="utf-8"
    )
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text("{}", encoding="utf-8")
    (repo / "JOHNNY_PROJECT_RULES.md").write_text(
        "<!-- johnny-project-contract-v4:start -->\n",
        encoding="utf-8",
    )

    result = run_hook("johnny_session_context.py", {"cwd": str(repo)})

    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "may be absent only while Phase 0 is creating it" in context
    assert "Missing required context files: PM/Planning/Model_Recommendation_Matrix.md" not in context


def test_subagent_context_attaches_matching_project_role_profile(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text("{}", encoding="utf-8")
    profile = repo / ".codex/agents/johnny-engineer.toml"
    profile.parent.mkdir(parents=True)
    profile.write_text(
        'name = "johnny_engineer"\ndeveloper_instructions = "工程師規則"\n',
        encoding="utf-8",
    )

    result = run_hook(
        "johnny_subagent_context.py",
        {"cwd": str(repo), "agent_type": "johnny_engineer"},
    )

    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert str(profile) in context
    assert 'name = "johnny_engineer"' in context


def test_subagent_context_blocks_johnny_role_without_matching_profile(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text("{}", encoding="utf-8")

    result = run_hook(
        "johnny_subagent_context.py",
        {"cwd": str(repo), "agent_type": "johnny_architect"},
    )

    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "[BLOCKED_PROFILE]" in output["additionalContext"]


def test_session_context_warns_instead_of_silently_truncating(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text("{}", encoding="utf-8")
    (repo / "JOHNNY_PROJECT_RULES.md").write_text(
        "<!-- johnny-project-contract-v4:start -->\n" + ("規則內容" * 2000),
        encoding="utf-8",
    )

    result = run_hook("johnny_session_context.py", {"cwd": str(repo)})

    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert len(context) <= 5600
    assert "[WARNING] SessionStart context exceeded" in context


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
    assert "codex-primary-runtime" in runner
    assert "where py" in runner
    assert "where python3" in runner
    assert "where python" in runner
    assert "johnny_python_fallback.ps1" in runner


def test_hook_analysis_does_not_claim_role_aware_write_sandbox() -> None:
    analysis = (
        HOOKS.parent
        / "skills"
        / "johnny-project-team"
        / "references"
        / "hook-lock-analysis.md"
    ).read_text(encoding="utf-8")

    assert "不會提供可靠的 Johnny agent role" in analysis
    assert "不是能辨識角色的檔案系統 sandbox" in analysis


def run_windows_runner(cwd: Path, *, python: Path | None) -> subprocess.CompletedProcess[str]:
    probe = cwd / "probe.py"
    probe.write_text("print('runner-ok')\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["USERPROFILE"] = str(cwd / "profile")
    environment["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    if python is None:
        environment.pop("CODEX_PYTHON", None)
    else:
        environment["CODEX_PYTHON"] = str(python)
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    command = f'& "{HOOKS / "johnny_python_runner.cmd"}" "{probe}"; exit $LASTEXITCODE'
    return subprocess.run(
        [str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_windows_runner_uses_codex_python_when_configured(tmp_path: Path) -> None:
    result = run_windows_runner(tmp_path, python=Path(sys.executable))

    assert result.returncode == 0
    assert "runner-ok" in result.stdout


def test_windows_runner_executes_session_start_hook_end_to_end(tmp_path: Path) -> None:
    repo = enabled_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents/context-manifest.json").write_text("{}", encoding="utf-8")
    (repo / "JOHNNY_PROJECT_RULES.md").write_text(
        "<!-- johnny-project-contract-v4:start -->\n",
        encoding="utf-8",
    )
    environment = {**os.environ, "CODEX_PYTHON": sys.executable, "PYTHONUTF8": "1"}
    powershell = (
        Path(os.environ["SystemRoot"])
        / "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    command = (
        f'& "{HOOKS / "johnny_python_runner.cmd"}" '
        f'"{HOOKS / "johnny_session_context.py"}"; exit $LASTEXITCODE'
    )
    result = subprocess.run(
        [
            str(powershell),
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            command,
        ],
        input=json.dumps({"cwd": str(repo), "source": "startup"}),
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Current Phase: 3" in context


def test_session_start_registration_covers_resume_and_has_headroom() -> None:
    hooks = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
    registration = hooks["hooks"]["SessionStart"][0]
    command = registration["hooks"][0]

    assert "startup" in registration["matcher"]
    assert "resume" in registration["matcher"]
    assert command["additionalContextLimit"] > 5600


def test_windows_runner_fails_open_without_enabled_project(tmp_path: Path) -> None:
    result = run_windows_runner(tmp_path, python=None)

    assert result.returncode == 0
    assert "no enabled Johnny repository" in result.stdout + result.stderr


def test_windows_runner_fails_closed_for_enabled_project(tmp_path: Path) -> None:
    repo = tmp_path / "project"
    marker = repo / ".johnny" / "enabled.json"
    marker.parent.mkdir(parents=True)
    marker.write_text(
        json.dumps({"enabled": True, "scope": str(repo.resolve())}),
        encoding="utf-8",
    )

    result = run_windows_runner(tmp_path, python=None)

    assert result.returncode != 0
    assert "cannot find Python for enabled repository" in result.stderr
