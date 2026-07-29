from __future__ import annotations

import ast
import re
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


def test_formal_references_only_name_existing_scripts() -> None:
    existing = {path.name for path in SCRIPTS.glob("*.py")}
    existing.update(path.name for path in (ROOT.parents[1] / "hooks").glob("*.py"))
    documents = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
    for document in documents:
        if document == CATALOG:
            continue
        content = document.read_text(encoding="utf-8")
        references = re.findall(
            r"`(scripts/)?([a-z0-9_]+\.py)(?:\s[^`]*)?`",
            content,
        )
        for prefix, name in references:
            if prefix or name.startswith("johnny_"):
                assert name in existing, f"{document.name} references missing script {name}"


def test_formal_references_do_not_invoke_experimental_placeholders() -> None:
    stems = {path.stem for path in (ROOT / "experimental").glob("*.py")}
    documents = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
    for document in documents:
        if document == CATALOG:
            continue
        content = document.read_text(encoding="utf-8")
        for stem in stems:
            assert stem not in content, f"{document.name} invokes experimental {stem}"
