# Codex Edition Changelog

本檔只記錄 `codex/`。Antigravity Edition 的歷史保留在 Repository 根目錄
`CHANGELOG.md`。

## 2.1.6-codex.1 — 2026-07-29

### Added

- OpenAI Codex Plugin manifest 與本機 Marketplace。
- `SessionStart`、`SubagentStart`、`PreToolUse` lifecycle hooks。
- Repository-local Git gates。
- Tree-bound DQA schema v2 與 append-only history。
- `SUPERVISED`／`AUTONOMOUS` Phase 3 execution policy。
- 同一 Milestone、同一 DQA 角色第五次退件的 CEO escalation。
- Tree-bound Milestone approval recorder。
- Script catalog、Task Context Pack 與 project rules。
- 122 份 ECC rule 文件與 22 個完整 ruleset。
- `johnny_ecc_rules.py` 技術棧辨識、`paths:` 路由及 JSON／path／hook context 輸出。
- Engineer、TDD DQA、SDD DQA 與 TE 的一致 ECC rule 載入契約。
- ECC ruleset 完整性、各技術偵測與 React Native 隔離測試。

### Changed

- Claude DQA 改為手動選用且預設不阻擋。
- SDD FAIL 會建立新 review cycle，重新要求 TDD 與 SDD。
- 未完成的概念腳本隔離至 `experimental/`。
- SessionStart、SubagentStart 與 `johnny_rules_refresh.py` 現在提供精確
  ECC rule routes。

### Validation

- 52 個整合與 rules routing 測試通過。
- 4 個 Skill validator 通過。
- Plugin validator 通過。
