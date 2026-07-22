"""管理 DQA 狀態，並以專案內容指紋讓過期的審查結果失效。"""

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


DEFAULT_STATUS_FILE = ".agents/.dqa_status.json"
VALID_ROLES = ("TDD", "SDD", "Claude")
VALID_STATUSES = ("PASS", "FAIL")
STALE = "STALE"
HARD_MAX_CLAUDE_ATTEMPTS = 2
_META = "_meta"
_CLAUDE = "_claude"
_IGNORED_DIRECTORIES = {".git", ".agents", "Claude DQA", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}


class StatusFileError(ValueError):
    """DQA 狀態檔存在但不是預期的 JSON 物件。"""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def resolve_status_path(project_dir: str, status_file: str = DEFAULT_STATUS_FILE) -> Path:
    path = Path(status_file)
    return path if path.is_absolute() else Path(project_dir).resolve() / path


def project_fingerprint(project_dir: str) -> str:
    """雜湊可審查的專案內容；排除狀態、報告與依賴快取避免自我失效。"""
    root = Path(project_dir).resolve()
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(root)
        if any(part in _IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if not path.is_file():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        try:
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as error:
            raise StatusFileError(f"無法讀取指紋檔案：{relative} ({error})") from error
        digest.update(b"\0")
    return digest.hexdigest()


def load_status(project_dir: str = ".", status_file: str = DEFAULT_STATUS_FILE) -> dict:
    path = resolve_status_path(project_dir, status_file)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise StatusFileError(f"DQA 狀態檔無法解析：{path}") from error
    if not isinstance(data, dict):
        raise StatusFileError(f"DQA 狀態檔必須是 JSON 物件：{path}")
    return data


def save_status(data: dict, project_dir: str = ".", status_file: str = DEFAULT_STATUS_FILE) -> Path:
    path = resolve_status_path(project_dir, status_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def refresh_context(project_dir: str = ".", status_file: str = DEFAULT_STATUS_FILE) -> tuple[dict, bool]:
    """若專案內容變更，將所有先前 PASS 標記為 STALE 並清除 Claude 重試額度。"""
    data = load_status(project_dir, status_file)
    if not data:
        return data, False
    fingerprint = project_fingerprint(project_dir)
    meta = data.get(_META)
    if isinstance(meta, dict) and meta.get("context_sha256") == fingerprint:
        return data, False
    for role in VALID_ROLES:
        if data.get(role) == "PASS":
            data[role] = STALE
    data[_META] = {"context_sha256": fingerprint, "updated_at": utc_now()}
    data.pop(_CLAUDE, None)
    save_status(data, project_dir, status_file)
    return data, True


def set_status(role: str, status: str, project_dir: str = ".", status_file: str = DEFAULT_STATUS_FILE) -> Path:
    if role not in VALID_ROLES:
        raise ValueError(f"不支援的 DQA 角色：{role}")
    if status not in VALID_STATUSES:
        raise ValueError(f"不支援的 DQA 狀態：{status}")
    data, _ = refresh_context(project_dir, status_file)
    data[role] = status
    data[_META] = {"context_sha256": project_fingerprint(project_dir), "updated_at": utc_now()}
    return save_status(data, project_dir, status_file)


def prepare_claude_attempt(project_dir: str, status_file: str, rerun: bool) -> None:
    """保留 Claude DQA 的有限重跑額度；FAIL 不會被一般 gate 自動重跑。"""
    data, stale = refresh_context(project_dir, status_file)
    if stale:
        raise StatusFileError("專案內容已變更，所有 DQA PASS 已標為 STALE；請重新執行 TDD 與 SDD DQA。")
    claude_status = data.get("Claude")
    if claude_status == "PASS":
        raise StatusFileError("Claude DQA 已通過，無須重跑。")
    if claude_status == "FAIL" and not rerun:
        raise StatusFileError("Claude DQA 上次失敗；修正後請明確加上 --rerun-claude 才能重跑。")
    attempt_data = data.get(_CLAUDE, {})
    attempts = attempt_data.get("attempts", 0) if isinstance(attempt_data, dict) else 0
    if claude_status == "FAIL" and attempts == 0:
        attempts = 1
    if attempts >= HARD_MAX_CLAUDE_ATTEMPTS:
        raise StatusFileError(f"Claude DQA 已達本內容指紋的固定重跑上限（{HARD_MAX_CLAUDE_ATTEMPTS} 次）。")
    data[_CLAUDE] = {"attempts": attempts + 1, "last_attempt_at": utc_now()}
    data[_META] = {"context_sha256": project_fingerprint(project_dir), "updated_at": utc_now()}
    save_status(data, project_dir, status_file)


def main() -> int:
    parser = argparse.ArgumentParser(description="管理 Phase 3 或 Phase 4 的 DQA 狀態。")
    parser.add_argument("--role", choices=VALID_ROLES, help="要更新的 DQA 角色")
    parser.add_argument("--status", choices=VALID_STATUSES, help="要寫入的狀態")
    parser.add_argument("--reset", action="store_true", help="清空 DQA 狀態")
    parser.add_argument("--project_dir", default=".", help="受審查專案目錄")
    parser.add_argument("--status_file", default=DEFAULT_STATUS_FILE, help="相對於專案的 DQA 狀態檔")
    args = parser.parse_args()
    try:
        if args.reset:
            path = save_status({}, args.project_dir, args.status_file)
            print(f"[SUCCESS] 已重設 DQA 狀態：{path}")
            return 0
        if not args.role or not args.status:
            parser.error("必須同時提供 --role 與 --status，或使用 --reset。")
        path = set_status(args.role, args.status, args.project_dir, args.status_file)
        print(f"[DQA] {args.role}={args.status}；狀態檔：{path}")
        return 0 if args.status == "PASS" else 1
    except (StatusFileError, ValueError) as error:
        print(f"[REJECTED] {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
