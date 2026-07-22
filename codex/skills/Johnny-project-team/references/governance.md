# 治理工具合約

以 `scripts/project_governance.py` 作為唯一的狀態、核准與 Gate 寫入入口。所有命令均以 UTF-8 工作、拒絕 `--auto`，且不安裝 Git hooks。

## 核准與失效

`approve` 必須提供 `/approve`、scope、Phase、核准者、Gate 與逐一列出的 `TYPE=path` artifact。Ledger 會保存 byte SHA-256 與格式正規化後的語意 SHA-256。`refresh` 將語意變更標為 `STALE`；只含空白、空行或 HTML 註解的變更只追加 `NON_SEMANTIC` 分類事件。

可用 scope：`phase0_5w_alignment`、`phase0_exit`、`phase_exit`、`milestone_spec`、`phase_test_expansion`、`security_spec`。Phase 核准與 Milestone 規格核准彼此獨立。

## Phase 0

0A 先建立 `PM/Phase0_5W_Alignment.md`，取得 `phase0_5w_alignment`。之後才可執行 `check-architect-dispatch`，並建立 `Architect/Phase0_How_Architecture_Draft.md`。0C 必須有 SDD、TDD 的 PASS 報告與獨立 `phase0_exit` 核准，才可 `gate --from-phase 0 --to-phase 1`。

任何 5W 語意變更都會使 5W、How 與 Phase 0 Exit 狀態變成 `STALE`；純排版不會失效。

## DQA 與測試目錄

Phase 3 與 Phase 4 必須依序完成 TDD DQA、SDD DQA、Claude DQA；前一項未 PASS 時，治理工具拒絕記錄下一項結論或執行 Claude DQA。Claude DQA 的 CLI 執行需要另行取得成本同意；未執行或不可用一律是 `BLOCKED`，不可當作 PASS。每位 DQA 必須自行執行其負責的測試、蒐集證據並在正式 DQA 報告中記錄結果；不得再建立或派遣測試執行代理。

`TDD_DQA/test_catalog.json` 的 `test_cases` 必須有唯一 `test_case_id`。Phase 3 合計上限 30、Phase 4 合計上限 50；超限不得刪減，PM 必須以列出允許數量的 `phase_test_expansion` 核准放行。測試重複只能以明確對應與去重理由處理。

## 狀態、Log 與 Migration

`.agents/project_state.json` 是唯一權威；`render-save-state` 產生 `Logs/Save_State.md`。`Logs/governance_events.jsonl` 為完整不可覆蓋事件歷史，包含時區、trace ID、Gate、DQA 與遮罩後的資料。`migrate` 預設只掃描，只有明確 `--apply` 才建立新檔案，且遇到不明確資料 fail-closed。

重新接手專案時執行 `resume --project-dir <project>`。若權威狀態存在且 Phase／Lock 有效，會保留既有斷點、Milestone、Blockers 與下一步；若僅有合法舊版 `.agents/.current_phase.lock`，會相容遷移並設定與 Phase 一致的下一步。完全沒有狀態、Logs 或 `PM/` 歷史時，才建立全新的 Phase 0 並從 5W 開始。若偵測到 Logs 或 `PM/` 歷史但權威狀態遺失，系統會拒絕猜測斷點，必須人工恢復。
