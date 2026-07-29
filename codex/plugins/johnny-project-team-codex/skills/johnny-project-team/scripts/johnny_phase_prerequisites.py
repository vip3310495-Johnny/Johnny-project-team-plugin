"""Validate structured evidence required by selected Johnny phase transitions."""

from __future__ import annotations

import hashlib
import json
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


def _load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"phase evidence is unreadable: {error}") from error
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("phase evidence must be a schema_version 1 JSON object")
    return value


def _require_fields(value: dict, fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if not _non_empty_list(value.get(field))]
    if missing:
        raise ValueError(f"{label} evidence is incomplete: {', '.join(missing)}")


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


def validate_phase_evidence(to_phase: int, path: Path | None) -> dict | None:
    """Return a hash-bound evidence summary for transitions with prerequisites."""
    required = to_phase in {1, 3, 5}
    if not required:
        if path is not None:
            raise ValueError("--evidence is only valid for transitions to Phase 1, 3, or 5")
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
    else:
        if evidence.get("integrated_tdd") != "PASS" or evidence.get("integrated_sdd") != "PASS":
            raise ValueError("Phase 4 evidence requires integrated_tdd and integrated_sdd PASS")
        _require_fields(
            evidence,
            ("fixed_tolerance_evidence", "as_built_inputs"),
            "Phase 4",
        )
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "to_phase": to_phase,
    }
