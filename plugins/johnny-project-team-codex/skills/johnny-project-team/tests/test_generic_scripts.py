from __future__ import annotations

import ast
import json
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


def test_experimental_placeholders_are_not_packaged() -> None:
    assert not (ROOT / "experimental").exists()


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


def test_te_contract_is_a_schema_and_obsolete_role_references_are_removed() -> None:
    schema_path = ROOT / "assets" / "schemas" / "te-result.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["status"]["enum"] == ["PASS", "FAIL", "BLOCKED"]
    assert set(schema["required"]) == set(schema["properties"])

    orchestration = (ROOT / "references" / "dqa-te-orchestration.md").read_text(
        encoding="utf-8"
    )
    assert "assets/schemas/te-result.schema.json" in orchestration
    for obsolete in (
        "te-persona.md",
        "verifier-guidelines.md",
        "engineering-agent.md",
        "personas.md",
    ):
        assert not (ROOT / "references" / obsolete).exists()
