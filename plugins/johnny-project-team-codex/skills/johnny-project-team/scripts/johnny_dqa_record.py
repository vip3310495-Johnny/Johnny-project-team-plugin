"""Single review-cycle state machine for tree-bound Johnny DQA evidence."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from johnny_common import (
    STATE_DIR,
    append_jsonl,
    atomic_json,
    git_root,
    is_enabled,
    read_json,
    run_git,
    staged_tree,
    state_lock,
    subject_tree,
)
from johnny_ecc_rules import select_rules

ROLES = ("tdd", "sdd", "claude")
DQA_ESCALATION_THRESHOLD = 5


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configured_roles(config: dict) -> list[str]:
    roles = ["tdd", "sdd"]
    claude = config.get("claude_dqa", {})
    if claude.get("enabled", False) and claude.get("required", False):
        roles.append("claude")
    return roles


def new_status(
    *,
    prior: dict,
    scope: str,
    ticket: str,
    current_subject: str,
    current_commit: str,
    roles: list[str],
) -> dict:
    same_milestone = (
        prior.get("scope", "ticket") == scope and prior.get("ticket") == ticket
    )
    return {
        "schema_version": 2,
        "scope": scope,
        "ticket": ticket,
        "large_milestone": prior.get("large_milestone"),
        "review_cycle": int(prior.get("review_cycle", 0)) + 1,
        "subject_tree": current_subject,
        "commit_tree": current_commit,
        "workflow": roles,
        "required_roles": list(roles),
        "completed_roles": [],
        "results": {},
        "reviews": {},
        "last_rejection": None,
        "rejection_counts": (
            dict(prior.get("rejection_counts", {})) if same_milestone else {}
        ),
        "escalation": prior.get("escalation") if same_milestone else None,
    }


def append_history(project: Path, event: str, status: dict, detail: dict) -> None:
    append_jsonl(
        project / STATE_DIR / "dqa-history.jsonl",
        {
            "schema_version": 2,
            "event": event,
            "at": utc_now(),
            "scope": status["scope"],
            "ticket": status["ticket"],
            "review_cycle": status["review_cycle"],
            "subject_tree": status["subject_tree"],
            "commit_tree": status["commit_tree"],
            **detail,
        },
    )


def verdict_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("verdict")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--scope", choices=("ticket", "phase4"), default="ticket")
    parser.add_argument("--role", choices=ROLES, required=True)
    parser.add_argument("--result", choices=("PASS", "FAIL"), required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--cycle", type=int)


def reopen_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("reopen")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument(
        "--cause",
        choices=("tdd-fail", "sdd-fail", "claude-fail", "ceo-reject"),
        required=True,
    )
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--reviewer-id", required=True)


def resolve_escalation_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("resolve-escalation")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--role", choices=ROLES, required=True)
    parser.add_argument("--approval", required=True)
    parser.add_argument("--resolution", required=True)


def load_context(args: argparse.Namespace) -> tuple[Path, dict, str, str, list[str]]:
    project = git_root(args.project)
    if not is_enabled(project):
        raise ValueError("project is not enabled")
    config = read_json(project / STATE_DIR / "config.json", {}) or {}
    product_paths = config.get("product_paths", [])
    return (
        project,
        config,
        subject_tree(project, product_paths),
        staged_tree(project),
        configured_roles(config),
    )


def record_verdict(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    try:
        project, config, current_subject, current_commit, roles = load_context(args)
    except ValueError as error:
        parser.error(str(error))
    ticket = args.ticket.strip()
    evidence = args.evidence.strip()
    reviewer = args.reviewer_id.strip()
    if not ticket or not evidence or not reviewer:
        parser.error("ticket, evidence, and reviewer-id must be non-empty")
    staged_paths = [
        value
        for value in run_git(project, "diff", "--cached", "--name-only").splitlines()
        if value.strip()
    ]
    selection = select_rules(project, staged_paths)
    atomic_json(project / STATE_DIR / "ecc-selection.json", selection)

    status_path = project / STATE_DIR / "dqa-status.json"
    with state_lock(project):
        prior = read_json(status_path, {}) or {}
        if (
            prior.get("schema_version") != 2
            or prior.get("subject_tree") != current_subject
            or prior.get("scope", "ticket") != args.scope
            or prior.get("ecc_selection_sha256") not in (
                None,
                selection["selection_sha256"],
            )
        ):
            status = new_status(
                prior=prior,
                scope=args.scope,
                ticket=ticket,
                current_subject=current_subject,
                current_commit=current_commit,
                roles=roles,
            )
            status["ecc_selection_sha256"] = selection["selection_sha256"]
            append_history(
                project,
                "cycle-opened",
                status,
                {"cause": "new-subject-tree", "reviewer_id": reviewer},
            )
        else:
            status = prior
            if status.get("ticket") != ticket:
                parser.error(
                    f"subject tree is already bound to ticket {status.get('ticket')}"
                )
            status["commit_tree"] = current_commit
        status["ecc_selection_sha256"] = selection["selection_sha256"]
        escalation = status.get("escalation")
        if escalation and escalation.get("active", False):
            parser.error(
                "milestone is frozen after five rejections by "
                f"{escalation.get('role')} DQA; CEO resolution is required"
            )
        if args.cycle is not None and args.cycle != status["review_cycle"]:
            parser.error(
                f"verdict cycle {args.cycle} does not match active cycle "
                f"{status['review_cycle']}"
            )

        results = dict(status.get("results", {}))
        reviews = dict(status.get("reviews", {}))
        if args.role == "sdd" and results.get("tdd") != "PASS":
            parser.error("SDD DQA requires TDD DQA PASS in the active review cycle")
        if args.role == "claude" and results.get("sdd") != "PASS":
            parser.error("Claude DQA requires TDD and SDD PASS in the active review cycle")

        review = {
            "result": args.result,
            "evidence": evidence,
            "reviewer_id": reviewer,
            "reviewed_at": utc_now(),
            "ecc_selection_sha256": selection["selection_sha256"],
        }
        reviews[args.role] = review
        results[args.role] = args.result
        rejection_count = None
        if args.result == "FAIL" and args.scope == "ticket":
            counts = dict(status.get("rejection_counts", {}))
            rejection_count = int(counts.get(args.role, 0)) + 1
            counts[args.role] = rejection_count
            status["rejection_counts"] = counts

        if args.result == "FAIL" and args.role == "sdd":
            append_history(project, "verdict", status, {"role": args.role, **review})
            status = new_status(
                prior=status,
                scope=args.scope,
                ticket=ticket,
                current_subject=current_subject,
                current_commit=current_commit,
                roles=roles,
            )
            status["last_rejection"] = {
                "role": "sdd",
                "reason": evidence,
                "at": utc_now(),
            }
            append_history(
                project,
                "cycle-reopened",
                status,
                {"cause": "sdd-fail", "reviewer_id": reviewer, "evidence": evidence},
            )
        else:
            if args.result == "FAIL":
                if args.role == "tdd":
                    results = {}
                    reviews = {}
                    status["required_roles"] = ["tdd"]
                else:
                    results = {
                        key: value
                        for key, value in results.items()
                        if key in ("tdd", "sdd") and value == "PASS"
                    }
                    reviews = {
                        key: value for key, value in reviews.items() if key in results
                    }
                    status["required_roles"] = ["claude"]
                status["last_rejection"] = {
                    "role": args.role,
                    "reason": evidence,
                    "at": utc_now(),
                }
            else:
                status["last_rejection"] = None
                if args.role == "tdd":
                    status["required_roles"] = ["sdd"]
                elif args.role == "sdd":
                    status["required_roles"] = (
                        ["claude"] if "claude" in status["workflow"] else []
                    )
                else:
                    status["required_roles"] = []
            status["results"] = results
            status["reviews"] = reviews
            status["completed_roles"] = [
                role for role in ROLES if results.get(role) == "PASS"
            ]
            append_history(project, "verdict", status, {"role": args.role, **review})
        if args.result == "FAIL" and args.scope == "ticket":
            limit = DQA_ESCALATION_THRESHOLD
            if rejection_count is not None and rejection_count >= limit:
                status["escalation"] = {
                    "active": True,
                    "role": args.role,
                    "rejection_count": rejection_count,
                    "threshold": limit,
                    "reviewer_id": reviewer,
                    "reason": evidence,
                    "escalated_at": utc_now(),
                    "requires": "CEO resolution",
                }
                status["required_roles"] = []
                append_history(
                    project,
                    "ceo-escalation-opened",
                    status,
                    {
                        "role": args.role,
                        "rejection_count": rejection_count,
                        "threshold": limit,
                        "reviewer_id": reviewer,
                        "evidence": evidence,
                    },
                )
        atomic_json(status_path, status)

    print(
        f"{ticket} {args.role.upper()} DQA {args.result} recorded "
        f"for cycle {status['review_cycle']} subject {current_subject}"
    )
    return 0


def resolve_escalation(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> int:
    try:
        project, _config, current_subject, current_commit, roles = load_context(args)
    except ValueError as error:
        parser.error(str(error))
    approval = args.approval.strip()
    resolution = args.resolution.strip()
    if not approval or not resolution:
        parser.error("approval and resolution must be non-empty")
    status_path = project / STATE_DIR / "dqa-status.json"
    with state_lock(project):
        prior = read_json(status_path, {}) or {}
        escalation = prior.get("escalation") or {}
        if prior.get("ticket") != args.ticket:
            parser.error("active DQA status does not match the requested ticket")
        if not escalation.get("active", False):
            parser.error("the requested milestone has no active CEO escalation")
        if escalation.get("role") != args.role:
            parser.error(
                f"active escalation belongs to {escalation.get('role')} DQA"
            )
        status = new_status(
            prior=prior,
            scope=prior.get("scope", "ticket"),
            ticket=args.ticket,
            current_subject=current_subject,
            current_commit=current_commit,
            roles=roles,
        )
        counts = dict(status.get("rejection_counts", {}))
        counts[args.role] = 0
        status["rejection_counts"] = counts
        status["escalation"] = None
        status["last_rejection"] = {
            "role": args.role,
            "reason": f"CEO resolution: {resolution}",
            "at": utc_now(),
        }
        if args.role == "claude" and prior.get("subject_tree") == current_subject:
            status["results"] = {
                key: value
                for key, value in prior.get("results", {}).items()
                if key in ("tdd", "sdd") and value == "PASS"
            }
            status["reviews"] = {
                key: value
                for key, value in prior.get("reviews", {}).items()
                if key in status["results"]
            }
            status["completed_roles"] = ["tdd", "sdd"]
            status["required_roles"] = ["claude"]
        append_history(
            project,
            "ceo-escalation-resolved",
            status,
            {
                "role": args.role,
                "approval": approval,
                "resolution": resolution,
            },
        )
        atomic_json(status_path, status)
    print(
        f"{args.ticket} {args.role.upper()} DQA escalation resolved by CEO; "
        f"review cycle {status['review_cycle']} opened"
    )
    return 0


def reopen(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    try:
        project, _config, current_subject, current_commit, roles = load_context(args)
    except ValueError as error:
        parser.error(str(error))
    status_path = project / STATE_DIR / "dqa-status.json"
    with state_lock(project):
        prior = read_json(status_path, {}) or {}
        if prior.get("ticket") != args.ticket:
            parser.error("active DQA status does not match the requested ticket")
        status = new_status(
            prior=prior,
            scope=prior.get("scope", "ticket"),
            ticket=args.ticket,
            current_subject=current_subject,
            current_commit=current_commit,
            roles=roles,
        )
        if args.cause == "claude-fail" and prior.get("subject_tree") == current_subject:
            status["results"] = {
                key: value
                for key, value in prior.get("results", {}).items()
                if key in ("tdd", "sdd") and value == "PASS"
            }
            status["reviews"] = {
                key: value
                for key, value in prior.get("reviews", {}).items()
                if key in status["results"]
            }
            status["completed_roles"] = ["tdd", "sdd"]
            status["required_roles"] = ["claude"]
        status["last_rejection"] = {
            "role": args.cause.removesuffix("-fail"),
            "reason": args.evidence,
            "at": utc_now(),
        }
        append_history(
            project,
            "cycle-reopened",
            status,
            {
                "cause": args.cause,
                "reviewer_id": args.reviewer_id,
                "evidence": args.evidence,
            },
        )
        atomic_json(status_path, status)
    print(f"{args.ticket} reopened as review cycle {status['review_cycle']}")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] not in ("verdict", "reopen", "resolve-escalation"):
        argv = ["verdict", *argv]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    verdict_parser(subparsers)
    reopen_parser(subparsers)
    resolve_escalation_parser(subparsers)
    args = parser.parse_args(argv)
    if args.command == "verdict":
        return record_verdict(args, parser)
    if args.command == "reopen":
        return reopen(args, parser)
    return resolve_escalation(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
