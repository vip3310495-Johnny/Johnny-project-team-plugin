# Git 分支與衝突策略 (Git Strategy)

本團隊採用受保護的 Trunk-based / GitHub Flow 混合模式。

## 1. 主分支保護 (Protected `main`)
- `main` 分支受到嚴格保護，任何人 (包含 PM 與 Engineer) 絕對禁止直接 push 或 commit 代碼至 `main` 分支。
- 所有的開發都必須在 Feature 分支上進行。

## 2. 命名規範與分支建立
- **Milestone 分支**：每個 Milestone 會有一個共用的 Feature 分支，命名為 `feature/milestone-X`。
- **Engineer 個人分支**：Engineer 在動工前，必須從 `feature/milestone-X` 切換出自己的獨立分支，命名為 `eng/<role>-ms<number>` (例如：`eng/backend-ms3`)。
- **Commit 規範**：必須嚴格遵守 Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:` 等)。

## 3. 合併前同步 (Pre-Handoff Sync)
- Engineer 準備交接給 DQA 進行測試前，必須先執行 `git pull origin feature/milestone-X` (或進行 merge/rebase)，確保本地分支沒有落後於當前的 Milestone 進度。
- 這能有效防堵過期分支送審所導致的 Semantic Conflicts。

## 4. 衝突解決策略 (Conflict Resolution)
- 當 PM 準備將 Engineer 的程式碼 (通過 DQA 驗證後) 合併回 `feature/milestone-X` 或 `main` 時，若遭遇 Merge Conflict (合併衝突)：
  1. **【禁止強行覆蓋】**：PM 絕對禁止強行覆蓋代碼。
  2. **工程師解衝突**：PM 必須立即將任務退回給原 Engineer，並要求 Engineer 執行 Rebase 或手動解決衝突。
  3. **重新自測 (Re-test)**：Engineer 解決衝突後，必須在本地端重新跑過所有測試，確保亮綠燈，才能將解決衝突後的 Commit 交還給 PM。
