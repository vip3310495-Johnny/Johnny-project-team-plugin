# DQA → TE 委派合約

TDD DQA 的預設 reasoning level 是 `High`。DQA 每一批必須提供 test case IDs、命令、工具、環境、預期結果與安全限制。TE 僅可執行測試、蒐集證據與索取缺少工具；不得修改產品程式碼、規格、測試工具或正式 DQA 報告，也不能核准 Gate。

TE 回傳 JSON 必須有：`batch_id`、`test_case_ids`、`environment`、`commands`、`started_at`、`finished_at`、`results`、`stdout`、`stderr`、`evidence_paths`、`blocked_items`、`tool_requests`、`security_observations`。所有批次完成後由 DQA 彙整並給出 PASS 或 FAIL。

此限制優先由工具驗證路徑；Codex 平台若未提供物理檔案系統隔離，角色設定僅是流程約束，不能宣稱為系統權限隔離。
