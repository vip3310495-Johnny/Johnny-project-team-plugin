from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "Johnny-project-team" / "scripts" / "project_governance.py"
PHASE_HOOK = ROOT / "skills" / "Johnny-project-team" / "scripts" / "phase_gate_hook.py"


class GovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="治理 測試 😀 ")
        self.project = Path(self.temp.name)
        self.invoke("init")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([sys.executable, str(SCRIPT), *args, "--project-dir", str(self.project)] if args[0] not in {"detect-python"} else [sys.executable, str(SCRIPT), *args], text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def write(self, relative: str, text: str) -> Path:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def approve(self, scope: str, phase: str, artifacts: list[str], **kwargs: str) -> None:
        command = ["approve", "--scope", scope, "--phase", phase, "--approver", kwargs.get("approver", "CEO"), "--gate", kwargs.get("gate", "test"), "--signature", "/approve"]
        for artifact in artifacts:
            command += ["--artifact", artifact]
        if "reason" in kwargs: command += ["--reason", kwargs["reason"]]
        self.invoke(*command)

    def phase0_ready(self) -> None:
        self.write("PM/Phase0_5W_Alignment.md", "Why\n目標\nWho\n使用者\nWhat\n功能\nWhere\nWindows\nWhen-Action\n失敗安全\n")
        self.approve("phase0_5w_alignment", "0", ["PRD=PM/Phase0_5W_Alignment.md"])
        self.invoke("check-architect-dispatch")
        self.write("Architect/Phase0_How_Architecture_Draft.md", "5W-TRACE: D1 -> Why-1。")
        for role in ("SDD", "TDD"):
            report = self.write(f"{role}_DQA/phase0.json", json.dumps({"role": role, "phase": "0", "verdict": "PASS", "evidence_paths": []}))
            self.invoke("set-dqa", "--phase", "0", "--role", role, "--status", "PASS", "--report", report.relative_to(self.project).as_posix())
        self.approve("phase0_exit", "0", ["PRD=PM/Phase0_5W_Alignment.md", "SDD=Architect/Phase0_How_Architecture_Draft.md"])

    def test_01_phase0_forward_gate(self) -> None:
        self.phase0_ready()
        self.invoke("gate", "--from-phase", "0", "--to-phase", "1", "--signature", "/approve")
        self.assertEqual(json.loads((self.project / ".agents/project_state.json").read_text(encoding="utf-8"))["current_phase"], "1")

    def test_02_architect_is_blocked_before_5w(self) -> None:
        self.invoke("check-architect-dispatch", expected=1)

    def test_03_auto_and_ambiguous_approval_fail(self) -> None:
        self.invoke("approve", "--scope", "phase_exit", "--phase", "1", "--approver", "CEO", "--gate", "x", "--signature", "/approve", "--auto", expected=1)

    def test_04_semantic_change_stales_approval(self) -> None:
        self.write("PM/a.md", "需求 A")
        self.approve("phase_exit", "1", ["PRD=PM/a.md"])
        self.write("PM/a.md", "需求 B")
        self.invoke("refresh")
        data = json.loads((self.project / "PM/Approval_Ledger.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item.get("record_type") == "approval_invalidated" for item in data["entries"]))

    def test_05_layout_change_does_not_stale(self) -> None:
        self.write("PM/a.md", "需求 A\n")
        self.approve("phase_exit", "1", ["PRD=PM/a.md"])
        self.write("PM/a.md", "\n需求 A   \n<!-- 版面註解 -->\n")
        self.invoke("refresh")
        data = json.loads((self.project / "PM/Approval_Ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(data["entries"][0]["status"], "ACTIVE")

    def test_06_milestone_specs_are_isolated(self) -> None:
        self.invoke("init-milestone", "--milestone", "M1.1")
        self.invoke("init-milestone", "--milestone", "M1.2")
        self.assertNotEqual((self.project / "specs/M1.1/sdd_spec.md").resolve(), (self.project / "specs/M1.2/sdd_spec.md").resolve())

    def test_07_complex_milestone_requires_parent(self) -> None:
        self.write("PM/milestones.json", json.dumps({"small_milestones": [{"id": f"M1.{i}"} for i in range(1, 7)]}))
        self.invoke("validate-milestones", expected=1)

    def test_08_te_cannot_write_product_code(self) -> None:
        batch = {key: [] for key in ("test_case_ids", "commands", "results", "evidence_paths", "blocked_items", "tool_requests", "security_observations")}
        batch.update({"batch_id": "B1", "environment": "Windows", "started_at": "x", "finished_at": "y", "stdout": "", "stderr": "", "written_paths": ["src/app.py"]})
        self.write("TE/b1.json", json.dumps(batch))
        self.invoke("validate-te", "--batch", "TE/b1.json", "--status", "PASS", expected=1)

    def test_09_te_schema_requires_all_fields(self) -> None:
        self.write("TE/bad.json", "{}")
        self.invoke("validate-te", "--batch", "TE/bad.json", "--status", "PASS", expected=1)

    def test_10_logs_redact_secret_and_have_trace(self) -> None:
        self.write("PM/a.md", "x")
        self.approve("phase_exit", "1", ["PRD=PM/a.md"], reason="token=supersecret")
        event = json.loads((self.project / "Logs/governance_events.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        self.assertIn("trace_id", event); self.assertNotIn("supersecret", json.dumps(event, ensure_ascii=False))

    def test_11_unicode_and_interpreter_detection(self) -> None:
        self.write("PM/繁體 😀.md", "測試")
        result = self.invoke("detect-python")
        self.assertIn("interpreters", result.stdout)

    def test_12_legacy_phase_hook_is_fail_closed_and_repeatable(self) -> None:
        command = [sys.executable, str(PHASE_HOOK), "--project_dir", str(self.project), "--from_phase", "0", "--to_phase", "1", "--ceo_signature", "/approve"]
        first = subprocess.run(command, text=True, encoding="utf-8", capture_output=True)
        second = subprocess.run(command, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(first.returncode, 1); self.assertEqual(second.returncode, 1)

    def test_13_migration_dry_run_does_not_create_state_overwrite(self) -> None:
        self.write(".agents/.current_phase.lock", "2")
        self.invoke("migrate")
        self.assertTrue((self.project / "Logs/migration_report.json").is_file())

    def test_14_phase3_cap_requires_pm_expansion_approval(self) -> None:
        catalog = {"test_cases": [{"test_case_id": f"T{i}"} for i in range(31)]}
        self.write("TDD_DQA/test_catalog.json", json.dumps(catalog))
        module = __import__("importlib.util").util
        spec = module.spec_from_file_location("governance", SCRIPT); governance = module.module_from_spec(spec); spec.loader.exec_module(governance)
        self.assertTrue(governance.validate_test_catalog(self.project, "3", "TDD_DQA/test_catalog.json"))

    def test_15_agent_schema_is_valid(self) -> None:
        validator = ROOT / "skills/Johnny-project-team/scripts/validate_agent_configs.py"
        result = subprocess.run([sys.executable, str(validator), "--agents-dir", str(ROOT / "agents")], text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


    def test_16_tampered_dqa_report_blocks_gate(self) -> None:
        self.phase0_ready()
        self.write("TDD_DQA/phase0.json", json.dumps({"role": "TDD", "phase": "0", "verdict": "PASS", "evidence_paths": ["changed"]}))
        self.invoke("gate", "--from-phase", "0", "--to-phase", "1", "--signature", "/approve", expected=1)

    def test_17_how_change_invalidates_phase0_exit(self) -> None:
        self.phase0_ready()
        self.write("Architect/Phase0_How_Architecture_Draft.md", "5W-TRACE: D2 -> What-1。")
        self.invoke("gate", "--from-phase", "0", "--to-phase", "1", "--signature", "/approve", expected=1)

    def test_18_init_refuses_to_overwrite_history(self) -> None:
        self.invoke("init", expected=1)
if __name__ == "__main__":
    unittest.main()

