from __future__ import annotations

import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_tdd_guidance_requires_vertical_red_green_refactor() -> None:
    guidance = (SKILL_ROOT / "references" / "tdd-integration.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "每次只推進一個可觀察行為",
        "end-to-end tracer bullet",
        "公開介面",
        "獨立 oracle",
        "**RED**",
        "**GREEN**",
        "**REFACTOR**",
        "禁止先批次寫完多個測試",
        "DQA 不共同設計或修改產品實作",
    ):
        assert required in guidance


def test_context_manifest_routes_engineer_to_tdd_method() -> None:
    manifest = json.loads(
        (SKILL_ROOT / "assets" / "templates" / "context-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["routes"]["tdd_method"].startswith("references/tdd-integration.md")
    assert (SKILL_ROOT / "assets" / "templates" / "tdd-cycle-evidence.md").is_file()
