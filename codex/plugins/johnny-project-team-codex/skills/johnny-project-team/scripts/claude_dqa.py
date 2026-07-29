"""Run a real Claude CLI review and record tree-bound DQA evidence."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from johnny_common import STATE_DIR, atomic_json, git_root, is_enabled, read_json, run_git
from johnny_ecc_rules import select_rules


def resolve_claude() -> str | None:
    for name in ("claude.cmd", "claude.exe", "claude"):
        found = shutil.which(name)
        if found:
            return found
    return None


def build_prompt(diff: str, selection: dict) -> str:
    absolute_rules = [
        {
            "path": str(Path(selection["rules_root"]) / relative),
            "sha256": selection["rule_hashes"][relative],
        }
        for relative in selection["rule_files"]
    ]
    ecc_contract = json.dumps(
        {
            "selection_sha256": selection["selection_sha256"],
            "active_paths": selection["active_paths"],
            "rules": absolute_rules,
        },
        ensure_ascii=False,
        indent=2,
    )
    return (
        "You are the independent Claude DQA reviewer. Review the staged diff below "
        "for correctness, security, regressions, test gaps, and spec mismatch. "
        "Before deciding, read every ECC rule file in the manifest and apply it to "
        "the matching active paths. A missing or unreadable rule is a blocking FAIL. "
        "Return exactly PASS only if there are no blocking findings. Otherwise return "
        "FAIL followed by concise findings.\n\nECC selection manifest:\n"
        + ecc_contract
        + "\n\nStaged diff:\n"
        + diff
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--scope", choices=("ticket", "phase4"), default="ticket")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--reviewer-id", default="claude-cli")
    args = parser.parse_args()
    project = git_root(args.project)
    if not is_enabled(project):
        parser.error("project is not enabled")
    config = read_json(project / STATE_DIR / "config.json", {})
    if not config.get("claude_dqa", {}).get("manual_allowed", True):
        parser.error("manual Claude DQA is disabled in project config")
    executable = resolve_claude()
    if not executable:
        parser.error("Claude CLI was not found")

    diff = run_git(project, "diff", "--cached", "--no-ext-diff", "--unified=80")
    if not diff:
        parser.error("there are no staged changes to review")
    staged_paths = [
        value
        for value in run_git(project, "diff", "--cached", "--name-only").splitlines()
        if value.strip()
    ]
    selection = select_rules(project, staged_paths)
    atomic_json(project / STATE_DIR / "ecc-selection.json", selection)
    prompt = build_prompt(diff, selection)
    try:
        result = subprocess.run(
            [executable, "-p", prompt],
            cwd=project,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.timeout,
        )
        output = result.stdout.strip()
        passed = result.returncode == 0 and output == "PASS"
        error = result.stderr.strip()
    except subprocess.TimeoutExpired:
        passed, output, error = False, "", "Claude DQA timed out"

    evidence_dir = project / STATE_DIR / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{args.ticket}-claude.txt"
    evidence_path.write_text(
        f"command={executable}\nreturncode={0 if passed else 1}\n"
        f"ecc_selection_sha256={selection['selection_sha256']}\n"
        f"stdout:\n{output}\n\nstderr:\n{error}\n",
        encoding="utf-8",
        newline="\n",
    )
    recorder = Path(__file__).with_name("johnny_dqa_record.py")
    record = subprocess.run(
        [
            sys.executable,
            str(recorder),
            "verdict",
            "--project",
            str(project),
            "--ticket",
            args.ticket,
            "--scope",
            args.scope,
            "--role",
            "claude",
            "--result",
            "PASS" if passed else "FAIL",
            "--evidence",
            str(evidence_path),
            "--reviewer-id",
            args.reviewer_id,
        ],
        cwd=project,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if record.returncode != 0:
        print(record.stderr.strip())
        return record.returncode
    print(output or error)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
