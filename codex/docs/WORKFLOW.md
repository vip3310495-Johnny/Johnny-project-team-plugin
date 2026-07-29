# Codex Edition 工作流

## Phase 概覽

| Phase | 目的 | 主要 Gate |
|---|---|---|
| 0 | 釐清 intent、non-goals、observable outcomes | CEO 核准需求方向 |
| 1 | 建立架構框架與外部邊界 | CEO 核准架構 |
| 2 | Scope Contract、Ticket/Milestone、Context Pack | CEO 選擇 Phase 3 policy |
| 3 | 單一 Milestone 實作與 TDD→SDD DQA | Milestone approval |
| 4 | 全產品整合 TDD→SDD DQA | 獨立 Phase 4 evidence scope |
| 5 | 依實體系統產生 As-Built | Architect 驗證 |
| 6 | 回顧、知識整理與退場 | 不重寫 Phase 5 歷史 |

## Phase 3 執行政策

### SUPERVISED

每個 Milestone 通過 TDD 與 SDD DQA 後，PM 提交 Review Package 給 CEO。
只有 CEO 明確核准後，`johnny_milestone_gate.py` 才能記錄 approval。

### AUTONOMOUS

CEO 在 Phase 2 核准完整 construction package 時一併委派。每個 Milestone
通過全部必要 DQA 後，`johnny_milestone_gate.py` 以
`phase2-ceo-delegation` 記錄 approval，不偽造新的 CEO 訊息。

## DQA 退件

- FAIL 1–4：工程師依可重現證據修正後重新送審。
- SDD FAIL：開啟新的 review cycle，重新執行 TDD 與 SDD。
- Claude FAIL：產品 tree 未變時只重跑 Claude；產品變動則所有 PASS 失效。
- 同一 Milestone、同一 DQA 角色第 5 次 FAIL：
  - 寫入 append-only history；
  - 凍結該 Milestone；
  - 阻擋 verdict、commit 與 Milestone approval；
  - 提交 CEO 解決衝突。

CEO resolution 會開啟新 review cycle，並只重設造成 escalation 的 DQA
角色計數。它不會把 FAIL 直接改為 PASS。

## 證據完整性

DQA status schema v2 綁定：

- stable Milestone/Ticket ID；
- review cycle；
- product `subject_tree`；
- complete staged `commit_tree`；
- reviewer ID；
- evidence path 或 reference。

產品內容改變後，舊 tree 的 PASS 不得用於新的 commit。

## Branch 規則

- Phase 3：`codex/milestone-Mxx`
- 整合：由 PM 在 approval 後合併至 `feature/<release>`
- 禁止直接在 `feature/*` 或 `main` 開發、commit 或 push

Repository-local `pre-commit` 與 `pre-push` 負責實體驗證；Codex
`PreToolUse` Hook 提供快速的 protected-branch 阻擋。
