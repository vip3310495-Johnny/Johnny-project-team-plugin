"""Resolve the exact enabled Johnny repository for lifecycle hooks."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectResolution:
    project: Path | None
    diagnostic: str | None = None


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def git_root(cwd: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def _is_exact_enabled(project: Path) -> bool:
    enabled = _read_json(project / ".johnny" / "enabled.json")
    return enabled.get("enabled") is True and enabled.get("scope") == str(project)


def resolve_project(cwd: Path) -> ProjectResolution:
    """Prefer the current Git root, otherwise find one enabled child repository.

    A lifecycle hook can be launched from a workspace folder rather than the
    repository itself. Only an unambiguous enabled child repository is selected;
    no repository is guessed when there are none or several candidates.
    """
    cwd = cwd.resolve()
    direct = git_root(cwd)
    if direct and _is_exact_enabled(direct):
        return ProjectResolution(direct)

    if not cwd.is_dir():
        return ProjectResolution(None)

    candidates: set[Path] = set()
    for marker in cwd.rglob("enabled.json"):
        if marker.parent.name != ".johnny":
            continue
        if any(part in {".git", "node_modules"} for part in marker.parts):
            continue
        root = git_root(marker.parent.parent)
        if root and _is_exact_enabled(root):
            candidates.add(root)

    if len(candidates) == 1:
        return ProjectResolution(next(iter(candidates)))
    if len(candidates) > 1:
        rendered = ", ".join(str(path) for path in sorted(candidates))
        return ProjectResolution(
            None,
            "Johnny initialization is ambiguous: multiple enabled repositories "
            f"were found below cwd ({rendered}). Open the task at one repository root.",
        )
    if (cwd / ".johnny").exists() or any(cwd.rglob(".johnny")):
        return ProjectResolution(
            None,
            "Johnny initialization found no enabled repository below cwd. Run "
            "johnny_project_hooks.py enable for the intended repository, then reopen the task there.",
        )
    return ProjectResolution(None)
