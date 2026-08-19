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
import johnny_pm_merge
from johnny_project_hooks import install_project_rules
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
    elif to_phase == 4:
        for relative in (
            "Architect/Phase4_Architecture_Review.md",
            "PM/Phase4_PRD.md",
            "PM/Phase_Contract_Matrix.md",
            "TDD_DQA/phase3-baseline.md",
        ):
            artifact = repo / relative
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(f"Evidence for {relative}\n", encoding="utf-8")
        common.update(
            {
                "architecture_review": ["Architect/Phase4_Architecture_Review.md"],
                "phase4_prd": ["PM/Phase4_PRD.md"],
                "scope_contract_matrix": ["PM/Phase_Contract_Matrix.md"],
                "milestones": ["P4-M01"],
                "regression_baseline": ["TDD_DQA/phase3-baseline.md"],
            }
        )
    else:
        regression = repo / "TDD_DQA/phase4-regression.md"
        regression.parent.mkdir(parents=True, exist_ok=True)
        regression.write_text("Phase 4 regression PASS\n", encoding="utf-8")
        report = repo / "Architect/As_Built_Architecture.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "# As-Built Report\n\n"
            "## 1. Final architecture\n\n"
            "## 2. Final data flow\n\n"
            "## 3. APIs, schemas, configuration, and dependencies\n\n"
            "## 4. Baseline-to-As-Built comparison\n\n"
            "## 5. Critical routes and maintenance entry points\n\n"
            "## 6. Known limitations and technical debt\n\n"
            "## 7. Reproducible commands\n\n"
            "## 8. Architect verification\n\n"
            "- Verdict: VERIFIED\n",
            encoding="utf-8",
        )
        common.update(
            {
                "completed_milestones": ["P4-M01"],
                "regression_evidence": ["TDD_DQA/phase4-regression.md"],
                "detailed_architecture_report": ["Architect/As_Built_Architecture.md"],
                "known_limitations": ["None"],
                "commit_tree": git(repo, "rev-parse", "HEAD^{tree}").stdout.strip(),
            }
        )
    path = repo / f"phase-{to_phase}-evidence.json"
    path.write_text(json.dumps(common), encoding="utf-8")
    return path


def append_merge_record(repo: Path, ticket: str) -> None:
    path = repo / ".johnny/merge-history.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ticket": ticket, "status": "MERGED"}) + "\n")


def phase3_completion_evidence(repo: Path) -> Path:
    regression = repo / "TDD_DQA/phase3-regression.md"
    regression.parent.mkdir(parents=True, exist_ok=True)
    regression.write_text("Phase 3 regression PASS\n", encoding="utf-8")
    evidence = {
        "schema_version": 1,
        "from_phase": 3,
        "to_phase": 4,
        "completed_milestones": ["M01"],
        "regression_evidence": ["TDD_DQA/phase3-regression.md"],
        "commit_tree": git(repo, "rev-parse", "HEAD^{tree}").stdout.strip(),
    }
    path = repo / "phase-3-completion-evidence.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")
    return path


def test_enable_is_repo_local_and_disable_restores(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    assert git(repo, "config", "--local", "--get", "core.hooksPath").stdout.strip() == ".johnny/git-hooks"
    marker = json.loads((repo / ".johnny/enabled.json").read_text(encoding="utf-8"))
    assert marker["scope"] == str(repo.resolve())
    assert (repo / ".johnny/git-hooks/pre-commit").is_file()
    assert not (repo / ".codex/agents/johnny-dqa.toml").exists()
    assert (repo / ".codex/agents/johnny-sdd-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-tdd-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-security-dqa.toml").is_file()
    assert (repo / ".codex/agents/johnny-log-agent.toml").is_file()
    assert (repo / ".codex/agents/johnny-te.toml").is_file()
    assert not (repo / ".codex/agents/johnny-pm.toml").exists()
    assert (repo / ".codex/agents/johnny-engineer.toml").is_file()
    assert (repo / ".codex/agents/johnny-architect.toml").is_file()
    assert (repo / "JOHNNY_PROJECT_RULES.md").is_file()
    rules = (repo / "JOHNNY_PROJECT_RULES.md").read_text(encoding="utf-8")
    assert "johnny-project-contract-v4:start" in rules
    assert "PM/tests/" in rules
    assert "繁體中文（台灣用語）" in rules
    assert "PM/" in rules
    assert (repo / ".agents/context-manifest.json").is_file()
    manifest = json.loads(
        (repo / ".agents/context-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["routes"]["tdd_method"].startswith("references/tdd-integration.md")
    assert manifest["routes"]["engineer_handoff"].startswith(
        "assets/templates/engineer-handoff.md"
    )
    assert manifest["model_matrix"] == "PM/Planning/Model_Recommendation_Matrix.md"
    assert manifest["pm_document_root"] == "PM/"
    config = json.loads((repo / ".johnny/config.json").read_text(encoding="utf-8"))
    assert config["claude_dqa"] == {
        "enabled": False,
        "required": False,
        "manual_allowed": True,
    }
    assert config["dqa_required_from_phase"] == 3
    assert config["dqa_required_phases"] == [3, 4]
    assert config["schema_version"] == 5
    assert config["product_root"] == "src/"
    assert config["allowed_code_roots"] == ["src/"]
    assert config["product_paths"] == ["src/"]
    assert config["phase3_commit_roots"] == ["src/"]
    assert config["phase4_commit_roots"] == ["src/"]
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
        "max_active_phase4_tickets": 1,
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
        "phase4_commit_roots": ["src/"],
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


def test_project_rules_upgrade_v3_and_refresh_v4(tmp_path: Path) -> None:
    rules = tmp_path / "JOHNNY_PROJECT_RULES.md"
    rules.write_text(
        "# Johnny Project Rules\n\n<!-- johnny-project-contract-v3 -->\nold rules\n",
        encoding="utf-8",
    )

    install_project_rules(tmp_path)

    upgraded = rules.read_text(encoding="utf-8")
    assert "johnny-project-contract-v3" not in upgraded
    assert "johnny-project-contract-v4:start" in upgraded
    assert "PM/tests/" in upgraded

    customized = "# Custom preface\n\n" + upgraded
    rules.write_text(customized, encoding="utf-8")
    install_project_rules(tmp_path)
    refreshed = rules.read_text(encoding="utf-8")
    assert refreshed.startswith("# Custom preface")
    assert refreshed.count("johnny-project-contract-v4:start") == 1


def test_log_pipeline_requires_real_artifact(tmp_path: Path) -> None:
    missing = run_script(
        "run_log_agent.py",
        "--project_dir",
        str(tmp_path),
        check=False,
    )
    assert missing.returncode != 0

    artifact = tmp_path / "reviewed-log.md"
    artifact.write_text(
        "### 實際觀測\n- Evidence: TDD_DQA/report.md\n- 狀態：需要人工判讀\n",
        encoding="utf-8",
    )
    completed = run_script(
        "run_log_agent.py",
        "--project_dir",
        str(tmp_path),
        "--input",
        str(artifact),
    )

    master_log = (tmp_path / "Logs/Master_Log.md").read_text(encoding="utf-8")
    assert completed.returncode == 0
    assert "Evidence: TDD_DQA/report.md" in master_log
    assert "資訊完整" not in master_log
    assert "效能成本" not in master_log


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


def test_dispatch_gate_requires_documents_and_only_skips_approval_in_autonomous(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    state_path = repo / ".johnny" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["execution_policy"] = {"mode": "SUPERVISED"}
    state_path.write_text(json.dumps(state), encoding="utf-8")

    missing = run_script(
        "johnny_dispatch_gate.py",
        "--project", str(repo), "--ticket", "M01", "--role", "engineer",
        "--approval", "/approve", check=False,
    )
    assert missing.returncode != 0
    assert "milestone_prd is missing or unreadable" in missing.stderr

    documents = {
        "PM/Milestones/M01_PRD.md": (
            "# M01\n\n## Acceptance Criteria\n\n"
            "| ID | 驗收對象 | 操作步驟 | 預期結果 | 容忍值 | 證據／測試命令 | 負責 DQA |\n"
            "|---|---|---|---|---|---|---|\n"
            "| AC-01 | API | 呼叫建立端點 | 回傳 201 | 0 errors | pytest src/tests -q | TDD DQA |\n"
        ),
        "PM/Flows/M01_Flow.md": "# Flow\n\n```mermaid\nflowchart TD\nA-->B\n```\n",
        "PM/DataFlows/M01_Data_Flow.md": "# Data Flow\n\n```mermaid\nflowchart TD\nA-->B\n```\n",
        "PM/Context/M01.md": "# Context\n\nReady\n",
    }
    for relative, content in documents.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    no_approval = run_script(
        "johnny_dispatch_gate.py",
        "--project", str(repo), "--ticket", "M01", "--role", "engineer",
        check=False,
    )
    assert no_approval.returncode != 0
    assert "requires explicit --approval /approve" in no_approval.stderr

    state["execution_policy"] = {"mode": "AUTONOMOUS"}
    state_path.write_text(json.dumps(state), encoding="utf-8")
    passed = run_script(
        "johnny_dispatch_gate.py",
        "--project", str(repo), "--ticket", "M01", "--role", "engineer",
    )
    authorization = json.loads(passed.stdout)
    assert authorization["execution_policy"] == "AUTONOMOUS"
    assert authorization["approval"] == "phase2-delegation"
    assert (repo / ".johnny/dispatch-authorizations/M01-engineer.json").is_file()


def test_phase5_can_restart_to_phase0_as_a_new_round(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    state_path = repo / ".johnny" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update(
        {
            "phase": 5,
            "revision": 11,
            "execution_policy": {"mode": "AUTONOMOUS"},
            "phase4_execution": {"status": "APPROVED"},
            "prerequisite_evidence": {
                "path": "PM/old-evidence.md",
                "sha256": "old",
                "to_phase": 5,
            },
        }
    )
    state_path.write_text(json.dumps(state), encoding="utf-8")

    run_script(
        "johnny_phase_gate.py",
        "--project",
        str(repo),
        "--to-phase",
        "0",
        "--approval",
        "CEO approved the next implementation round",
    )

    restarted = json.loads(state_path.read_text(encoding="utf-8"))
    assert restarted["phase"] == 0
    assert restarted["revision"] == 12
    assert restarted["round"] == 2
    assert "execution_policy" not in restarted
    assert "phase4_execution" not in restarted
    assert "prerequisite_evidence" not in restarted

    history = [
        json.loads(line)
        for line in (repo / ".johnny" / "approval-history.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert history[-1]["from_phase"] == 5
    assert history[-1]["to_phase"] == 0
    assert history[-1]["round"] == 2
    assert history[-1]["reentry_from_phase5"] is True


def test_only_phase5_can_restart_to_phase0(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    state_path = repo / ".johnny" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = 4
    state_path.write_text(json.dumps(state), encoding="utf-8")

    rejected = run_script(
        "johnny_phase_gate.py",
        "--project",
        str(repo),
        "--to-phase",
        "0",
        "--approval",
        "CEO approval",
        check=False,
    )

    assert rejected.returncode != 0
    assert "only restart transition is 5 -> 0" in rejected.stderr


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


def test_phase4_plan_and_completion_require_structured_evidence(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    for phase in (1, 2, 3):
        arguments = [
            "--project", str(repo), "--to-phase", str(phase),
            "--approval", f"CEO approved phase {phase}",
        ]
        if phase in {1, 3}:
            arguments.extend(["--evidence", str(phase_evidence(repo, phase))])
        if phase == 3:
            arguments.extend(["--execution-policy", "AUTONOMOUS"])
        run_script("johnny_phase_gate.py", *arguments)

    missing_phase3_completion = run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "4",
        "--approval", "CEO approved entering Phase 4 planning", check=False,
    )
    assert missing_phase3_completion.returncode != 0
    append_merge_record(repo, "M01")
    run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "4",
        "--approval", "CEO approved entering Phase 4 planning",
        "--evidence", str(phase3_completion_evidence(repo)),
    )
    missing_plan = run_script(
        "johnny_phase4_start.py", "--project", str(repo),
        "--approval", "CEO approved Phase 4 construction",
        "--evidence", str(repo / "missing-plan.json"), check=False,
    )
    assert missing_plan.returncode != 0
    run_script(
        "johnny_phase4_start.py", "--project", str(repo),
        "--approval", "CEO approved Phase 4 architecture plan",
        "--evidence", str(phase_evidence(repo, 4)),
    )
    append_merge_record(repo, "P4-M01")
    run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "5",
        "--approval", "CEO approved Phase 4 completion",
        "--evidence", str(phase_evidence(repo, 5)),
    )
    state = json.loads((repo / ".johnny/state.json").read_text(encoding="utf-8"))
    assert state["phase"] == 5
    assert state["phase4_execution"]["status"] == "APPROVED"


def test_phase3_completion_rejects_unmerged_or_escalated_work(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    for phase in (1, 2, 3):
        arguments = [
            "--project", str(repo), "--to-phase", str(phase),
            "--approval", f"CEO approved phase {phase}",
        ]
        if phase in {1, 3}:
            arguments.extend(["--evidence", str(phase_evidence(repo, phase))])
        if phase == 3:
            arguments.extend(["--execution-policy", "AUTONOMOUS"])
        run_script("johnny_phase_gate.py", *arguments)

    evidence = phase3_completion_evidence(repo)
    unmerged = run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "4",
        "--approval", "approved", "--evidence", str(evidence), check=False,
    )
    assert unmerged.returncode != 0
    assert "not recorded as merged" in unmerged.stderr

    append_merge_record(repo, "M01")
    (repo / ".johnny/dqa-status.json").write_text(
        json.dumps({"schema_version": 2, "escalation": {"active": True}}),
        encoding="utf-8",
    )
    escalated = run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "4",
        "--approval", "approved", "--evidence", str(evidence), check=False,
    )
    assert escalated.returncode != 0
    assert "active DQA escalation" in escalated.stderr


def test_phase4_completion_rejects_incomplete_as_built_report(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    state_path = repo / ".johnny/state.json"
    plan = phase_evidence(repo, 4)
    plan_payload = plan.read_bytes()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update(
        {
            "phase": 4,
            "phase4_execution": {
                "status": "APPROVED",
                "plan_evidence": {
                    "path": str(plan.resolve()),
                    "sha256": hashlib.sha256(plan_payload).hexdigest(),
                    "to_phase": 4,
                },
            },
        }
    )
    state_path.write_text(json.dumps(state), encoding="utf-8")
    append_merge_record(repo, "P4-M01")
    evidence = phase_evidence(repo, 5)
    (repo / "Architect/As_Built_Architecture.md").write_text(
        "# Incomplete report\n", encoding="utf-8"
    )

    rejected = run_script(
        "johnny_phase_gate.py", "--project", str(repo), "--to-phase", "5",
        "--approval", "approved", "--evidence", str(evidence), check=False,
    )

    assert rejected.returncode != 0
    assert "architecture report is incomplete" in rejected.stderr


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
    skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
    engineer = tomllib.loads(
        (agents / "johnny-engineer.toml").read_text(encoding="utf-8")
    )
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

    assert "擔任 PM／主 agent" in skill
    assert "2–3 個明確方案" in skill
    assert "不得替 CEO approve" in skill
    assert "預設 CEO 沒有技術背景" in skill
    assert "不得直接傾倒 code、stack trace 或原始 log" in skill
    assert "立即通知 PM" in engineer["developer_instructions"]
    assert "不得直接派工或交付 TDD／SDD DQA" in engineer["developer_instructions"]
    assert "Engineer/<Wave>_<Milestone>_R<review-cycle>_Engineer_Hand_off.md" in engineer[
        "developer_instructions"
    ]
    assert "角色派工由 PM／主 agent" in skill
    assert "johnny_ecc_rules.py" in engineer["developer_instructions"]
    assert "TDD DQA PASS 後" in sdd["developer_instructions"]
    assert "johnny_ecc_rules.py" in sdd["developer_instructions"]
    assert "不得解鎖 SDD" in tdd["developer_instructions"]
    assert "johnny_ecc_rules.py" in tdd["developer_instructions"]
    assert "references/tdd-dqa-review.md" in tdd["developer_instructions"]
    assert "stress／load／soak" in tdd["developer_instructions"]
    assert "monkey／fuzz" in tdd["developer_instructions"]
    assert "受控\n實際硬體測試" in tdd["developer_instructions"]
    assert "references/sdd-review.md" in sdd["developer_instructions"]
    assert "assets/templates/sdd-dqa-review-report.md" in sdd["developer_instructions"]
    assert sdd["sandbox_mode"] == "workspace-write"
    assert tdd["sandbox_mode"] == "workspace-write"
    assert "SDD_DQA/tool/" in sdd["developer_instructions"]
    assert "TDD_DQA/tool/" in tdd["developer_instructions"]
    assert "絕不修改 `src/`" in sdd["developer_instructions"]
    assert "絕不修改 `src/`" in tdd["developer_instructions"]
    assert security["sandbox_mode"] == "read-only"
    assert "明確要求 Security DQA" in security["developer_instructions"]
    assert "不得加入預設 TDD → SDD gate" in security["developer_instructions"]
    assert log_agent["sandbox_mode"] == "workspace-write"
    assert "預設啟用的非 gate" in log_agent["description"]
    assert "不得由 SessionStart" in log_agent["developer_instructions"]
    assert "不得修改產品程式" in log_agent["developer_instructions"]
    assert "`Logs/`" in log_agent["developer_instructions"]
    assert "視為流程／文件缺陷" in architect["developer_instructions"]
    assert "Phase 1 必須建立" in architect["developer_instructions"]
    assert architect["sandbox_mode"] == "workspace-write"
    assert te["sandbox_mode"] == "read-only"
    assert "只能執行上層 DQA" in te["developer_instructions"]
    assert "assets/schemas/te-result.schema.json" in te["developer_instructions"]
    assert "johnny_tdd_dqa" in skill
    assert "johnny_sdd_dqa" in skill

    matrix = (
        SCRIPTS.parent / "references" / "templates" / "Model_Recommendation_Matrix.md"
    ).read_text(encoding="utf-8")
    assert "assets/agents/johnny-security-dqa.toml" in matrix
    assert "assets/agents/johnny-log-agent.toml" in matrix
    assert "Default-enabled non-gate observability" in matrix
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
        "TE": ("terra", "Low"),
        "Log Agent": ("terra", "Low"),
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


def test_skill_routes_phase_details_without_repeating_them() -> None:
    skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")

    assert "## Phase 路由" in skill
    assert "### Phase" not in skill
    for phase in range(6):
        assert f"references/phases/phase{phase}.md" in skill


def test_phase3_is_single_ticket_policy_review_loop() -> None:
    phase3 = (
        SCRIPTS.parent / "references" / "phases" / "phase3.md"
    ).read_text(encoding="utf-8")
    ticket_template = (
        SCRIPTS.parent / "assets" / "templates" / "tracer-ticket.md"
    ).read_text(encoding="utf-8")
    engineer = tomllib.loads(
        (SCRIPTS.parent / "assets" / "agents" / "johnny-engineer.toml").read_text(
            encoding="utf-8"
        )
    )

    assert "一次只執行一個 dependency-ready `Mxx`" in phase3
    assert "`SUPERVISED`：CEO 明確核准" in phase3
    assert "`AUTONOMOUS`：引用 Phase 2 delegation" in phase3
    assert "第 5 次凍結該 Milestone" in phase3
    assert "**Blocked by:**" in ticket_template
    assert "**Milestone:**" in ticket_template
    assert "exactly one ticket maps to this milestone" in ticket_template
    assert "SDD DQA: PENDING / PASS / FAIL" in ticket_template
    assert "TDD DQA: PENDING / PASS / FAIL" in ticket_template
    assert "Claude DQA (manual only)" in ticket_template
    assert "不得預作後續工作" in engineer["developer_instructions"]
    handoff = (
        SCRIPTS.parent / "assets" / "templates" / "engineer-handoff.md"
    ).read_text(encoding="utf-8")
    assert handoff.startswith("# <Wave>_<Milestone>_Engineer Hand off")
    assert "Subject tree" in handoff
    assert "TDD cycle evidence 路徑" in handoff
    assert "READY_FOR_PM / BLOCKED" in handoff
    assert "修改明細" in handoff
    assert "非預期失敗紀錄" in handoff
    assert "Smoke test 閘門" in handoff
    assert "PASS / BLOCKED" in handoff
    assert (SCRIPTS.parent / "assets/examples/engineer-handoff-example.md").is_file()


def test_phase4_uses_architecture_plan_and_ticket_scoped_tdd_then_sdd(monkeypatch) -> None:
    phase4 = (
        SCRIPTS.parent / "references" / "phases" / "phase4.md"
    ).read_text(encoding="utf-8")
    assert "`improve-codebase-architecture` skill" in phase4
    assert "`PM/PRD/Phase4_PRD.md`" in phase4
    assert "`P4-Mxx` vertical-slice Milestones" in phase4
    assert "`codex/phase4-Mxx`" in phase4
    assert "PM validates the Engineer Handoff" in phase4
    assert "`references/tdd-integration.md`" in phase4
    assert "SDD DQA may run only after TDD PASS" in phase4
    assert "Architect writes `Architect/As_Built_Architecture.md`" in phase4
    assert "does not assume a `CONTEXT.md` exists" in phase4
    assert "`Architect/Phase4_Codebase_Context.md`" in phase4
    assert "A missing `CONTEXT.md` is not a blocker" in phase4

    with pytest.raises(SystemExit):
        johnny_guard.validate_paths(
            Path("."), ["src/feature.py"], {"phase4_commit_roots": ["src/"]}, {"phase": 4}
        )
    johnny_guard.validate_paths(
        Path("."),
        ["src/feature.py"],
        {"phase4_commit_roots": ["src/"]},
        {"phase": 4, "phase4_execution": {"status": "APPROVED"}},
    )

    monkeypatch.setattr(johnny_guard, "staged_tree", lambda project: "tree-1")
    monkeypatch.setattr(johnny_guard, "subject_tree", lambda project, paths: "subject-1")
    monkeypatch.setattr(
        johnny_guard,
        "read_json",
        lambda path, default: ({
            "schema_version": 2,
            "scope": "ticket",
            "subject_tree": "subject-1",
            "commit_tree": "tree-1",
            "ecc_selection_sha256": "rules-1",
            "results": {"tdd": "PASS", "sdd": "PASS"},
            "reviews": {
                "tdd": {"ecc_selection_sha256": "rules-1"},
                "sdd": {"ecc_selection_sha256": "rules-1"},
            },
        } if path.name == "dqa-status.json" else {"selection_sha256": "rules-1"}),
    )
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


def test_codex_lifecycle_allows_phase5_reentry_with_two_phase2_policies() -> None:
    phases = SCRIPTS.parent / "references" / "phases"
    assert sorted(path.name for path in phases.glob("phase*.md")) == [
        "phase0.md", "phase1.md", "phase2.md", "phase3.md", "phase4.md", "phase5.md"
    ]
    phase2 = (phases / "phase2.md").read_text(encoding="utf-8")
    assert "`SUPERVISED`" in phase2
    assert "`AUTONOMOUS`" in phase2
    assert "只提供兩種方案" in phase2
    phase0 = (phases / "phase0.md").read_text(encoding="utf-8")
    phase5 = (phases / "phase5.md").read_text(encoding="utf-8")
    assert "剛由 Phase 5 回到 Phase 0" in phase0
    assert "--to-phase 0" in phase5
    assert "唯一允許的 restart transition" in phase5
    skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "Phase 5 結束的是一輪實作" in skill
    readme = (SCRIPTS.parents[4] / "README.md").read_text(encoding="utf-8")
    assert "Phase 0～5" in readme
    assert "Antigravity" not in readme


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
    assert "Phase 3 construction commits may contain only src/" in (
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


def test_pm_merge_safety_allows_tracked_legacy_process_artifacts(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    for relative_path, content in (
        (".johnny/state.json", '{"phase": 0}\n'),
        (".johnny/dqa-status.json", '{"ticket": "M01"}\n'),
    ):
        path = repo / relative_path
        path.write_text(content, encoding="utf-8")
    git(repo, "add", ".johnny/state.json", ".johnny/dqa-status.json")
    git(repo, "commit", "-m", "track legacy process artifacts")

    (repo / ".johnny/state.json").write_text('{"phase": 4}\n', encoding="utf-8")
    (repo / ".johnny/dqa-status.json").write_text(
        '{"ticket": "M01", "status": "PASS"}\n', encoding="utf-8"
    )

    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == []


def test_pm_merge_safety_rejects_tracked_product_change(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    feature = repo / "src/feature.py"
    feature.parent.mkdir()
    feature.write_text("VALUE = 1\n", encoding="utf-8")
    git(repo, "add", "src/feature.py")
    git(repo, "commit", "-m", "track product file")
    feature.write_text("VALUE = 2\n", encoding="utf-8")

    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == ["src/feature.py"]


def test_pm_merge_safety_preserves_first_unstaged_porcelain_record(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    (repo / "README.md").write_text("unstaged change\n", encoding="utf-8")

    raw = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=no"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    assert raw.startswith(" M README.md\0")
    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == ["README.md"]


def test_pm_merge_safety_rejects_non_process_tracked_files(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    manifest = repo / "package.json"
    manifest.write_text('{"name":"before"}\n', encoding="utf-8")
    git(repo, "add", "package.json")
    git(repo, "commit", "-m", "track build manifest")
    (repo / "README.md").write_text("changed readme\n", encoding="utf-8")
    manifest.write_text('{"name":"after"}\n', encoding="utf-8")

    assert set(johnny_pm_merge._blocking_tracked_dirty_paths(repo)) == {
        "README.md",
        "package.json",
    }


def test_pm_merge_safety_uses_configured_process_artifact_roots(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    report = repo / "PM/report.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("before\n", encoding="utf-8")
    git(repo, "add", "PM/report.md")
    git(repo, "commit", "-m", "track PM report")
    report.write_text("after\n", encoding="utf-8")

    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == []
    config_path = repo / ".johnny/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["process_artifact_roots"] = [".johnny/"]
    config_path.write_text(json.dumps(config), encoding="utf-8")
    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == ["PM/report.md"]


def test_pm_merge_safety_keeps_untracked_files_out_of_existing_scope(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    untracked = repo / "src/untracked.py"
    untracked.parent.mkdir()
    untracked.write_text("VALUE = 1\n", encoding="utf-8")

    assert johnny_pm_merge._blocking_tracked_dirty_paths(repo) == []


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
    retired_agent = repo / ".codex/agents/johnny-dqa.toml"
    retired_agent.write_text(
        'name = "johnny_dqa"\ndeveloper_instructions = "managed retired role"\n',
        encoding="utf-8",
    )
    managed["johnny-dqa.toml"] = hashlib.sha256(retired_agent.read_bytes()).hexdigest()
    managed_path.write_text(json.dumps(managed), encoding="utf-8")
    stale_hook = repo / ".johnny/git-hooks/pre-commit"
    stale_hook.write_text("#!/bin/sh\nexec /removed/cache/johnny_guard.py\n", encoding="utf-8")

    run_script("johnny_project_hooks.py", "migrate", "--project", str(repo))

    migrated = json.loads(config_path.read_text(encoding="utf-8"))
    assert migrated["schema_version"] == 5
    assert migrated["custom_project_choice"] == {"keep": True}
    assert migrated["dqa_escalation"]["max_rejections_per_role_per_milestone"] == 5
    assert migrated["allowed_code_roots"] == ["src/"]
    assert migrated["product_paths"] == ["src/"]
    assert migrated["phase3_commit_roots"] == ["src/"]
    assert migrated["phase4_commit_roots"] == ["src/"]
    refreshed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert refreshed_manifest["custom_route"] == "keep"
    assert "react-native" in refreshed_manifest["ecc_rules"]["supported_rule_sets"]
    assert custom_agent.read_text(encoding="utf-8") == custom_profile
    assert "只 stage 與 commit `src/**`" in managed_agent.read_text(encoding="utf-8")
    assert not retired_agent.exists()
    assert "johnny-dqa.toml" not in json.loads(managed_path.read_text(encoding="utf-8"))
    expected_guard = str((SCRIPTS / "johnny_guard.py").resolve()).replace("\\", "/")
    assert expected_guard in stale_hook.read_text(encoding="utf-8")
    assert (repo / ".johnny/migration-history.jsonl").is_file()


def test_migrate_preserves_custom_retired_dqa_profile(repo: Path) -> None:
    run_script("johnny_project_hooks.py", "enable", "--project", str(repo))
    custom = repo / ".codex/agents/johnny-dqa.toml"
    content = 'name = "project_owned_dqa"\ndeveloper_instructions = "keep me"\n'
    custom.write_text(content, encoding="utf-8")

    run_script("johnny_project_hooks.py", "migrate", "--project", str(repo))

    assert custom.read_text(encoding="utf-8") == content


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
