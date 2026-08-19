from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "assets" / "agents" / "johnny-sdd-dqa.toml"


def test_sdd_profile_routes_to_progressive_guidance() -> None:
    text = PROFILE.read_text(encoding="utf-8")

    assert "references/sdd-review.md" in text
    assert "references/sdd-ui-review.md" in text
    assert "references/dqa-test-environment.md" in text
    assert "assets/templates/sdd-dqa-review-report.md" in text
    assert "BLOCKED_INPUT" in text
    assert "BLOCKED_DEPENDENCY" in text
    assert "BLOCKED_ENVIRONMENT" in text


def test_sdd_ui_review_uses_screenshots_before_omniparser() -> None:
    text = (ROOT / "references" / "sdd-ui-review.md").read_text(encoding="utf-8")

    assert "先以實際截圖對照核准 reference" in text
    assert "只有截圖不足以判定 FIXED requirement" in text
    assert "Timeout 只是非強制操作建議" in text
    assert "`--max-dimension 640 --box-threshold 0.4`" in text
    assert "改用 480 秒" in text
    assert "`omniparser-runner`" not in text


def test_sdd_review_has_contract_matrix_and_report_contract() -> None:
    guidance = (ROOT / "references" / "sdd-review.md").read_text(encoding="utf-8")
    report = (
        ROOT / "assets" / "templates" / "sdd-dqa-review-report.md"
    ).read_text(encoding="utf-8")

    for required in (
        "Contract Matrix",
        "Engineer Handoff",
        "TDD verdict",
        "非目標",
        "BLOCKED_INPUT",
        "BLOCKED_DEPENDENCY",
        "BLOCKED_ENVIRONMENT",
    ):
        assert required in guidance
    assert "Acceptance matrix" in report
    assert "Intent、non-goals 與 compatibility" in report
    assert "PASS / FAIL / BLOCKED_INPUT / BLOCKED_DEPENDENCY / BLOCKED_ENVIRONMENT" in report
