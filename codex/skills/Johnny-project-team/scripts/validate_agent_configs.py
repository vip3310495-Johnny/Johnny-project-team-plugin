#!/usr/bin/env python3
"""驗證角色設定符合統一治理 Schema。"""
from __future__ import annotations
import argparse
import json
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass
from pathlib import Path

REQUIRED = {"role_id", "filename", "model", "reasoning_level", "available_tools", "write_permissions", "modifiable_paths", "prohibited_operations", "input_schema", "output_schema", "approvable_gates", "enforcement"}

def main() -> int:
    parser = argparse.ArgumentParser(description="驗證 agents/*.json。")
    parser.add_argument("--agents-dir", required=True)
    args = parser.parse_args()
    failures = []
    for path in sorted(Path(args.agents_dir).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path.name}: 無法解析 ({exc})"); continue
        missing = REQUIRED - set(data)
        if missing: failures.append(f"{path.name}: 缺少 {sorted(missing)}")
        elif data["filename"] != path.name: failures.append(f"{path.name}: filename 不一致")
    if failures:
        print("[FAIL] " + "；".join(failures)); return 1
    print("[PASS] Agent 設定均符合統一 Schema"); return 0

if __name__ == "__main__":
    sys.exit(main())

