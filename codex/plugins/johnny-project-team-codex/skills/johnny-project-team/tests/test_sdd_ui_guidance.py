from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "assets" / "agents" / "johnny-sdd-dqa.toml"


def test_sdd_ui_review_uses_screenshots_before_omniparser() -> None:
    text = PROFILE.read_text(encoding="utf-8")

    assert "first review actual screenshots against the approved reference" in text
    assert "`omniparser` skill only when the screenshots do not provide" in text
    assert "Treat OmniParser timing as non-binding operating guidance" in text
    assert "`--max-dimension 640 --box-threshold 0.4`" in text
    assert "480-second outer timeout" in text
    assert "`omniparser-runner`" not in text
