"""Select every applicable bundled ECC rule for the current code paths."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

RULES_ROOT = Path(__file__).resolve().parents[1] / "references" / "rules"

RULESET_ORDER = (
    "common",
    "angular",
    "arkts",
    "cpp",
    "csharp",
    "dart",
    "fsharp",
    "golang",
    "java",
    "kotlin",
    "nuxt",
    "perl",
    "php",
    "python",
    "react",
    "react-native",
    "ruby",
    "rust",
    "swift",
    "typescript",
    "vue",
    "web",
)

LANGUAGE_HINTS = {
    "arkts": ((".ets",), ("oh-package.json5", "build-profile.json5", "module.json5")),
    "cpp": ((".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"), ("CMakeLists.txt",)),
    "csharp": ((".cs", ".csproj", ".csx", ".sln", ".slnx"), ()),
    "dart": ((".dart",), ("pubspec.yaml", "analysis_options.yaml")),
    "fsharp": ((".fs", ".fsproj", ".fsx"), ()),
    "golang": ((".go",), ("go.mod", "go.sum")),
    "java": ((".java",), ("pom.xml",)),
    "kotlin": ((".kt", ".kts"), ()),
    "perl": ((".cgi", ".pl", ".pm", ".psgi", ".t"), ("cpanfile",)),
    "php": ((".php",), ("composer.json", "composer.lock")),
    "python": ((".py", ".pyi"), ("pyproject.toml", "requirements.txt", "Pipfile")),
    "ruby": ((".gemspec", ".rake", ".rb"), ("Gemfile", "Gemfile.lock")),
    "rust": ((".rs",), ("Cargo.toml", "Cargo.lock")),
    "swift": ((".swift",), ("Package.swift",)),
    "typescript": ((".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"), ("tsconfig.json",)),
}

WEB_SUFFIXES = (".css", ".html", ".less", ".sass", ".scss", ".svelte")
IGNORED_PARTS = {
    ".git",
    ".johnny",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "vendor",
}


def _run_git(project: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _normalize_paths(paths: Iterable[str]) -> list[str]:
    normalized = set()
    for raw_path in paths:
        if not raw_path:
            continue
        path = raw_path.replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        candidate = PurePosixPath(path)
        if set(candidate.parts) & IGNORED_PARTS:
            continue
        normalized.add(str(candidate))
    return sorted(path for path in normalized if path not in {"", "."})


def project_paths(project: Path) -> list[str]:
    """Return repository files without traversing ignored dependency trees."""
    paths = _run_git(project, "ls-files", "--cached", "--others", "--exclude-standard")
    if paths:
        return _normalize_paths(paths)
    return _normalize_paths(
        str(path.relative_to(project))
        for path in project.rglob("*")
        if path.is_file()
    )


def changed_paths(project: Path) -> list[str]:
    """Prefer active changes; fall back to all project files for initial routing."""
    paths = set(_run_git(project, "diff", "--name-only", "HEAD"))
    paths.update(_run_git(project, "diff", "--cached", "--name-only"))
    paths.update(_run_git(project, "ls-files", "--others", "--exclude-standard"))
    return _normalize_paths(paths) or project_paths(project)


def _package_dependency_sets(project: Path, paths: Sequence[str]) -> list[set[str]]:
    """Read every tracked project package manifest, including monorepo packages."""
    dependency_sets: list[set[str]] = []
    manifests = [
        project / path
        for path in paths
        if PurePosixPath(path).name.lower() == "package.json"
    ]
    root_manifest = project / "package.json"
    if root_manifest.is_file() and root_manifest not in manifests:
        manifests.append(root_manifest)
    for package in manifests:
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        dependencies: set[str] = set()
        if not isinstance(data, dict):
            continue
        for key in (
            "dependencies",
            "devDependencies",
            "peerDependencies",
            "optionalDependencies",
        ):
            values = data.get(key, {})
            if isinstance(values, dict):
                dependencies.update(str(name).lower() for name in values)
        dependency_sets.append(dependencies)
    return dependency_sets


def _has_hint(paths: Sequence[str], suffixes: Sequence[str], names: Sequence[str]) -> bool:
    lowered_names = {name.lower() for name in names}
    return any(
        path.lower().endswith(tuple(suffix.lower() for suffix in suffixes))
        or PurePosixPath(path).name.lower() in lowered_names
        for path in paths
    )


def detect_rulesets(project: Path, all_paths: Sequence[str] | None = None) -> list[str]:
    """Detect the installed ECC layers without applying overlapping framework rules."""
    paths = list(all_paths) if all_paths is not None else project_paths(project)
    dependency_sets = _package_dependency_sets(project, paths)
    dependencies = set().union(*dependency_sets) if dependency_sets else set()
    selected = {"common"}

    for ruleset, (suffixes, names) in LANGUAGE_HINTS.items():
        if _has_hint(paths, suffixes, names):
            selected.add(ruleset)

    native = any({"react-native", "expo"} & values for values in dependency_sets)
    angular = "@angular/core" in dependencies or any(
        PurePosixPath(path).name.lower() == "angular.json" for path in paths
    )
    nuxt = "nuxt" in dependencies or any(
        PurePosixPath(path).name.lower().startswith("nuxt.config") for path in paths
    )
    vue = "vue" in dependencies or any(path.lower().endswith(".vue") for path in paths)
    react_web = any(
        "react" in values and not ({"react-native", "expo"} & values)
        for values in dependency_sets
    )
    react = react_web or (
        not native and any(path.lower().endswith((".jsx", ".tsx")) for path in paths)
    )

    if native:
        selected.add("react-native")
    if angular:
        selected.add("angular")
    if nuxt:
        selected.update(("nuxt", "vue"))
    elif vue:
        selected.add("vue")
    if react:
        selected.add("react")
    if angular or nuxt or vue or react or any(
        path.lower().endswith(WEB_SUFFIXES) for path in paths
    ):
        selected.add("web")

    return [name for name in RULESET_ORDER if name in selected]


def rule_globs(path: Path) -> list[str]:
    """Parse the small YAML frontmatter subset used by ECC rule files."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return []
    if not lines or lines[0].strip() != "---":
        return []
    globs: list[str] = []
    in_paths = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped == "paths:":
            in_paths = True
            continue
        if in_paths and stripped.startswith("- "):
            value = stripped[2:].strip().strip("\"'")
            if value:
                globs.append(value)
        elif in_paths and stripped and not line.startswith((" ", "\t")):
            in_paths = False
    return globs


def _matches(path: str, pattern: str) -> bool:
    candidate = PurePosixPath(path)
    if candidate.match(pattern) or fnmatch.fnmatchcase(path, pattern):
        return True
    return pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:])


def select_rules(
    project: Path,
    paths: Sequence[str] | None = None,
    rules_root: Path = RULES_ROOT,
) -> dict:
    """Return common rules plus every technology rule matching the active paths."""
    project = project.resolve()
    all_paths = project_paths(project)
    active_paths = _normalize_paths(paths) if paths is not None else changed_paths(project)
    rulesets = detect_rulesets(project, all_paths)
    selected: list[str] = []
    matched_by: dict[str, list[str]] = {}

    for ruleset in rulesets:
        directory = rules_root / ruleset
        for rule in sorted(directory.glob("*.md")):
            relative = rule.relative_to(rules_root).as_posix()
            globs = rule_globs(rule)
            matches = (
                active_paths
                if ruleset == "common" or not globs
                else [
                    path
                    for path in active_paths
                    if any(_matches(path, pattern) for pattern in globs)
                ]
            )
            if ruleset == "common" or matches:
                selected.append(relative)
                matched_by[relative] = matches[:20]

    return {
        "schema_version": 1,
        "rules_root": str(rules_root.resolve()),
        "active_paths": active_paths,
        "detected_rulesets": rulesets,
        "rule_files": selected,
        "matched_by": matched_by,
    }


def format_context(selection: dict) -> str:
    files = ", ".join(selection["rule_files"])
    return (
        "ECC rules are mandatory before writing or reviewing matching code. "
        f"Detected rulesets: {', '.join(selection['detected_rulesets'])}. "
        f"Read every selected file under {selection['rules_root']}: {files}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--paths", nargs="*")
    parser.add_argument("--format", choices=("json", "paths", "context"), default="json")
    args = parser.parse_args()
    selection = select_rules(args.project, args.paths)
    if args.format == "paths":
        root = Path(selection["rules_root"])
        print("\n".join(str(root / path) for path in selection["rule_files"]))
    elif args.format == "context":
        print(format_context(selection))
    else:
        print(json.dumps(selection, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
