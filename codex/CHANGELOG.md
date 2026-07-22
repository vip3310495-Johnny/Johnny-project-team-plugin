# Changelog

本專案依循 [Keep a Changelog](https://keepachangelog.com/) 格式，並採用語意化版本。

## [Unreleased]

## [3.2.1] - 2026-07-23

### Changed

- Engineer 的程式碼異動範圍限於 `src/` 與 `tests/`，並明確禁止使用 DQA 工具、腳本、Gate 與 Claude DQA CLI；測試執行與品質判定交由 DQA 執行。

## [3.2.0] - 2026-07-23

### Changed

- Phase 3／4 的 DQA 改為強制依序執行 TDD → SDD → Claude，拒絕跳過前置 DQA 或提早執行 Claude。
- 移除 TE agent、TE 批次契約與 Gate 依賴；DQA 直接執行測試、蒐集證據並完成判定，以避免額外耗用 Codex 子代理槽位。

## [3.1.0] - 2026-07-22

### Added

- Codex 原生治理入口、單一專案狀態、append-only Approval Ledger 與 JSONL 完整 Log。
- Phase 0A Grill-me 5W 引導流程，新增 CEO 希望的設計風格、參考／排除案例與無障礙方向。
- Phase 0 5W 核准、Architect How、雙 DQA 與獨立 Exit 核准；How 使用 `5W-TRACE` 可追溯至 5W。
- 大小 Milestone、隔離規格目錄、Context Injection manifest、DQA → TE 批次契約與角色設定 Schema。
- Windows UTF-8／Unicode 與 Python interpreter 偵測，以及 18 項治理回歸測試。

### Changed

- `/approve` 改為需綁定 scope、artifact 路徑、SHA-256 與語意指紋；語意變更以 Ledger 失效事件記錄。
- Phase Gate 改為驗證必要 artifact、DQA report Schema、report hash、context hash、blocker 與 TE 狀態。
- Phase 3／4 合併測試項目上限定為 30／50；超限必須取得 PM `phase_test_expansion` 核准。
- 舊版相容 Hook 改為 fail-closed，不再使用自動核准或自動付費外部 DQA。

### Security

- Claude DQA 僅在有效 CEO `external_service_cost` Ledger 核准存在時可執行；無核准一律 `BLOCKED`。
- 完整 Log 新增結構化敏感資料遮罩、trace ID 與證據欄位。

## [3.0.0] - 2026-07-21

- 初版 Codex 相容多代理專案治理與 DQA 工作流程。
