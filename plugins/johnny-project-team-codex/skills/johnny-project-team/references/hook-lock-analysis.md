# Hook 鎖定機制分析

## 原始實作的問題

1. 其他 host 的 `BeforeTool`／`AfterTool` 宣告不是 Codex plugin hook，因此無法在 Codex
   形成實體鎖。
2. Phase token 與狀態檔由不同腳本寫入，且未包含在同一個原子交易中。殘留 token 可能
   誤授權之後無關的寫入。
3. 全域環境繞過設定（`SKIP_PATH_GUARD`、`DQA_WRITE_SPECS`）沒有範圍限制，也無法稽核。
4. Phase 0 廣泛允許寫入，削弱了宣稱的實體鎖效果。
5. Claude DQA 過去只檢查 CLI 是否存在，未實際執行，卻仍將審查標記為 PASS。
6. 若 hook 呼叫 reviewer，或修改自己正在驗證的檔案，可能造成遞迴、死結，或留下只寫入
   一部分的狀態。
7. 覆寫根目錄的 `AGENTS.md`、`.gitignore` 或全域 hook 設定，可能影響未選擇啟用本流程
   的專案。

## Codex 設計

- 每個 repository 分別透過 `.johnny/enabled.json` 啟用。
- Git 使用 repository-local 的 `core.hooksPath=.johnny/git-hooks`。
- 停用時會還原先前保存的 repository-local hooks path。
- 既有專案 hook 會串接在 Johnny guard 之前，所以啟用 Johnny 時仍然有效；任一 hook
  都可以阻擋操作。
- pre-commit dispatcher 為唯讀，並採固定順序：啟用狀態 → 工作流狀態 → staged paths → DQA。
- 外部 reviewer 絕不在 hook 內執行。
- Phase 變更使用一個短生命週期的 OS lock 及原子化 `os.replace`。
- 執行 Git、Claude、測試或網路操作時，不得持有任何鎖。
- DQA 證據綁定 staged Git tree，避免使用過期核准。
- 不提供環境變數繞過機制。復原時使用明確且可稽核的 disable 命令，並保留狀態與證據。

## 仍存在的取捨

Git hooks 實際阻擋的是 commit，而非任意檔案寫入。Codex 目前沒有提供受支援的
plugin-level pre-write hook；若宣稱可以阻擋，將造成錯誤的安全保證。Phase gate 與
repository-local Git hook 共同保護工作流轉換及提交內容，同時不更動無關的 repository。

目前的 `PreToolUse` payload 也不會提供可靠的 Johnny agent role，因此無法在實體層級
區分 Engineer 寫入與 TDD／SDD DQA 寫入。角色 profile、Codex sandbox mode、DQA
workspace contract 與 Git gate 仍是分層控制措施，並不是能辨識角色的檔案系統 sandbox。
