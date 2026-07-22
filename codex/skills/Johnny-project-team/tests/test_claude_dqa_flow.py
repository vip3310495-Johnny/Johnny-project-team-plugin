import importlib.util
import os
import subprocess
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
VERIFY_PHASE3 = SCRIPTS_DIR / "verify_all_dqa_passed_hook.py"
VERIFY_PHASE4 = SCRIPTS_DIR / "phase4_final_gate.py"
PHASE_GATE = SCRIPTS_DIR / "phase_gate_hook.py"
CLAUDE_DQA = SCRIPTS_DIR / "claude_dqa_hook.py"
STATUS_MANAGER = SCRIPTS_DIR / "dqa_status_manager.py"

spec = importlib.util.spec_from_file_location("dqa_status_manager", STATUS_MANAGER)
status_manager = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = status_manager
spec.loader.exec_module(status_manager)


def write_status(project_dir: Path, filename: str, values: dict) -> None:
    for role, status in values.items():
        status_manager.set_status(role, status, str(project_dir), filename)


def run(script: Path, project_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), "--project_dir", str(project_dir), *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_phase3_blocks_without_claude_evidence(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    write_status(project_dir, ".agents/.dqa_status.json", {"TDD": "PASS", "SDD": "PASS"})
    result = run(VERIFY_PHASE3, project_dir)
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout


def test_phase3_dqa_status_requires_tdd_sdd_claude_order(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    result = run(STATUS_MANAGER, project_dir, "--role", "SDD", "--status", "PASS")
    assert result.returncode == 1
    assert "TDD" in result.stdout
    assert run(STATUS_MANAGER, project_dir, "--role", "TDD", "--status", "PASS").returncode == 0
    result = run(STATUS_MANAGER, project_dir, "--role", "Claude", "--status", "PASS")
    assert result.returncode == 1
    assert "SDD" in result.stdout
    assert run(STATUS_MANAGER, project_dir, "--role", "SDD", "--status", "PASS").returncode == 0
    assert run(STATUS_MANAGER, project_dir, "--role", "Claude", "--status", "PASS").returncode == 0


def test_phase4_dqa_status_requires_tdd_sdd_claude_order(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    status_file = ".agents/.phase4_dqa_status.json"
    result = run(STATUS_MANAGER, project_dir, "--status_file", status_file, "--role", "SDD", "--status", "PASS")
    assert result.returncode == 1
    assert "TDD" in result.stdout
    assert run(STATUS_MANAGER, project_dir, "--status_file", status_file, "--role", "TDD", "--status", "PASS").returncode == 0
    assert run(STATUS_MANAGER, project_dir, "--status_file", status_file, "--role", "SDD", "--status", "PASS").returncode == 0
    assert run(STATUS_MANAGER, project_dir, "--status_file", status_file, "--role", "Claude", "--status", "PASS").returncode == 0


def test_phase4_blocks_without_claude_evidence(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    write_status(project_dir, ".agents/.phase4_dqa_status.json", {"TDD": "PASS", "SDD": "PASS"})
    result = run(VERIFY_PHASE4, project_dir)
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout


def test_claude_dqa_dry_run_never_invokes_external_cli(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    result = run(CLAUDE_DQA, project_dir, "--claude_command", "definitely-not-installed")
    assert result.returncode == 0
    assert "INFO" in result.stdout
    assert not (project_dir / "Claude DQA").exists()


def test_claude_dqa_execute_requires_cost_approval_id(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    result = run(CLAUDE_DQA, project_dir, "--execute", "--claude_command", "definitely-not-installed")
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout


def test_claude_dqa_rejects_unknown_cost_approval_id(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    result = run(CLAUDE_DQA, project_dir, "--execute", "--cost-approval-id", "not-in-ledger", "--claude_command", "definitely-not-installed")
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout
    assert not (project_dir / "Claude DQA").exists()


def test_malformed_status_file_fails_closed(tmp_path):
    project_dir = tmp_path / "project"
    (project_dir / ".agents").mkdir(parents=True)
    (project_dir / ".agents/.dqa_status.json").write_text("not json", encoding="utf-8")
    result = run(VERIFY_PHASE3, project_dir)
    assert result.returncode == 1
    assert "REJECTED" in result.stdout


def test_legacy_phase_gate_rejects_auto_and_ambiguous_approval(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    auto = subprocess.run([sys.executable, str(PHASE_GATE), "--from_phase", "0", "--to_phase", "1", "--auto"], cwd=project_dir, capture_output=True, text=True, encoding="utf-8")
    ambiguous = subprocess.run([sys.executable, str(PHASE_GATE), "--from_phase", "0", "--to_phase", "1", "--ceo_signature", "/approve"], cwd=project_dir, capture_output=True, text=True, encoding="utf-8")
    assert auto.returncode == 1
    assert ambiguous.returncode == 1
    assert '--auto' in auto.stdout
    assert 'phase0_exit' in ambiguous.stdout
    assert '--auto' in auto.stdout
    assert 'phase0_exit' in ambiguous.stdout


def test_existing_triple_dqa_evidence_is_accepted(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    write_status(project_dir, ".agents/.dqa_status.json", {"TDD": "PASS", "SDD": "PASS", "Claude": "PASS"})
    result = run(VERIFY_PHASE3, project_dir)
    assert result.returncode == 0, result.stdout + result.stderr
