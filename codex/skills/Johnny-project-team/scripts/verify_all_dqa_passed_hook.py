"""相容 DQA Gate：只驗證既有證據，絕不自動呼叫外部 Claude CLI。"""
import argparse
import sys
from pathlib import Path
from dqa_status_manager import DEFAULT_STATUS_FILE, StatusFileError, refresh_context

PHASE_STATUS_FILES = {"0": ".agents/.phase0_dqa_status.json", "1": ".agents/.phase1_dqa_status.json", "2": ".agents/.phase2_dqa_status.json", "3": DEFAULT_STATUS_FILE, "4": ".agents/.phase4_dqa_status.json", "5": ".agents/.phase5_dqa_status.json", "6": ".agents/.phase6_dqa_status.json"}

def main() -> int:
    parser = argparse.ArgumentParser(description="驗證既有 DQA 證據；不執行外部服務。")
    parser.add_argument("--project_dir", default=".")
    parser.add_argument("--phase", choices=tuple(PHASE_STATUS_FILES), default="3")
    parser.add_argument("--status_file", default=None)
    args, _unknown = parser.parse_known_args()
    try:
        status, stale = refresh_context(str(Path(args.project_dir).resolve()), args.status_file or PHASE_STATUS_FILES[args.phase])
    except StatusFileError as error:
        print(f"[REJECTED] {error}"); return 1
    required = ("SDD", "TDD") if args.phase in {"0", "1", "2"} else ("SDD", "TDD", "Claude")
    failed = [role for role in required if status.get(role) != "PASS"]
    if stale or failed:
        print(f"[BLOCKED] Phase {args.phase} 缺少有效 DQA 證據：{', '.join(failed) or '內容已變更'}。不會自動呼叫 Claude CLI；需另取得外部成本核准後明確執行。")
        return 1
    print(f"[PASSED] Phase {args.phase} 既有 DQA 證據已通過。"); return 0

if __name__ == "__main__":
    sys.exit(main())