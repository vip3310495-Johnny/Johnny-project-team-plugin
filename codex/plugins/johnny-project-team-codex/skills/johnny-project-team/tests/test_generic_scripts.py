from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CATALOG = ROOT / "references" / "script-catalog.md"


def test_formal_scripts_parse_and_are_documented() -> None:
    catalog = CATALOG.read_text(encoding="utf-8")
    for path in sorted(SCRIPTS.glob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assert path.name in catalog, f"{path.name} lacks a skill application description"


def test_experimental_scripts_are_quarantined_and_not_formal_references() -> None:
    experimental = ROOT / "experimental"
    catalog = CATALOG.read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert len(list(experimental.glob("*.py"))) == 29
    for path in experimental.glob("*.py"):
        assert path.name in catalog
        assert f"experimental/{path.name}" not in skill
