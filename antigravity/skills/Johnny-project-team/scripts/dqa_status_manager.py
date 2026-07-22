import os
import sys
import json
import argparse

# Force UTF-8 encoding for stdout on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

STATUS_FILE = os.path.join(".agents", ".dqa_status.json")

def print_error(msg):
    print(f"🔴 [ERROR] {msg}")
    sys.exit(1)

def print_success(msg):
    print(f"🟢 [SUCCESS] {msg}")

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_status(data):
    # Ensure .agents dir exists
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Manage DQA Phase 3 Statuses.")
    parser.add_argument("--role", type=str, choices=["TDD", "SDD", "Claude"], help="The DQA role recording the status.")
    parser.add_argument("--status", type=str, choices=["PASS", "FAIL"], help="The status to record.")
    parser.add_argument("--reset", action="store_true", help="Reset all DQA statuses (usually at the start of Phase 3).")
    
    args = parser.parse_args()

    if args.reset:
        save_status({})
        print_success("已成功重置所有 DQA 狀態。")
        sys.exit(0)
    
    if not args.role or not args.status:
        print_error("必須提供 --role 與 --status 參數，或者使用 --reset 進行重置。")

    data = load_status()
    data[args.role] = args.status
    save_status(data)

    if args.status == "PASS":
        print_success(f"已記錄 {args.role} DQA 狀態為: PASS (綠燈)")
    else:
        print_error(f"已記錄 {args.role} DQA 狀態為: FAIL (紅燈退件)")

if __name__ == "__main__":
    main()
