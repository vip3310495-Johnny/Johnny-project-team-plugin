# Johnny Project Team Plugin

此倉庫同時保留兩個獨立版本，請依使用環境選擇對應資料夾安裝。

## `antigravity/`

原始 Antigravity 版本的完整快照，保留其原本的 Plugin 結構與行為。

## `codex/`

Codex 版本（3.1.0），包含：

- Phase 0 Grill-me 引導 CEO 對齊 5W 與希望的設計風格。
- Approval Ledger、機器可讀狀態、Phase Gate 與 stale 偵測。
- Phase 3 起 SDD DQA、TDD DQA、Claude DQA 的三重審查流程。
- DQA → TE 批次測試契約、完整可遮罩 JSONL Log，以及 Windows／UTF-8 相容性。

### 安裝

以要使用的版本資料夾作為 Plugin 根目錄：

- Codex：[`codex/`](./codex/)
- Antigravity：[`antigravity/`](./antigravity/)

Codex 版本的詳細使用方式請見 [`codex/README.md`](./codex/README.md)。