#!/usr/bin/env python3
"""稽核 Plugin 腳本是否明示為 placeholder、stub 或真實檢查。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

MARKERS = ("[AUTO-IMPLEMENTED]", "stub", "尚未實作", "預設通過", "skip")

def main() -> int:
    parser = argparse.ArgumentParser(description="輸出腳本能力盤點；不修改任何檔案。")
    parser.add_argument("--scripts-dir", default=Path(__file__).parent)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    directory = Path(args.scripts_dir).resolve()
    records = []
    for path in sorted(directory.glob("*.py")):
        if path.name == Path(__file__).name:
            records.append({"script": path.name, "classification": "requires_manual_capability_review", "evidence": [], "guarantee": "稽核器本身；需由測試與人工檢視驗證"})
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace").lower()
        markers = [marker for marker in MARKERS if marker.lower() in text]
        records.append({"script": path.name, "classification": "placeholder_or_stub" if markers else "requires_manual_capability_review", "evidence": markers, "guarantee": "僅依靜態標記分類；非安全隔離或完整掃描證明"})
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] 已輸出 {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

