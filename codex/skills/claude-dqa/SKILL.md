---
name: claude-dqa
description: 管理 Johnny Project Team 的 Claude DQA 外部唯讀審查。當使用者要求執行或檢查 Phase 3／4 的 Claude DQA、DQA 三重鎖定或最終閘門時使用。
---

# Claude DQA

Claude DQA 是外部、唯讀的獨立審查員，不得修改目標專案，也不會掛載 Git 或 Codex hooks。

## Phase 3

先由 TDD 與 SDD 將 `.agents/.dqa_status.json` 分別記為 `PASS`，再執行 `verify_all_dqa_passed_hook.py`。控制器會自動呼叫 Claude DQA；只有 Claude 真實回覆 `PASS` 才能解除三重 DQA 鎖定。

## Phase 4

SDD 初衷覆核與 TDD 回歸測試完成後，使用 `.agents/.phase4_dqa_status.json` 分別記錄 `PASS`。接著由 `phase_gate_hook.py --from_phase 4 --to_phase 5` 自動啟動 Claude DQA，三者皆 PASS 才能進入 CEO UAT 後的 Phase 5。

## 安全限制

- CLI 以 safe mode、plan permission、`Read`／`Glob`／`Grep` 唯讀工具執行。
- 每次審查預設上限為 900 秒與 2 美元；可透過閘門引數調整。
- CLI 不可用、逾時、非零結束碼或非預期格式，均視為 `FAIL`。
- 每次結果寫入目標專案的 `Claude DQA/`，並同步寫入對應 DQA 狀態檔。
