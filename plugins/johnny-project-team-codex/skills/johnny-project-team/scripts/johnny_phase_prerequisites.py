"""Validate structured evidence required by selected Johnny phase transitions."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def _non_empty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        (
            isinstance(item, str)
            and bool(item.strip())
            and not (item.strip().startswith("<") and item.strip().endswith(">"))
        )
        or (isinstance(item, dict) and bool(item))
        for item in value
    )


def _read_json_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is unreadable: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _load(path: Path) -> dict:
    value = _read_json_object(path, "phase evidence")
    if value.get("schema_version") != 1:
        raise ValueError("phase evidence must be a schema_version 1 JSON object")
    return value


def _require_fields(value: dict, fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if not _non_empty_list(value.get(field))]
    if missing:
        raise ValueError(f"{label} evidence is incomplete: {', '.join(missing)}")


def _repository_file(project: Path, raw: str, label: str) -> Path:
    candidate = Path(raw)
    candidate = candidate if candidate.is_absolute() else project / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(project.resolve())
    except ValueError as error:
        raise ValueError(f"{label} path escapes the project: {raw}") from error
    if not candidate.is_file():
        raise ValueError(f"{label} file does not exist: {raw}")
    return candidate


def _require_existing_files(project: Path, values: object, label: str) -> list[Path]:
    if not _non_empty_list(values) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"{label} must contain project-relative file paths")
    return [_repository_file(project, item, label) for item in values]


def _current_tree(project: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD^{tree}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError("cannot resolve the current Git tree")
    return result.stdout.strip()


def _require_current_tree(project: Path, evidence: dict, label: str) -> None:
    declared = str(evidence.get("commit_tree", "")).strip()
    if not declared or declared.startswith("<"):
        raise ValueError(f"{label} evidence requires commit_tree")
    actual = _current_tree(project)
    if declared != actual:
        raise ValueError(f"{label} evidence belongs to a stale Git tree")


def _load_hashed_evidence(summary: object, expected_phase: int, label: str) -> dict:
    if not isinstance(summary, dict) or summary.get("to_phase") != expected_phase:
        raise ValueError(f"{label} evidence summary is missing")
    path = Path(str(summary.get("path", "")))
    expected_hash = str(summary.get("sha256", ""))
    if not path.is_file() or not expected_hash:
        raise ValueError(f"{label} evidence source is missing")
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_hash:
        raise ValueError(f"{label} evidence changed after approval")
    return _load(path)


def _merged_tickets(project: Path) -> set[str]:
    path = project / ".johnny" / "merge-history.jsonl"
    if not path.is_file():
        return set()
    merged: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("merge history contains invalid JSON") from error
        if isinstance(record, dict) and record.get("status") == "MERGED":
            ticket = str(record.get("ticket", "")).strip()
            if ticket:
                merged.add(ticket)
    return merged


def _require_completed_milestones(
    project: Path, expected: object, completed: object, label: str
) -> None:
    if not _non_empty_list(expected) or not all(isinstance(item, str) for item in expected):
        raise ValueError(f"{label} approved milestone list is missing")
    if not _non_empty_list(completed) or not all(isinstance(item, str) for item in completed):
        raise ValueError(f"{label} completed_milestones is missing")
    expected_set = set(expected)
    completed_set = set(completed)
    if completed_set != expected_set:
        raise ValueError(f"{label} completed milestones do not match the approved plan")
    missing_merges = sorted(expected_set - _merged_tickets(project))
    if missing_merges:
        raise ValueError(f"{label} milestones are not recorded as merged: {', '.join(missing_merges)}")


def _require_no_active_escalation(project: Path, label: str) -> None:
    path = project / ".johnny" / "dqa-status.json"
    if not path.is_file():
        return
    status = _read_json_object(path, "DQA status")
    if (status.get("escalation") or {}).get("active") is True:
        raise ValueError(f"{label} has an active DQA escalation")


def _validate_model_matrix(matrix: object) -> None:
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("Phase 2 evidence requires a non-empty model_matrix")
    required_roles = {"PM", "Architect", "Engineer", "TDD DQA", "SDD DQA"}
    approved_roles: set[str] = set()
    for entry in matrix:
        if not isinstance(entry, dict):
            raise ValueError("model_matrix entries must be objects")
        role = str(entry.get("role", "")).strip()
        model = str(entry.get("model", "")).strip()
        availability = entry.get("availability")
        approved_by = str(entry.get("approved_by", "")).strip()
        placeholders = any(
            value.startswith("<") and value.endswith(">")
            for value in (role, model, approved_by)
        )
        if (
            not role
            or not model
            or availability != "AVAILABLE"
            or not approved_by
            or placeholders
        ):
            raise ValueError(
                "every model_matrix entry requires role, model, "
                "availability=AVAILABLE, and approved_by"
            )
        approved_roles.add(role)
    missing = sorted(required_roles - approved_roles)
    if missing:
        raise ValueError("model_matrix is missing required roles: " + ", ".join(missing))


def validate_phase_evidence(
    to_phase: int, path: Path | None, project: Path | None = None
) -> dict | None:
    """Return a hash-bound evidence summary for transitions with prerequisites."""
    required = to_phase in {1, 3, 4, 5}
    if not required:
        if path is not None:
            raise ValueError("--evidence is only valid for transitions to Phase 1, 3, 4, or 5")
        return None
    if path is None:
        raise ValueError(f"transition to Phase {to_phase} requires --evidence JSON")
    evidence = _load(path)
    if int(evidence.get("to_phase", -1)) != to_phase:
        raise ValueError(f"phase evidence must declare to_phase={to_phase}")
    if to_phase == 1:
        _require_fields(
            evidence,
            ("intent", "non_goals", "observable_outcomes", "risks"),
            "Phase 0",
        )
    elif to_phase == 3:
        _require_fields(
            evidence,
            ("scope_contract_matrix", "milestones", "task_context_packs"),
            "Phase 2",
        )
        _validate_model_matrix(evidence.get("model_matrix"))
    elif to_phase == 4:
        _require_fields(
            evidence,
            ("architecture_review", "phase4_prd", "scope_contract_matrix", "milestones", "regression_baseline"),
            "Phase 4 plan",
        )
        if project is None:
            raise ValueError("Phase 4 plan validation requires the project path")
        for field in (
            "architecture_review",
            "phase4_prd",
            "scope_contract_matrix",
            "regression_baseline",
        ):
            _require_existing_files(project, evidence.get(field), f"Phase 4 plan {field}")
    else:
        _require_fields(
            evidence,
            ("completed_milestones", "regression_evidence", "detailed_architecture_report", "known_limitations"),
            "Phase 4 completion",
        )
        if project is None:
            raise ValueError("Phase 4 completion validation requires the project path")
        state = _read_json_object(project / ".johnny" / "state.json", "Johnny state")
        plan = _load_hashed_evidence(
            (state.get("phase4_execution") or {}).get("plan_evidence"),
            4,
            "Phase 4 plan",
        )
        _require_completed_milestones(
            project,
            plan.get("milestones"),
            evidence.get("completed_milestones"),
            "Phase 4",
        )
        _require_existing_files(
            project, evidence.get("regression_evidence"), "Phase 4 regression evidence"
        )
        reports = _require_existing_files(
            project,
            evidence.get("detailed_architecture_report"),
            "Phase 4 detailed architecture report",
        )
        required_sections = (
            "## 1. Final architecture",
            "## 2. Final data flow",
            "## 3. APIs, schemas, configuration, and dependencies",
            "## 4. Baseline-to-As-Built comparison",
            "## 5. Critical routes and maintenance entry points",
            "## 6. Known limitations and technical debt",
            "## 7. Reproducible commands",
            "## 8. Architect verification",
            "- Verdict: VERIFIED",
        )
        report = reports[0].read_text(encoding="utf-8")
        missing_sections = [section for section in required_sections if section not in report]
        if missing_sections:
            raise ValueError(
                "Phase 4 detailed architecture report is incomplete: "
                + ", ".join(missing_sections)
            )
        _require_current_tree(project, evidence, "Phase 4 completion")
        _require_no_active_escalation(project, "Phase 4 completion")
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "to_phase": to_phase,
    }


def validate_phase3_completion_evidence(project: Path, path: Path | None) -> dict:
    if path is None:
        raise ValueError("transition to Phase 4 requires Phase 3 completion evidence")
    evidence = _load(path)
    if evidence.get("from_phase") != 3 or evidence.get("to_phase") != 4:
        raise ValueError("Phase 3 completion evidence must declare from_phase=3 and to_phase=4")
    _require_fields(
        evidence,
        ("completed_milestones", "regression_evidence"),
        "Phase 3 completion",
    )
    state = _read_json_object(project / ".johnny" / "state.json", "Johnny state")
    phase2 = _load_hashed_evidence(
        state.get("prerequisite_evidence"), 3, "Phase 2 construction plan"
    )
    _require_completed_milestones(
        project,
        phase2.get("milestones"),
        evidence.get("completed_milestones"),
        "Phase 3",
    )
    _require_existing_files(
        project, evidence.get("regression_evidence"), "Phase 3 regression evidence"
    )
    _require_current_tree(project, evidence, "Phase 3 completion")
    _require_no_active_escalation(project, "Phase 3 completion")
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "from_phase": 3,
        "to_phase": 4,
    }
