# Johnny Project Team Plugin

此倉庫同時保留兩個獨立版本，請依使用環境選擇對應資料夾安裝。

## `antigravity/`

原始 Antigravity 版本的完整快照，保留其原本的 Plugin 結構與行為。

## `codex/`

Codex 版本（3.2.1），包含：

- Phase 0 Grill-me 引導 CEO 對齊 5W 與希望的設計風格。
- Approval Ledger、機器可讀狀態、Phase Gate 與 stale 偵測。
- Phase 3／4 固定依 TDD DQA、SDD DQA、Claude DQA 的順序進行三重審查。
- DQA 自行執行測試並完成判定、完整可遮罩 JSONL Log，以及 Windows／UTF-8 相容性。

### 安裝

以要使用的版本資料夾作為 Plugin 根目錄：

- Codex：[`codex/`](./codex/)
- Antigravity：[`antigravity/`](./antigravity/)

Codex 版本的詳細使用方式請見 [`codex/README.md`](./codex/README.md)。
