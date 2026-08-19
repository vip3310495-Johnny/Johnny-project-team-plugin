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
        "端對端 tracer bullet",
        "公開介面",
        "獨立測試判定依據（oracle）",
        "**RED**",
        "**GREEN**",
        "**REFACTOR**",
        "禁止先批次寫完多個測試",
        "DQA 不參與共同設計，也不修改產品實作",
        "smoke 是固定交接閘門",
        "最小驗收探測（minimal acceptance probe）",
    ):
        assert required in guidance


def test_context_manifest_routes_engineer_to_tdd_method() -> None:
    manifest = json.loads(
        (SKILL_ROOT / "assets" / "templates" / "context-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["routes"]["tdd_method"].startswith("references/tdd-integration.md")
    assert manifest["routes"]["engineer_handoff"].startswith(
        "assets/templates/engineer-handoff.md"
    )
    assert manifest["routes"]["tdd_dqa_review"].startswith(
        "references/tdd-dqa-review.md"
    )
    assert manifest["routes"]["sdd_dqa_review"].startswith(
        "references/sdd-review.md"
    )
    assert (SKILL_ROOT / "assets" / "templates" / "tdd-cycle-evidence.md").is_file()


def test_tdd_evidence_template_stays_separate_from_handoff_report() -> None:
    cycle = (SKILL_ROOT / "assets" / "templates" / "tdd-cycle-evidence.md").read_text(
        encoding="utf-8"
    )
    handoff = (SKILL_ROOT / "assets" / "templates" / "engineer-handoff.md").read_text(
        encoding="utf-8"
    )
    assert "Cycle completion metadata" in cycle
    assert "Engineer Handoff report path" in cycle
    assert "READY_FOR_PM / BLOCKED" not in cycle
    assert "READY_FOR_PM / BLOCKED" in handoff
    assert "修改明細" in handoff
    assert "使用工具與依賴" in handoff
    assert "非預期失敗紀錄" in handoff
    assert "流程觀察" in handoff
    assert "Smoke test 閘門" in handoff
    example = (SKILL_ROOT / "assets" / "examples" / "engineer-handoff-example.md")
    assert example.is_file()
    completed = example.read_text(encoding="utf-8")
    assert "Wave1_M01_Engineer Hand off" in completed
    assert "SQLite database locked" in completed
    assert "Verdict：PASS" in completed


def test_tdd_dqa_requires_resilience_and_isolated_environment() -> None:
    review = (SKILL_ROOT / "references" / "tdd-dqa-review.md").read_text(
        encoding="utf-8"
    )
    environment = (
        SKILL_ROOT / "references" / "dqa-test-environment.md"
    ).read_text(encoding="utf-8")
    report = (
        SKILL_ROOT / "assets" / "templates" / "tdd-dqa-review-report.md"
    ).read_text(encoding="utf-8")

    for required in (
        "壓力、負載或 soak test",
        "monkey、fuzz",
        "同時具兩類風險時兩者都要執行",
        "BLOCKED_ENVIRONMENT",
        "assets/templates/tdd-dqa-review-report.md",
    ):
        assert required in review
    for required in (
        "禁止使用正式環境 credentials",
        "允許使用實際硬體",
        "緊急停止機制",
        "非正式環境 backend",
        "不得提交 PASS verdict",
    ):
        assert required in environment
    assert "Stress／monkey／resilience" in report
    assert "Actual hardware" in report
    assert "PASS / FAIL / BLOCKED_INPUT / BLOCKED_ENVIRONMENT" in report
