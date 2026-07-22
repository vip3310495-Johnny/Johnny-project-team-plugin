# DQA Gate 安全規則

## Phase 0～6 轉換

- `phase_gate_hook.py` 僅接受相鄰轉換：`0→1→2→3→4→5→6`。
- 所有轉換皆拒絕 `--auto`，且必須提供完全等於 `/approve` 的 CEO 簽核。
- Phase 0～2 只驗證相鄰轉換、鎖定狀態與 CEO 簽核；Phase 3 與 Phase 4 必須依序完成 TDD、SDD、Claude 三重 DQA。
- `3→4` 另驗證 Milestone 視覺化報告；`5→6` 另驗證 As-Built Architecture Handover。Phase 6 是終態。

## Claude DQA

- Phase 3～5 的 TDD/SDD 皆為 `PASS` 時，gate 才會首次自動呼叫唯讀 Claude CLI；Phase 3 與 Phase 4 依 TDD → SDD → Claude 順序執行。
- Claude 只使用 `Read,Glob,Grep`、`--permission-mode plan`、固定預算與逾時限制。
- Claude FAIL 不會被一般 gate 自動重跑；修正後須明確加上 `--rerun-claude`，同一內容指紋固定最多兩次。
- 專案內容變更會將既有 PASS 標示為 `STALE`，必須重新完成內部 DQA。

## 狀態檔

- Phase 3：`.agents/.dqa_status.json`
- Phase 4：`.agents/.phase4_dqa_status.json`
- Phase 5：`.agents/.phase5_dqa_status.json`
- 報告：`Claude DQA/claude-dqa-<UTC timestamp>-<random>.json`
