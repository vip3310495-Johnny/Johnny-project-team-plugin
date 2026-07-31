from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from johnny_common import state_lock
import johnny_guard
from te_dispatch_plan import calculate_plan


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("initial\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "initial")
    return tmp_path


def run_script(name: str, *args: str, check: bool = True):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )


def phase_evidence(repo: Path, to_phase: int) -> Path:
    common = {"schema_version": 1, "to_phase": to_phase}
    if to_phase == 1:
        common.update(
            {
                "intent": ["intent"],
                "non_goals": ["non-goal"],
                "observable_outcomes": ["outcome"],
                "risks": ["risk"],
            }
        )
    elif to_phase == 3:
        common.update(
            {
                "scope_contract_matrix": ["PM/Phase_Contract_Matrix.md"],
                "milestones": ["M01"],
                "task_context_packs": ["PM/Context/M01.md"],
                "model_matrix": [
                    {
                        "role": role,
                        "model": "test-model",
                        "availability": "AVAILABLE",
                        "approved_by": "CEO",
                    }
                    for role in ("PM", "Architect", "Engineer", "TDD DQA", "SDD DQA")
                ],
            }
        )
    else:
        common.update(
            {
                "integrated_tdd": "PASS",
                "integrated_sdd": "PASS",
                "fixed_tolerance_evidence": ["TDD_DQA/final.md"],
                "as_built_inputs": ["PM/ledger.md"],
            }
        )
    path = repo / f"phase-{to_phase}-evidence.json"
    path.write_text(json.dumps(common), encoding="utf-8")
    return path


def test_enable_is_repo_local_and_disable_restores(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    assert git(repo, "config", "--local", "--get", "core.hooksPath").stdout.strip() == ".johnny/git-hooks"
    marker = json.loads((repo / ".johnny/enabled.json").read_text(encoding="utf-8"))
    assert marker["scope"] == str(repo.resolve())
    assert (repo / ".johnny/git-hooks/pre-commit").is_file()
    assert (repo / ".codex/agents/johnny-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-sdd-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-tdd-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-security-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-log-agent.toml").is_file()
    assert (repo / ".codex/agents/johnny-te.toml").is_file()
    assert (repo / ".codex/agents/johnny-pm.toml").is_file()
    assert (repo / ".codex/agents/johnny-engineer.toml").is_file()
    assert (repo / ".codex/agents/johnny-architect.toml").is_file()
    assert (repo / "JOHNNY_PROJECT_RULES.md").is_file()
    assert (repo / ".agents/context-manifest.json").is_file()
    manifest = json.loads(
        (repo / ".agents/context-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["routes"]["tdd_method"].startswith("references/tdd-integration.md")
    config = json.loads((repo / ".johnny/config.json").read_text(encoding="utf-8"))
    assert config["claude_dqa"] == {
        "enabled": False,
        "required": False,
        "manual_allowed": True,
    }
    assert config["dqa_required_from_phase"] == 3
    assert config["dqa_required_phases"] == [3, 4]
    assert config["schema_version"] == 3
    assert config["product_root"] == "src/"
    assert config["allowed_code_roots"] == ["src/"]
    assert config["product_paths"] == ["src/"]
    assert config["phase3_commit_roots"] == ["src/"]
    assert config["dqa_workspaces"]["tdd"]["tool"] == "TDD_DQA/tool/"
    assert config["dqa_workspaces"]["sdd"]["tool"] == "SDD_DQA/tool/"
    assert config["dqa_workspaces"]["claude"]["tool"] == "Claude DQA/tool/"
    assert config["te_orchestration"]["max_concurrent_per_dqa"] == 2
    assert config["scope_contract"] == {
        "levels": ["FIXED", "CONTROLLED", "DISCRETIONARY"],
        "classification_owner": "PM",
        "classification_challenges_per_item": 1,
        "dqa_intervenes_in_phase3": True,
        "controlled_requires_approval": False,
        "phase4_tests_compatibility": True,
    }
    assert config["ticket_flow"] == {
        "style": "tracer-bullet",
        "milestone_ticket_cardinality": "one-to-one",
        "max_active_phase3_tickets": 1,
        "requires_dependency_edges": True,
        "required_dqa_order": ["tdd", "sdd"],
        "claude_dqa_mode": "manual",
        "execution_policy_choices": ["SUPERVISED", "AUTONOMOUS"],
        "execution_policy_selected_at_phase": 2,
        "requires_user_review_each_ticket": "by-policy",
        "unlock_next_after_approval": "by-policy",
    }
    assert config["dqa_escalation"] == {
        "max_rejections_per_role_per_milestone": 5,
        "count_scope": "milestone-and-dqa-role",
        "action": "freeze-and-escalate-to-ceo",
    }
    assert config["ecc_rules"] == {
        "enabled": True,
        "selector": "johnny_ecc_rules.py",
        "selection_schema_version": 2,
        "selection_manifest": ".johnny/ecc-selection.json",
        "common_always": True,
        "require_every_selected_file": True,
    }
    manifest = json.loads(
        (repo / ".agents/context-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["ecc_rules"]["supported_rule_sets"] == [
        "common",
        "angular",
        "arkts",
        "cpp",
        "csharp",
        "dart",
        "fsharp",
        "golang",
        "java",
        "kotlin",
        "nuxt",
        "perl",
        "php",
        "python",
        "react",
        "react-native",
        "ruby",
        "rust",
        "swift",
        "typescript",
        "vue",
        "web",
    ]
    assert manifest["product_layout"] == {
        "delivery_root": "src/",
        "permanent_tests": "src/tests/",
        "phase3_commit_roots": ["src/"],
        "dqa_tool_roots": {
            "tdd": "TDD_DQA/tool/",
            "sdd": "SDD_DQA/tool/",
            "claude": "Claude DQA/tool/",
        },
        "te_write_access": False,
    }
    run_script("johnny_project_hooks.py", "disable", "--project", str(repo))
    result = git(repo, "config", "--local", "--get", "core.hooksPath", check=False)
    assert result.returncode != 0


def test_lock_times_out_instead_of_deadlocking(repo: Path) -> None:
    (repo / ".johnny").mkdir()
    with state_lock(repo):
        with pytest.raises(TimeoutError):
            with state_lock(repo, timeout=0.1):
                pass


def test_phase_requires_one_step_and_approval(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    rejected = run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "2",
        "--approval", "approved",
        check=False,
    )
    assert rejected.returncode != 0
    run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "1",
        "--approval", "User explicitly approved phase 1",
        "--evidence", str(phase_evidence(repo, 1)),
    )
    state = json.loads((repo / ".johnny/state.json").read_text(encoding="utf-8"))
    assert state["phase"] == 1


def test_phase2_requires_execution_policy_for_phase3(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    for phase in (1, 2):
        arguments = [
            "--project", str(repo),
            "--to-phase", str(phase),
            "--approval", f"CEO approved phase {phase}",
        ]
        if phase == 1:
            arguments.extend(["--evidence", str(phase_evidence(repo, 1))])
        run_script(
            "johnny_phase_gate.py",
            *arguments,
        )
    missing = run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "3",
        "--approval", "CEO approved construction",
        check=False,
    )
    assert missing.returncode != 0
    assert "requires --execution-policy" in missing.stderr
    run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "3",
        "--execution-policy", "AUTONOMOUS",
        "--approval", "CEO delegated autonomous Milestone approval",
        "--evidence", str(phase_evidence(repo, 3)),
    )
    state = json.loads((repo / ".johnny/state.json").read_text(encoding="utf-8"))
    assert state["execution_policy"]["mode"] == "AUTONOMOUS"
    assert state["execution_policy"]["delegated_by"] == "CEO"


def test_phase3_rejects_unavailable_or_unapproved_model_matrix(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "1",
        "--approval", "approved",
        "--evidence", str(phase_evidence(repo, 1)),
    )
    run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "2",
        "--approval", "approved",
    )
    evidence = json.loads(phase_evidence(repo, 3).read_text(encoding="utf-8"))
    evidence["model_matrix"][0]["availability"] = "UNKNOWN"
    path = repo / "invalid-model-matrix.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")
    rejected = run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "3",
        "--execution-policy", "AUTONOMOUS",
        "--approval", "approved",
        "--evidence", str(path),
        check=False,
    )
    assert rejected.returncode != 0
    assert "availability=AVAILABLE" in rejected.stderr


def test_guard_fails_open_without_activation(repo: Path) -> None:
    result = run_script(
        "johnny_guard.py",
        "--project", str(repo),
        "--event", "pre-commit",
        check=False,
    )
    assert result.returncode == 0


def test_physical_pre_commit_hook_blocks_disallowed_code_path(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    (repo / "outside.py").write_text("print('blocked')\n", encoding="utf-8")
    git(repo, "add", "outside.py")
    result = git(repo, "commit", "-m", "must be blocked", check=False)
    assert result.returncode != 0
    assert "outside allowed roots" in (result.stdout + result.stderr)


def test_existing_project_hook_is_chained_and_restored(repo: Path) -> None:
    old_hooks = repo / "existing-hooks"
    old_hooks.mkdir()
    old_hook = old_hooks / "pre-commit"
    old_hook.write_text(
        "#!/bin/sh\n"
        'echo chained > "$(git rev-parse --show-toplevel)/existing-hook-ran"\n',
        encoding="utf-8",
        newline="\n",
    )
    old_hook.chmod(old_hook.stat().st_mode | 0o111)
    git(repo, "config", "--local", "core.hooksPath", "existing-hooks")

    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    (repo / "README.md").write_text("allowed\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "runs both hooks")
    assert (repo / "existing-hook-ran").read_text(encoding="utf-8").strip() == "chained"

    run_script("johnny_project_hooks.py", "disable", "--project", str(repo))
    assert git(repo, "config", "--local", "--get", "core.hooksPath").stdout.strip() == "existing-hooks"


def test_enable_is_idempotent_and_does_not_chain_itself(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    first = (repo / ".johnny/git-hooks/pre-commit").read_text(encoding="utf-8")
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    second = (repo / ".johnny/git-hooks/pre-commit").read_text(encoding="utf-8")
    assert first == second
    assert second.count("johnny_guard.py") == 1
    assert '".johnny/git-hooks/pre-commit"' not in second


def test_enable_requires_clean_initial_commit(tmp_path: Path) -> None:
    git(tmp_path, "init")
    result = run_script(
        "johnny_project_hooks.py", "enable", "--project", str(tmp_path), check=False
    )
    assert result.returncode != 0
    assert "clean initial commit" in result.stderr


@pytest.mark.parametrize(
    ("requested", "active", "spawn", "queued"),
    [
        (3, 2, 2, 1),
        (3, 3, 1, 2),
        (2, 4, 0, 2),
        (1, 2, 1, 0),
    ],
)
def test_te_capacity_respects_session_and_per_dqa_limits(
    requested: int, active: int, spawn: int, queued: int
) -> None:
    plan = calculate_plan(requested, active)
    assert plan["spawn_now"] == spawn
    assert plan["queue"] == queued


def test_te_dispatch_refuses_while_state_lock_is_held(repo: Path) -> None:
    (repo / ".johnny").mkdir()
    with state_lock(repo):
        result = run_script(
            "te_dispatch_plan.py",
            "--project", str(repo),
            "--requested", "2",
            "--active-agents", "2",
            check=False,
        )
    assert result.returncode != 0
    assert "state lock timed out" in result.stderr


def test_enable_refuses_to_overwrite_custom_agent(repo: Path) -> None:
    target = repo / ".codex/agents/johnny-te.toml"
    target.parent.mkdir(parents=True)
    target.write_text("user-owned = true\n", encoding="utf-8")
    result = run_script(
        "johnny_project_hooks.py", "enable", "--project", str(repo), check=False
    )
    assert result.returncode != 0
    assert target.read_text(encoding="utf-8") == "user-owned = true\n"
    assert git(repo, "config", "--local", "--get", "core.hooksPath", check=False).returncode != 0


def test_agent_responsibilities_match_scope_contract() -> None:
    agents = SCRIPTS.parent / "assets" / "agents"
    pm = tomllib.loads((agents / "johnny-pm.toml").read_text(encoding="utf-8"))
    engineer = tomllib.loads(
        (agents / "johnny-engineer.toml").read_text(encoding="utf-8")
    )
    dqa = tomllib.loads((agents / "johnny-dqa.toml").read_text(encoding="utf-8"))
    sdd = tomllib.loads((agents / "johnny-sdd-dqa.toml").read_text(encoding="utf-8"))
    tdd = tomllib.loads((agents / "johnny-tdd-dqa.toml").read_text(encoding="utf-8"))
    security = tomllib.loads(
        (agents / "johnny-security-dqa.toml").read_text(encoding="utf-8")
    )
    log_agent = tomllib.loads(
        (agents / "johnny-log-agent.toml").read_text(encoding="utf-8")
    )
    te = tomllib.loads((agents / "johnny-te.toml").read_text(encoding="utf-8"))
    architect = tomllib.loads(
        (agents / "johnny-architect.toml").read_text(encoding="utf-8")
    )

    assert "You alone make the initial and final classification" in pm["developer_instructions"]
    assert "notify PM immediately" in engineer["developer_instructions"]
    assert "TDD DQA, then SDD DQA" in engineer["developer_instructions"]
    assert "johnny_ecc_rules.py" in engineer["developer_instructions"]
    assert "per-ticket" in dqa["description"]
    assert "backward-compatibility testing" in dqa["developer_instructions"]
    assert "only after TDD DQA has" in sdd["developer_instructions"]
    assert "johnny_ecc_rules.py" in sdd["developer_instructions"]
    assert "do\nnot unlock SDD" in tdd["developer_instructions"]
    assert "johnny_ecc_rules.py" in tdd["developer_instructions"]
    assert sdd["sandbox_mode"] == "workspace-write"
    assert tdd["sandbox_mode"] == "workspace-write"
    assert "SDD_DQA/tool/" in sdd["developer_instructions"]
    assert "TDD_DQA/tool/" in tdd["developer_instructions"]
    assert "絕不修改 `src/`" in sdd["developer_instructions"]
    assert "絕不修改 `src/`" in tdd["developer_instructions"]
    assert security["sandbox_mode"] == "read-only"
    assert "explicitly requests" in security["developer_instructions"]
    assert "Do not\njoin the default TDD-to-SDD gate" in security["developer_instructions"]
    assert log_agent["sandbox_mode"] == "workspace-write"
    assert "Never modify application code" in log_agent["developer_instructions"]
    assert "`Logs/`" in log_agent["developer_instructions"]
    assert "Process/Documentation Defects" in architect["developer_instructions"]
    assert "In Phase 1" in architect["developer_instructions"]
    assert architect["sandbox_mode"] == "read-only"
    assert te["sandbox_mode"] == "read-only"
    assert "只能執行 parent DQA" in te["developer_instructions"]
    assert "TE 不得建立" in dqa["developer_instructions"]

    matrix = (
        SCRIPTS.parent / "references" / "templates" / "Model_Recommendation_Matrix.md"
    ).read_text(encoding="utf-8")
    assert "assets/agents/johnny-security-dqa.toml" in matrix
    assert "assets/agents/johnny-log-agent.toml" in matrix
    assert "agents/security_dqa.json" not in matrix
    assert "agents/log_agent.json" not in matrix


def test_model_recommendation_matrix_has_requested_defaults() -> None:
    matrix = (
        SCRIPTS.parent / "references" / "templates" / "Model_Recommendation_Matrix.md"
    ).read_text(encoding="utf-8")

    expected = {
        "PM": ("sol", "Medium"),
        "Architect": ("sol", "Medium"),
        "Engineer": ("terra", "Medium"),
        "TDD DQA": ("terra", "High"),
        "SDD DQA": ("terra", "High"),
        "DQA coordinator": ("terra", "High"),
        "TE": ("Luna", "High"),
    }
    rows = {
        parts[1].strip(): (parts[4].strip(), parts[5].strip())
        for line in matrix.splitlines()
        if line.startswith("|") and len(parts := line.split("|")) >= 9
    }
    for role, recommendation in expected.items():
        assert rows[role] == recommendation
    assert (
        "| Security DQA | `assets/agents/johnny-security-dqa.toml` "
        "| Optional manual security and trust-boundary review | sol | Medium |"
    ) in matrix


def test_phase3_is_single_ticket_policy_review_loop() -> None:
    phase3 = (
        SCRIPTS.parent / "references" / "phases" / "phase3.md"
    ).read_text(encoding="utf-8")
    ticket_template = (
        SCRIPTS.parent / "assets" / "templates" / "tracer-ticket.md"
    ).read_text(encoding="utf-8")
    pm = tomllib.loads(
        (SCRIPTS.parent / "assets" / "agents" / "johnny-pm.toml").read_text(
            encoding="utf-8"
        )
    )
    engineer = tomllib.loads(
        (SCRIPTS.parent / "assets" / "agents" / "johnny-engineer.toml").read_text(
            encoding="utf-8"
        )
    )

    assert "do not start multiple tickets in parallel" in phase3
    assert "`SUPERVISED`: PM presents that single result to the CEO" in phase3
    assert "`AUTONOMOUS`: after committing the approved tree" in phase3
    assert "attempt 5 by the same role" in phase3
    assert "**Blocked by:**" in ticket_template
    assert "**Milestone:**" in ticket_template
    assert "exactly one ticket maps to this milestone" in ticket_template
    assert "SDD DQA: PENDING / PASS / FAIL" in ticket_template
    assert "TDD DQA: PENDING / PASS / FAIL" in ticket_template
    assert "Claude DQA (manual only)" in ticket_template
    assert "keep exactly one\ndependency-ready pair active" in pm["developer_instructions"]
    assert "do not pre-build later pairs" in engineer["developer_instructions"]


def test_phase4_requires_tdd_then_sdd_in_fresh_scope(monkeypatch) -> None:
    phase4 = (
        SCRIPTS.parent / "references" / "phases" / "phase4.md"
    ).read_text(encoding="utf-8")
    assert "Phase 3 ticket DQA evidence cannot satisfy this gate" in phase4
    assert phase4.index("TDD DQA runs integrated") < phase4.index(
        "Only after TDD PASS"
    )
    assert "--scope phase4 --ticket PHASE4-FINAL --role tdd" in phase4
    assert "using `--role sdd`" in phase4

    monkeypatch.setattr(johnny_guard, "staged_tree", lambda project: "tree-1")
    monkeypatch.setattr(johnny_guard, "subject_tree", lambda project, paths: "subject-1")
    monkeypatch.setattr(
        johnny_guard,
        "read_json",
        lambda path, default: {
            "schema_version": 2,
            "scope": "ticket",
            "subject_tree": "subject-1",
            "commit_tree": "tree-1",
            "results": {"tdd": "PASS", "sdd": "PASS"},
        },
    )
    with pytest.raises(SystemExit):
        johnny_guard.validate_dqa(
            Path("."),
            ["src/feature.py"],
            {"dqa_required_phases": [3, 4], "product_paths": ["src/"]},
            {"phase": 4},
        )

    # Phase 5 documentation is verified by Architect and must not be deadlocked
    # by stale Phase 4 DQA evidence.
    johnny_guard.validate_dqa(
        Path("."),
        ["PM/As-Built.md"],
        {"dqa_required_phases": [3, 4], "product_paths": ["src/"]},
        {"phase": 5},
    )


def test_phase3_dqa_is_ordered_and_tree_bound(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    git(repo, "switch", "-c", "codex/milestone-M01")
    state_path = repo / ".johnny/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = 3
    state_path.write_text(json.dumps(state), encoding="utf-8")
    (repo / "src").mkdir()
    product = repo / "src/feature.py"
    product.write_text("VALUE = 1\n", encoding="utf-8")
    git(repo, "add", "src/feature.py")

    early_sdd = run_script(
        "johnny_dqa_record.py",
        "--project", str(repo),
        "--ticket", "M01",
        "--role", "sdd",
        "--result", "PASS",
        "--evidence", "contract checked",
        "--reviewer-id", "sdd-1",
        check=False,
    )
    assert early_sdd.returncode != 0
    assert "requires TDD DQA PASS" in early_sdd.stderr

    run_script(
        "johnny_dqa_record.py",
        "--project", str(repo),
        "--ticket", "M01",
        "--role", "tdd",
        "--result", "PASS",
        "--evidence", "tests passed",
        "--reviewer-id", "tdd-1",
    )
    blocked = git(repo, "commit", "-m", "still needs sdd", check=False)
    assert blocked.returncode != 0
    assert "required DQA did not pass: sdd" in (blocked.stdout + blocked.stderr)

    run_script(
        "johnny_dqa_record.py",
        "--project", str(repo),
        "--ticket", "M01",
        "--role", "sdd",
        "--result", "PASS",
        "--evidence", "contract checked",
        "--reviewer-id", "sdd-1",
    )
    selection_path = repo / ".johnny/ecc-selection.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selection["selection_sha256"] = "stale-selection"
    selection_path.write_text(json.dumps(selection), encoding="utf-8")
    stale_rules = git(repo, "commit", "-m", "wrong ECC selection", check=False)
    assert stale_rules.returncode != 0
    assert "stale for the active ECC selection" in (
        stale_rules.stdout + stale_rules.stderr
    )
    selection["selection_sha256"] = json.loads(
        (repo / ".johnny/dqa-status.json").read_text(encoding="utf-8")
    )["ecc_selection_sha256"]
    selection_path.write_text(json.dumps(selection), encoding="utf-8")
    git(repo, "commit", "-m", "ticket M01")

    product.write_text("VALUE = 2\n", encoding="utf-8")
    git(repo, "add", "src/feature.py")
    stale = git(repo, "commit", "-m", "tree changed", check=False)
    assert stale.returncode != 0
    assert "DQA evidence is missing or stale" in (stale.stdout + stale.stderr)


def test_phase3_commit_rejects_everything_outside_src(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    git(repo, "switch", "-c", "codex/milestone-M09")
    state_path = repo / ".johnny/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = 3
    state_path.write_text(json.dumps(state), encoding="utf-8")
    tool = repo / "TDD_DQA/tool/probe.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("print('probe')\n", encoding="utf-8")
    git(repo, "add", "-f", "TDD_DQA/tool/probe.py")

    blocked = git(repo, "commit", "-m", "must not commit DQA tool", check=False)

    assert blocked.returncode != 0
    assert "Phase 3 commit 只能包含 src/" in (
        blocked.stdout + blocked.stderr
    )


def test_sdd_fail_opens_new_cycle_and_requires_tdd_again(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    git(repo, "switch", "-c", "codex/milestone-M02")
    (repo / "src").mkdir()
    (repo / "src/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(repo, "add", "src/feature.py")
    run_script(
        "johnny_dqa_record.py", "verdict",
        "--project", str(repo), "--ticket", "M02", "--role", "tdd",
        "--result", "PASS", "--evidence", "tests", "--reviewer-id", "tdd-1",
    )
    run_script(
        "johnny_dqa_record.py", "verdict",
        "--project", str(repo), "--ticket", "M02", "--role", "sdd",
        "--result", "FAIL", "--evidence", "contract mismatch",
        "--reviewer-id", "sdd-1",
    )
    status = json.loads((repo / ".johnny/dqa-status.json").read_text(encoding="utf-8"))
    assert status["review_cycle"] == 2
    assert status["required_roles"] == ["tdd", "sdd"]
    assert status["completed_roles"] == []
    assert status["results"] == {}
    history = (repo / ".johnny/dqa-history.jsonl").read_text(encoding="utf-8")
    assert '"event":"cycle-reopened"' in history


def test_fifth_same_role_rejection_freezes_until_ceo_resolution(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    git(repo, "switch", "-c", "codex/milestone-M03")
    state_path = repo / ".johnny/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = 3
    state["execution_policy"] = {
        "mode": "AUTONOMOUS",
        "delegated_by": "CEO",
        "delegated_at": "test",
        "approval": "test delegation",
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")
    config_path = repo / ".johnny/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["dqa_escalation"]["max_rejections_per_role_per_milestone"] = 2
    config_path.write_text(json.dumps(config), encoding="utf-8")
    (repo / "src").mkdir()
    product = repo / "src/feature.py"

    for attempt in range(1, 6):
        product.write_text(f"VALUE = {attempt}\n", encoding="utf-8")
        git(repo, "add", "src/feature.py")
        run_script(
            "johnny_dqa_record.py", "verdict",
            "--project", str(repo), "--ticket", "M03", "--role", "tdd",
            "--result", "FAIL", "--evidence", f"failure {attempt}",
            "--reviewer-id", "tdd-1",
        )
        status = json.loads(
            (repo / ".johnny/dqa-status.json").read_text(encoding="utf-8")
        )
        assert status["rejection_counts"]["tdd"] == attempt
        assert bool((status.get("escalation") or {}).get("active")) == (attempt == 5)

    blocked = run_script(
        "johnny_dqa_record.py", "verdict",
        "--project", str(repo), "--ticket", "M03", "--role", "tdd",
        "--result", "PASS", "--evidence", "fixed", "--reviewer-id", "tdd-1",
        check=False,
    )
    assert blocked.returncode != 0
    assert "CEO resolution is required" in blocked.stderr
    blocked_commit = git(repo, "commit", "-m", "must await CEO", check=False)
    assert blocked_commit.returncode != 0
    assert "frozen pending CEO resolution" in (
        blocked_commit.stdout + blocked_commit.stderr
    )

    run_script(
        "johnny_dqa_record.py", "resolve-escalation",
        "--project", str(repo), "--ticket", "M03", "--role", "tdd",
        "--approval", "CEO approved the conflict resolution",
        "--resolution", "Use the documented tolerance and retry",
    )
    status = json.loads(
        (repo / ".johnny/dqa-status.json").read_text(encoding="utf-8")
    )
    assert status["escalation"] is None
    assert status["rejection_counts"]["tdd"] == 0
    assert status["required_roles"] == ["tdd", "sdd"]
    history = (repo / ".johnny/dqa-history.jsonl").read_text(encoding="utf-8")
    assert '"event":"ceo-escalation-opened"' in history
    assert '"event":"ceo-escalation-resolved"' in history


def test_autonomous_milestone_uses_phase2_delegation(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    for phase in (1, 2):
        arguments = [
            "--project", str(repo),
            "--to-phase", str(phase),
            "--approval", f"CEO approved phase {phase}",
        ]
        if phase == 1:
            arguments.extend(["--evidence", str(phase_evidence(repo, 1))])
        run_script(
            "johnny_phase_gate.py",
            *arguments,
        )
    run_script(
        "johnny_phase_gate.py",
        "--project", str(repo),
        "--to-phase", "3",
        "--execution-policy", "AUTONOMOUS",
        "--approval", "CEO delegated autonomous Milestone approval",
        "--evidence", str(phase_evidence(repo, 3)),
    )
    git(repo, "switch", "-c", "codex/milestone-M04")
    (repo / "src").mkdir()
    (repo / "src/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(repo, "add", "src/feature.py")
    for role in ("tdd", "sdd"):
        run_script(
            "johnny_dqa_record.py", "verdict",
            "--project", str(repo), "--ticket", "M04", "--role", role,
            "--result", "PASS", "--evidence", f"{role} passed",
            "--reviewer-id", f"{role}-1",
        )
    git(repo, "commit", "-m", "ticket M04")
    run_script(
        "johnny_milestone_gate.py",
        "--project", str(repo),
        "--ticket", "M04",
    )
    milestone = json.loads(
        (repo / ".johnny/milestone-status.json").read_text(encoding="utf-8")
    )
    assert milestone["status"] == "APPROVED"
    assert milestone["execution_policy"] == "AUTONOMOUS"
    assert milestone["approval_source"] == "phase2-ceo-delegation"
    assert milestone["approval"] == "CEO delegated autonomous Milestone approval"
    run_script(
        "johnny_pm_merge.py",
        "--project", str(repo),
        "--ticket", "M04",
        "--target", "main",
    )
    assert git(repo, "branch", "--show-current").stdout.strip() == "main"
    merge = json.loads((repo / ".johnny/merge-status.json").read_text(encoding="utf-8"))
    assert merge["status"] == "MERGED"
    assert merge["source_branch"] == "codex/milestone-M04"
    assert merge["target_branch"] == "main"
    assert merge["push_status"] == "NOT_REQUESTED"


def test_migrate_upgrades_managed_contracts_and_preserves_custom_config(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    config_path = repo / ".johnny/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["schema_version"] = 1
    config["custom_project_choice"] = {"keep": True}
    config["dqa_escalation"]["max_rejections_per_role_per_milestone"] = 9
    config_path.write_text(json.dumps(config), encoding="utf-8")
    manifest_path = repo / ".agents/context-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["ecc_rules"]["supported_rule_sets"] = ["common"]
    manifest["custom_route"] = "keep"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    custom_agent = repo / ".codex/agents/johnny-pm.toml"
    custom_profile = (
        'name = "johnny_pm"\n'
        'developer_instructions = "project-owned customization"\n'
    )
    custom_agent.write_text(custom_profile, encoding="utf-8")
    managed_agent = repo / ".codex/agents/johnny-engineer.toml"
    old_managed = 'name = "johnny_engineer"\ndeveloper_instructions = "old contract"\n'
    managed_agent.write_text(old_managed, encoding="utf-8")
    managed_path = repo / ".codex/agents/.johnny-managed.json"
    managed = json.loads(managed_path.read_text(encoding="utf-8"))
    managed["johnny-engineer.toml"] = hashlib.sha256(
        managed_agent.read_bytes()
    ).hexdigest()
    managed_path.write_text(json.dumps(managed), encoding="utf-8")
    stale_hook = repo / ".johnny/git-hooks/pre-commit"
    stale_hook.write_text("#!/bin/sh\nexec /removed/cache/johnny_guard.py\n", encoding="utf-8")

    run_script("johnny_project_hooks.py", "migrate", "--project", str(repo))

    migrated = json.loads(config_path.read_text(encoding="utf-8"))
    assert migrated["schema_version"] == 3
    assert migrated["custom_project_choice"] == {"keep": True}
    assert migrated["dqa_escalation"]["max_rejections_per_role_per_milestone"] == 5
    assert migrated["allowed_code_roots"] == ["src/"]
    assert migrated["product_paths"] == ["src/"]
    assert migrated["phase3_commit_roots"] == ["src/"]
    refreshed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert refreshed_manifest["custom_route"] == "keep"
    assert "react-native" in refreshed_manifest["ecc_rules"]["supported_rule_sets"]
    assert custom_agent.read_text(encoding="utf-8") == custom_profile
    assert "只 stage 與 commit `src/**`" in managed_agent.read_text(encoding="utf-8")
    expected_guard = str((SCRIPTS / "johnny_guard.py").resolve()).replace("\\", "/")
    assert expected_guard in stale_hook.read_text(encoding="utf-8")
    assert (repo / ".johnny/migration-history.jsonl").is_file()


def test_migrate_refuses_tracked_product_files_outside_src(repo: Path) -> None:
    misplaced = {
        "app/legacy.py": "VALUE = 1\n",
        "config/prod.yaml": "mode: production\n",
        "migrations/001.sql": "CREATE TABLE example(id INT);\n",
        "scripts/build.ps1": "Write-Output build\n",
        "include/example.hpp": "#pragma once\n",
        "Makefile": "all:\n\t@echo build\n",
    }
    for relative, content in misplaced.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", *misplaced)
    git(repo, "commit", "-m", "legacy layout")
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    config_path = repo / ".johnny/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["schema_version"] = 2
    config_path.write_text(json.dumps(config), encoding="utf-8")
    agent = repo / ".codex/agents/johnny-engineer.toml"
    before_agent = agent.read_bytes()

    result = run_script(
        "johnny_project_hooks.py", "migrate", "--project", str(repo), check=False
    )

    assert result.returncode != 0
    assert "tracked 產品交付檔案移入 src/" in result.stderr
    for relative in misplaced:
        assert relative in result.stderr
    assert json.loads(config_path.read_text(encoding="utf-8"))["schema_version"] == 2
    assert agent.read_bytes() == before_agent
