#!/usr/bin/env python3
"""Johnny Project Team 的本機、可驗證治理入口。

此工具不會安裝 Git hooks 或呼叫外部服務；所有資料以 UTF-8 寫入指定專案。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

STATE_REL = Path(".agents/project_state.json")
LEDGER_REL = Path("PM/Approval_Ledger.json")
LOG_REL = Path("Logs/governance_events.jsonl")
SAVE_STATE_REL = Path("Logs/Save_State.md")
ROLES = ("SDD", "TDD", "Security", "Claude")
TRIPLE_DQA_PHASES = {"3", "4", "5", "6"}
VALID_PHASES = {str(value) for value in range(7)}
APPROVAL_SCOPES = {
    "phase0_5w_alignment", "phase0_exit", "phase_exit", "milestone_spec",
    "phase_test_expansion", "security_spec", "external_service_cost",
}
SECRET = re.compile(r"(?i)(password|token|api[_-]?key|secret)\s*([:=])\s*([^\s,;]+)")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"無法解析 JSON：{path} ({exc})") from exc


def root(value: str) -> Path:
    result = Path(value).resolve()
    if not result.is_dir():
        raise ValueError(f"專案目錄不存在：{result}")
    return result


def rel(root_dir: Path, value: Path) -> str:
    return value.resolve().relative_to(root_dir).as_posix()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def semantic_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    # 保留段落與語意符號；忽略行尾空白、空白行數量與 HTML 註解。
    lines = []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = re.sub(r"<!--.*?-->", "", line).strip()
        if line:
            lines.append(re.sub(r"[ \t]+", " ", line))
    return "\n".join(lines)


def semantic_sha(path: Path) -> str:
    return hashlib.sha256(semantic_text(path).encode("utf-8")).hexdigest()


def project_context_sha(project: Path) -> str:
    """計算可審查產物的內容指紋，排除治理狀態、Log 與審查輸出。"""
    excluded = {".agents", "Logs", "SDD_DQA", "TDD_DQA", "Security_DQA", "Claude DQA", "TE", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
    digest = hashlib.sha256()
    for path in sorted(project.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(project)
        if not path.is_file() or any(part in excluded for part in relative.parts):
            continue
        if relative.as_posix() == "PM/Approval_Ledger.json":
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def next_action_for_phase(phase: str) -> str:
    if phase not in VALID_PHASES:
        raise ValueError(f"Phase 必須是 0～6：{phase}")
    return "完成 Phase 0A 的 5W 對齊" if phase == "0" else f"執行 Phase {phase}"


def state_for_phase(phase: str) -> dict[str, Any]:
    state = default_state()
    state["current_phase"] = phase
    state["phase_lock"] = phase
    state["next_action"] = next_action_for_phase(phase)
    return state


def default_state() -> dict[str, Any]:
    return {
        "schema_version": 1, "current_phase": "0", "current_big_milestone": None,
        "current_small_milestone": None, "phase_lock": "0", "approvals": [],
        "stale_approvals": [], "dqa_status": {}, "te_batch_status": {},
        "engineer_dispatch_status": "NOT_DISPATCHED", "blockers": [],
        "next_action": next_action_for_phase("0"), "report_pointers": [],
        "phase0_5w_status": "NOT_STARTED", "phase0_5w_approval_id": None,
        "architect_dispatch_status": "BLOCKED", "phase0_how_status": "NOT_STARTED",
        "phase0_exit_status": "NOT_STARTED", "updated_at": now(),
    }


def state_path(project: Path) -> Path:
    return project / STATE_REL


def ledger_path(project: Path) -> Path:
    return project / LEDGER_REL


def get_state(project: Path) -> dict[str, Any]:
    data = load(state_path(project), default_state())
    if not isinstance(data, dict):
        raise ValueError("project_state.json 必須是 JSON 物件")
    merged = default_state()
    merged.update(data)
    return merged


def validate_resumable_state(state: dict[str, Any]) -> None:
    phase = state.get("current_phase")
    lock = state.get("phase_lock")
    if not isinstance(phase, str) or phase not in VALID_PHASES:
        raise ValueError("project_state.json 的 current_phase 必須是 0～6")
    if lock != phase:
        raise ValueError("project_state.json 的 phase_lock 必須等於 current_phase")
    if not isinstance(state.get("next_action"), str) or not state["next_action"].strip():
        raise ValueError("project_state.json 的 next_action 必須是非空文字")


def save_state(project: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now()
    dump(state_path(project), state)


def event(project: Path, kind: str, payload: dict[str, Any]) -> None:
    def scrub(value: Any) -> Any:
        if isinstance(value, str):
            return SECRET.sub(lambda match: f"{match.group(1)}{match.group(2)}***REDACTED***", value)
        if isinstance(value, dict):
            return {key: ("***REDACTED***" if re.search(r"(?i)(password|token|api[_-]?key|secret)", str(key)) else scrub(item)) for key, item in value.items()}
        if isinstance(value, list):
            return [scrub(item) for item in value]
        return value
    clean = scrub(payload)
    record = {"timestamp": now(), "timezone": str(dt.datetime.now().astimezone().tzinfo),
              "event_type": kind, "trace_id": uuid.uuid4().hex,
              "role": clean.get("role", "governance"), "agent_id": clean.get("agent_id"), "command": clean.get("command"),
              "tool_versions": clean.get("tool_versions", {}), "environment": clean.get("environment", {"platform": platform.platform(), "python": sys.version}),
              "stdout": clean.get("stdout"), "stderr": clean.get("stderr"), "exception": clean.get("exception"),
              "retry": clean.get("retry", []), "evidence_paths": clean.get("evidence_paths", []), "payload": clean}
    path = project / LOG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def ledger(project: Path) -> dict[str, Any]:
    data = load(ledger_path(project), {"schema_version": 1, "entries": []})
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError("Approval_Ledger.json 必須含 entries 陣列")
    return data


def invalidated_approval_ids(project: Path) -> set[str]:
    return {str(item.get("approval_id")) for item in ledger(project)["entries"] if item.get("record_type") == "approval_invalidated"}


def active_approval(project: Path, scope: str, phase: str, milestone: str | None = None) -> dict[str, Any] | None:
    invalidated = invalidated_approval_ids(project)
    for item in reversed(ledger(project)["entries"]):
        if item.get("record_type") != "approval" or item.get("approval_id") in invalidated:
            continue
        if item.get("scope_type") == scope and item.get("phase_id") == phase and item.get("small_milestone_id") == milestone:
            return item
    return None

def parse_artifacts(project: Path, raw: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for item in raw:
        if "=" not in item:
            raise ValueError("--artifact 格式必須是 TYPE=相對路徑")
        kind, value = item.split("=", 1)
        path = (project / value).resolve()
        if not path.is_file() or project not in path.parents:
            raise ValueError(f"artifact 不存在或超出專案：{value}")
        items.append({"type": kind.upper(), "path": rel(project, path), "sha256": file_sha(path), "semantic_sha256": semantic_sha(path)})
    if not items:
        raise ValueError("核准必須至少列出一個 --artifact")
    return items


def approve(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    if args.auto or args.signature != "/approve":
        raise ValueError("拒絕自動或模糊核准；signature 必須完全等於 /approve")
    if args.scope not in APPROVAL_SCOPES:
        raise ValueError(f"不支援的 scope_type：{args.scope}")
    artifacts = parse_artifacts(project, args.artifact)
    if args.scope == "phase0_5w_alignment" and args.phase != "0":
        raise ValueError("phase0_5w_alignment 僅適用於 Phase 0")
    if args.scope == "external_service_cost" and args.approver != "CEO":
        raise ValueError("外部付費服務必須由 CEO 明確核准")
    entry = {"record_type": "approval", "approval_id": f"APR-{uuid.uuid4().hex[:12]}",
             "scope_type": args.scope, "phase_id": args.phase, "big_milestone_id": args.big_milestone,
             "small_milestone_id": args.small_milestone, "artifacts": artifacts, "approver": args.approver,
             "approved_at": now(), "status": "ACTIVE", "invalidation_reason": None,
             "corresponding_gate": args.gate, "reason": args.reason}
    data = ledger(project); data["entries"].append(entry); dump(ledger_path(project), data)
    state = get_state(project); state["approvals"].append(entry["approval_id"])
    if args.scope == "phase0_5w_alignment":
        state["phase0_5w_status"] = "APPROVED"; state["phase0_5w_approval_id"] = entry["approval_id"]
        state["architect_dispatch_status"] = "READY"
    if args.scope == "phase0_exit": state["phase0_exit_status"] = "APPROVED"
    save_state(project, state); event(project, "approval_created", entry)
    print(json.dumps(entry, ensure_ascii=False, indent=2)); return 0


def refresh(args: argparse.Namespace) -> int:
    project = root(args.project_dir); data = ledger(project); stale: list[str] = []
    for item in data["entries"]:
        if item.get("record_type") != "approval" or item.get("status") != "ACTIVE": continue
        semantic_changed = False; layout_changed = False
        for artifact in item.get("artifacts", []):
            path = project / artifact["path"]
            if not path.exists(): semantic_changed = True; continue
            semantic_changed |= semantic_sha(path) != artifact.get("semantic_sha256")
            layout_changed |= file_sha(path) != artifact.get("sha256")
        if semantic_changed:
            stale.append(item["approval_id"])
            data["entries"].append({"record_type": "approval_invalidated", "approval_id": item["approval_id"], "invalidated_at": now(), "reason": "受核准產物發生語意變更或遺失"})
        elif layout_changed:
            data["entries"].append({"record_type": "change_classification", "approval_id": item["approval_id"], "classification": "NON_SEMANTIC", "recorded_at": now(), "reason": "僅偵測到格式或排版差異"})
    dump(ledger_path(project), data)
    state = get_state(project); state["stale_approvals"] = sorted(set(state["stale_approvals"] + stale))
    if stale and state.get("phase0_5w_approval_id") in stale:
        state["phase0_5w_status"] = "STALE"; state["architect_dispatch_status"] = "BLOCKED"; state["phase0_how_status"] = "STALE"; state["phase0_exit_status"] = "STALE"
    save_state(project, state); event(project, "approval_refresh", {"stale": stale})
    print(json.dumps({"stale": stale}, ensure_ascii=False)); return 0


def check_architect(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    refresh(argparse.Namespace(project_dir=str(project)))
    state = get_state(project)
    approval = active_approval(project, "phase0_5w_alignment", "0")
    if state.get("phase0_5w_status") != "APPROVED" or not approval_has_artifact(approval, "PM/Phase0_5W_Alignment.md"):
        print("[FAIL] 尚未取得綁定 PM/Phase0_5W_Alignment.md 的有效 PHASE0_5W_ALIGNMENT，禁止派遣 Architect。")
        return 1
    state["architect_dispatch_status"] = "DISPATCH_AUTHORIZED"
    save_state(project, state)
    event(project, "architect_dispatch_authorized", {"approval_id": state["phase0_5w_approval_id"]})
    print("[PASS] Architect 派遣已授權。")
    return 0

def set_dqa(args: argparse.Namespace) -> int:
    project = root(args.project_dir); state = get_state(project)
    if args.role not in ROLES or args.status not in {"PASS", "FAIL", "BLOCKED"}: raise ValueError("無效 DQA 角色或狀態")
    report = (project / args.report).resolve()
    if not report.is_file() or project not in report.parents: raise ValueError("DQA report 必須是專案內既有檔案")
    key = f"{args.phase}:{args.role}"; state["dqa_status"][key] = {"status": args.status, "report": rel(project, report), "report_sha256": file_sha(report), "context_sha256": project_context_sha(project), "updated_at": now()}
    save_state(project, state); event(project, "dqa_status", {"phase": args.phase, "role": args.role, "status": args.status, "report": rel(project, report)})
    print(f"[DQA] {key}={args.status}"); return 0


def validate_test_catalog(project: Path, phase: str, catalog_path: str) -> list[str]:
    path = (project / catalog_path).resolve()
    if not path.is_file() or project not in path.parents: return [f"找不到測試目錄：{catalog_path}"]
    data = load(path, None)
    cases = data.get("test_cases") if isinstance(data, dict) else None
    if not isinstance(cases, list): return ["測試目錄必須含 test_cases 陣列"]
    ids = [case.get("test_case_id") for case in cases if isinstance(case, dict)]
    if not all(isinstance(value, str) and value for value in ids) or len(set(ids)) != len(ids): return ["test_case_id 必須存在且唯一"]
    limit = {"3": 30, "4": 50}.get(phase)
    if limit is not None and len(ids) > limit:
        approval = active_approval(project, "phase_test_expansion", phase)
        if not approval: return [f"Phase {phase} 有 {len(ids)} 項測試，超過 {limit}；需要 PM phase_test_expansion 核准"]
        allowed = approval.get("reason", "")
        if str(len(ids)) not in allowed: return ["超限核准未明確記錄允許測試數量"]
    return []


def validate_te(args: argparse.Namespace) -> int:
    project = root(args.project_dir); data = load((project / args.batch).resolve(), None)
    required = {"batch_id", "test_case_ids", "environment", "commands", "started_at", "finished_at", "results", "stdout", "stderr", "evidence_paths", "blocked_items", "tool_requests", "security_observations"}
    if not isinstance(data, dict) or required - set(data): raise ValueError(f"TE batch 缺少欄位：{sorted(required - set(data or {}))}")
    for path in data.get("written_paths", []):
        normalized = Path(path).as_posix().lstrip("./")
        if normalized.startswith(("src/", "specs/", "TDD_DQA/tool/", "SDD_DQA/tool/")):
            raise ValueError(f"TE 不得寫入產品碼、規格或測試工具：{path}")
    state = get_state(project); state["te_batch_status"][data["batch_id"]] = {"status": args.status, "path": rel(project, project / args.batch), "updated_at": now()}; save_state(project, state)
    event(project, "te_batch", {"batch_id": data["batch_id"], "status": args.status}); print("[PASS] TE batch schema 有效"); return 0


def validate_milestones(args: argparse.Namespace) -> int:
    project = root(args.project_dir); path = project / args.file; data = load(path, None)
    errors: list[str] = []
    milestones = data.get("small_milestones") if isinstance(data, dict) else None
    if not isinstance(milestones, list) or not milestones: errors.append("small_milestones 必須是非空陣列")
    else:
        ids = [value.get("id") for value in milestones if isinstance(value, dict)]
        if len(ids) != len(set(ids)) or any(not isinstance(value, str) or not re.fullmatch(r"M\d+\.\d+", value) for value in ids): errors.append("小 Milestone ID 必須唯一且符合 M1.1")
        if len(milestones) > 5:
            if not all(value.get("parent_big_milestone") for value in milestones if isinstance(value, dict)): errors.append("超過 5 個小 Milestone 必須設定 parent_big_milestone")
    if errors: print("[FAIL] " + "；".join(errors)); return 1
    print("[PASS] Milestone 階層有效"); return 0


def approval_has_artifact(approval: dict[str, Any] | None, required_path: str) -> bool:
    return bool(approval and any(item.get("path") == required_path for item in approval.get("artifacts", [])))


def dqa_errors(project: Path, state: dict[str, Any], phase: str, roles: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    current = project_context_sha(project)
    for role in roles:
        record = state["dqa_status"].get(f"{phase}:{role}", {})
        if record.get("status") != "PASS":
            errors.append(f"Phase {phase} {role} DQA 未 PASS")
            continue
        report_rel = record.get("report")
        report = (project / report_rel).resolve() if isinstance(report_rel, str) else None
        if report is None or not report.is_file() or project not in report.parents:
            errors.append(f"Phase {phase} {role} DQA report 不存在或越界")
        elif file_sha(report) != record.get("report_sha256"):
            errors.append(f"Phase {phase} {role} DQA report 指紋已變更")
        else:
            report_data = load(report, None)
            required = {"role", "phase", "verdict", "evidence_paths"}
            if not isinstance(report_data, dict) or required - set(report_data) or report_data.get("role") != role or str(report_data.get("phase")) != phase or report_data.get("verdict") != "PASS" or not isinstance(report_data.get("evidence_paths"), list):
                errors.append(f"Phase {phase} {role} DQA report Schema 或 PASS 證據無效")
        if record.get("context_sha256") != current:
            errors.append(f"Phase {phase} {role} DQA 結論已與目前內容指紋不一致")
    return errors


def gate(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    refresh(argparse.Namespace(project_dir=str(project)))
    state = get_state(project)
    errors: list[str] = []
    if args.auto or args.signature != "/approve":
        errors.append("禁止 --auto 或模糊 signature")
    if str(int(args.from_phase) + 1) != args.to_phase:
        errors.append("只允許相鄰 Phase 轉換")
    if state["phase_lock"] != args.from_phase:
        errors.append(f"Phase lock 為 {state['phase_lock']}")
    scope = "phase0_exit" if args.from_phase == "0" else "phase_exit"
    exit_approval = active_approval(project, scope, args.from_phase, args.small_milestone)
    if not exit_approval:
        errors.append(f"缺少有效 {scope} 核准")
    if args.from_phase == "0":
        alignment = active_approval(project, "phase0_5w_alignment", "0")
        required_5w = "PM/Phase0_5W_Alignment.md"
        required_how = "Architect/Phase0_How_Architecture_Draft.md"
        if not approval_has_artifact(alignment, required_5w):
            errors.append("5W 核准未綁定 PM/Phase0_5W_Alignment.md")
        if not approval_has_artifact(exit_approval, required_5w) or not approval_has_artifact(exit_approval, required_how):
            errors.append("Phase 0 Exit 核准必須同時綁定已核准 5W 與 How")
        for required in (project / required_5w, project / required_how):
            if not required.is_file():
                errors.append(f"缺少 Phase 0 產物：{required}")
        how = project / required_how
        if how.is_file() and "5W-TRACE:" not in how.read_text(encoding="utf-8-sig"):
            errors.append("Phase 0 How 缺少每項決策的 5W-TRACE: 追溯記錄")
        errors += dqa_errors(project, state, "0", ("SDD", "TDD"))
        if not errors:
            state["phase0_how_status"] = "VERIFIED"
    if args.from_phase in TRIPLE_DQA_PHASES:
        errors += dqa_errors(project, state, args.from_phase, ("SDD", "TDD", "Claude"))
        errors += validate_test_catalog(project, args.from_phase, args.test_catalog)
        pending = [batch for batch, item in state["te_batch_status"].items() if item.get("status") != "PASS"]
        if pending:
            errors.append("尚有未通過 TE 批次：" + ", ".join(pending))
    if state.get("blockers"):
        errors.append("存在未處理 blockers")
    if errors:
        event(project, "gate_failed", {"from": args.from_phase, "to": args.to_phase, "errors": errors})
        print(json.dumps({"result": "FAIL", "missing": errors}, ensure_ascii=False, indent=2))
        return 1
    state["current_phase"] = args.to_phase
    state["phase_lock"] = args.to_phase
    state["next_action"] = next_action_for_phase(args.to_phase)
    save_state(project, state)
    event(project, "gate_passed", {"from": args.from_phase, "to": args.to_phase})
    print(json.dumps({"result": "PASS", "current_phase": args.to_phase}, ensure_ascii=False))
    return 0

def init_milestone(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    if not re.fullmatch(r"M\d+\.\d+", args.milestone): raise ValueError("Milestone ID 必須符合 M1.1")
    folder = project / "specs" / args.milestone
    if folder.exists() and any(folder.iterdir()): raise ValueError("Milestone 規格已存在，拒絕覆寫")
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("sdd_spec.md", "tdd_spec.md"):
        (folder / name).write_text(f"# {args.milestone} {name}\n\n<!-- 由 PM/DQA 填寫 -->\n", encoding="utf-8")
    dump(folder / "approval.json", {"milestone_id": args.milestone, "approvals": []})
    dump(folder / "injection_manifest.json", {"milestone_id": args.milestone, "injections": []})
    print(f"[PASS] 已建立隔離規格：{folder}"); return 0


def record_injection(args: argparse.Namespace) -> int:
    project = root(args.project_dir); folder = project / "specs" / args.milestone; source = (project / args.source).resolve()
    target = folder / "injection_manifest.json"
    if not source.is_file() or not target.is_file(): raise ValueError("來源或 milestone injection_manifest 不存在")
    data = load(target, {"milestone_id": args.milestone, "injections": []})
    data["injections"].append({"source": rel(project, source), "source_sha256": file_sha(source), "target_role": args.target_role, "injected_at": now(), "result": args.result, "encoding": "utf-8", "failure_reason": args.failure_reason})
    dump(target, data); print("[PASS] 已記錄 Context Injection"); return 0


def render_save_state(args: argparse.Namespace) -> int:
    project = root(args.project_dir); state = get_state(project)
    text = "\n".join(["# 專案 Save State", "", f"- 更新時間：{state['updated_at']}", f"- 目前 Phase：{state['current_phase']}", f"- Phase Lock：{state['phase_lock']}", f"- 大 Milestone：{state['current_big_milestone']}", f"- 小 Milestone：{state['current_small_milestone']}", f"- 下一步：{state['next_action']}", f"- Blockers：{', '.join(state['blockers']) or '無'}", f"- 權威狀態：{STATE_REL.as_posix()}", ""])
    path = project / SAVE_STATE_REL; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
    print(f"[PASS] 已產生 {rel(project, path)}"); return 0


def detect_python(args: argparse.Namespace) -> int:
    candidates = [sys.executable, shutil.which("python"), shutil.which("python3"), shutil.which("py")]
    rows = []
    for candidate in dict.fromkeys(str(item) for item in candidates if item):
        try:
            run = subprocess.run([candidate, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=10)
            rows.append({"path": candidate, "returncode": run.returncode, "version": (run.stdout or run.stderr).strip()})
        except OSError as exc: rows.append({"path": candidate, "error": str(exc)})
    print(json.dumps({"platform": platform.platform(), "interpreters": rows}, ensure_ascii=False, indent=2)); return 0 if rows else 1


def initialize(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    if state_path(project).exists() or ledger_path(project).exists():
        raise ValueError("治理狀態或 Ledger 已存在；拒絕 init 覆寫歷史。請使用 migrate 或建立新的隔離專案。")
    save_state(project, default_state())
    dump(ledger_path(project), {"schema_version": 1, "entries": []})
    event(project, "governance_initialized", {"project_dir": str(project)})
    print("[PASS] 已初始化治理狀態")
    return 0


def legacy_phase(project: Path) -> str | None:
    legacy = project / ".agents/.current_phase.lock"
    if not legacy.exists():
        return None
    phase = legacy.read_text(encoding="utf-8-sig").strip()
    if phase not in VALID_PHASES:
        raise ValueError(f"舊版 Phase lock 必須是 0～6：{phase}")
    return phase


def has_recovery_history(project: Path) -> bool:
    return any(path.exists() for path in (ledger_path(project), project / LOG_REL, project / SAVE_STATE_REL))


def apply_legacy_migration(project: Path, phase: str) -> None:
    if state_path(project).exists():
        raise ValueError("拒絕覆寫既有 state")
    state = state_for_phase(phase)
    save_state(project, state)
    dump(ledger_path(project), {"schema_version": 1, "entries": []})
    event(project, "governance_migrated", {"legacy_phase": phase})


def migrate(args: argparse.Namespace) -> int:
    project = root(args.project_dir); findings = []
    legacy = project / ".agents/.current_phase.lock"
    phase = legacy_phase(project)
    if phase is not None: findings.append({"legacy": rel(project, legacy), "value": phase})
    report = project / "Logs/migration_report.json"; dump(report, {"generated_at": now(), "findings": findings, "apply_requested": args.apply})
    if args.apply:
        if not findings: raise ValueError("拒絕在無明確舊資料時套用 migration")
        apply_legacy_migration(project, phase)
    print(f"[PASS] migration report：{rel(project, report)}"); return 0


def resume(args: argparse.Namespace) -> int:
    project = root(args.project_dir)
    if state_path(project).exists():
        state = get_state(project)
        validate_resumable_state(state)
        source = "project_state"
    else:
        phase = legacy_phase(project)
        if phase is not None:
            apply_legacy_migration(project, phase)
            state = get_state(project)
            source = "legacy_phase_lock"
        elif has_recovery_history(project):
            raise ValueError("偵測到 Logs 或 PM 的既有歷史，但缺少權威 project_state.json；請人工恢復，系統不會猜測斷點")
        else:
            initialize(argparse.Namespace(project_dir=str(project)))
            state = get_state(project)
            source = "new_project"
    print(json.dumps({"result": "RESUMED", "source": source, "current_phase": state["current_phase"], "next_action": state["next_action"]}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Johnny Project Team 治理工具（fail-closed）")
    sub = parser.add_subparsers(dest="command", required=True)
    def add_project(command: argparse.ArgumentParser) -> None: command.add_argument("--project-dir", default=".")
    init = sub.add_parser("init"); add_project(init); init.set_defaults(func=initialize)
    command = sub.add_parser("approve"); add_project(command); command.add_argument("--scope", required=True); command.add_argument("--phase", required=True); command.add_argument("--big-milestone"); command.add_argument("--small-milestone"); command.add_argument("--artifact", action="append", default=[]); command.add_argument("--approver", required=True); command.add_argument("--gate", required=True); command.add_argument("--reason", default=""); command.add_argument("--signature", required=True); command.add_argument("--auto", action="store_true"); command.set_defaults(func=approve)
    command = sub.add_parser("refresh"); add_project(command); command.set_defaults(func=refresh)
    command = sub.add_parser("check-architect-dispatch"); add_project(command); command.set_defaults(func=check_architect)
    command = sub.add_parser("set-dqa"); add_project(command); command.add_argument("--phase", required=True); command.add_argument("--role", required=True); command.add_argument("--status", required=True); command.add_argument("--report", required=True); command.add_argument("--context-sha256", default="declared"); command.set_defaults(func=set_dqa)
    command = sub.add_parser("validate-te"); add_project(command); command.add_argument("--batch", required=True); command.add_argument("--status", choices=("PASS", "FAIL", "BLOCKED"), required=True); command.set_defaults(func=validate_te)
    command = sub.add_parser("validate-milestones"); add_project(command); command.add_argument("--file", default="PM/milestones.json"); command.set_defaults(func=validate_milestones)
    command = sub.add_parser("gate"); add_project(command); command.add_argument("--from-phase", required=True); command.add_argument("--to-phase", required=True); command.add_argument("--signature", required=True); command.add_argument("--small-milestone"); command.add_argument("--test-catalog", default="TDD_DQA/test_catalog.json"); command.add_argument("--auto", action="store_true"); command.set_defaults(func=gate)
    command = sub.add_parser("init-milestone"); add_project(command); command.add_argument("--milestone", required=True); command.set_defaults(func=init_milestone)
    command = sub.add_parser("record-injection"); add_project(command); command.add_argument("--milestone", required=True); command.add_argument("--source", required=True); command.add_argument("--target-role", required=True); command.add_argument("--result", choices=("SUCCESS", "FAIL"), required=True); command.add_argument("--failure-reason"); command.set_defaults(func=record_injection)
    command = sub.add_parser("render-save-state"); add_project(command); command.set_defaults(func=render_save_state)
    command = sub.add_parser("detect-python"); command.set_defaults(func=detect_python)
    command = sub.add_parser("migrate"); add_project(command); command.add_argument("--apply", action="store_true"); command.set_defaults(func=migrate)
    command = sub.add_parser("resume"); add_project(command); command.set_defaults(func=resume)
    return parser


def main() -> int:
    try: return build_parser().parse_args().func(build_parser().parse_args())
    except (ValueError, OSError) as exc: print(f"[REJECTED] {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    sys.exit(main())
