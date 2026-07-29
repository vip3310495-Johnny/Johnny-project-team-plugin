from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RULES = ROOT / "references" / "rules"
sys.path.insert(0, str(SCRIPTS))

from johnny_ecc_rules import (
    RULESET_ORDER,
    detect_rulesets,
    format_context,
    rule_globs,
    select_rules,
)


def write_project(
    project: Path,
    path: str,
    *,
    dependencies: tuple[str, ...] = (),
) -> None:
    target = project / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("sample\n", encoding="utf-8")
    if dependencies:
        (project / "package.json").write_text(
            json.dumps(
                {"dependencies": {dependency: "latest" for dependency in dependencies}}
            ),
            encoding="utf-8",
        )


def test_catalog_covers_every_bundled_ruleset_and_rule_file() -> None:
    directories = {
        path.name for path in RULES.iterdir() if path.is_dir()
    }
    assert set(RULESET_ORDER) == directories
    assert len(list(RULES.rglob("*.md"))) == 122
    for directory in directories - {"common"}:
        for rule in (RULES / directory).glob("*.md"):
            assert rule_globs(rule), f"{rule.relative_to(RULES)} has no paths frontmatter"


@pytest.mark.parametrize(
    ("ruleset", "path", "dependencies"),
    [
        ("angular", "src/app.component.ts", ("@angular/core",)),
        ("arkts", "entry/src/main.ets", ()),
        ("cpp", "src/main.cpp", ()),
        ("csharp", "src/Program.cs", ()),
        ("dart", "lib/main.dart", ()),
        ("fsharp", "src/Program.fs", ()),
        ("golang", "cmd/main.go", ()),
        ("java", "src/Main.java", ()),
        ("kotlin", "src/main.kt", ()),
        ("nuxt", "pages/index.vue", ("nuxt",)),
        ("perl", "script.pl", ()),
        ("php", "public/index.php", ()),
        ("python", "src/app.py", ()),
        ("react", "src/App.tsx", ("react",)),
        ("react-native", "src/App.tsx", ("react", "react-native")),
        ("ruby", "app/main.rb", ()),
        ("rust", "src/main.rs", ()),
        ("swift", "Sources/Main.swift", ()),
        ("typescript", "src/index.ts", ()),
        ("vue", "src/App.vue", ("vue",)),
        ("web", "public/index.html", ()),
    ],
)
def test_every_technology_ruleset_can_be_detected(
    tmp_path: Path,
    ruleset: str,
    path: str,
    dependencies: tuple[str, ...],
) -> None:
    write_project(tmp_path, path, dependencies=dependencies)
    assert ruleset in detect_rulesets(tmp_path)


def test_selector_loads_common_and_all_matching_language_rules(tmp_path: Path) -> None:
    write_project(tmp_path, "src/app.py")
    write_project(tmp_path, "native/lib.rs")
    selection = select_rules(tmp_path, ["src/app.py", "native/lib.rs"])

    assert selection["detected_rulesets"] == ["common", "python", "rust"]
    assert len([path for path in selection["rule_files"] if path.startswith("common/")]) == 10
    assert "python/coding-style.md" in selection["rule_files"]
    assert "python/security.md" in selection["rule_files"]
    assert "rust/coding-style.md" in selection["rule_files"]
    assert "rust/testing.md" in selection["rule_files"]
    assert "react-native/coding-style.md" not in selection["rule_files"]
    assert "Read every selected file" in format_context(selection)


def test_react_web_layers_do_not_leak_into_react_native(tmp_path: Path) -> None:
    write_project(
        tmp_path,
        "src/App.tsx",
        dependencies=("react", "react-native", "expo"),
    )
    selection = select_rules(tmp_path, ["src/App.tsx"])

    assert selection["detected_rulesets"] == [
        "common",
        "react-native",
        "typescript",
    ]
    assert any(path.startswith("react-native/") for path in selection["rule_files"])
    assert not any(path.startswith("react/") for path in selection["rule_files"])
    assert not any(path.startswith("web/") for path in selection["rule_files"])


def test_react_web_loads_react_typescript_and_web_layers(tmp_path: Path) -> None:
    write_project(tmp_path, "src/App.tsx", dependencies=("react",))
    selection = select_rules(tmp_path, ["src/App.tsx"])

    assert selection["detected_rulesets"] == [
        "common",
        "react",
        "typescript",
        "web",
    ]
    assert any(path.startswith("react/") for path in selection["rule_files"])
    assert any(path.startswith("typescript/") for path in selection["rule_files"])
    assert any(path.startswith("web/") for path in selection["rule_files"])


def test_nested_package_manifests_are_detected_in_monorepos(tmp_path: Path) -> None:
    write_project(tmp_path, "apps/mobile/App.tsx")
    package = tmp_path / "apps/mobile/package.json"
    package.write_text(
        json.dumps({"dependencies": {"react": "latest", "react-native": "latest"}}),
        encoding="utf-8",
    )

    selection = select_rules(tmp_path, ["apps/mobile/App.tsx"])
    assert "react-native" in selection["detected_rulesets"]
    assert "react" not in selection["detected_rulesets"]
    assert "web" not in selection["detected_rulesets"]
