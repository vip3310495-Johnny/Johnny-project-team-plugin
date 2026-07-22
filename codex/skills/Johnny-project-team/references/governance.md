# 治理工具合約

以 `scripts/project_governance.py` 作為唯一的狀態、核准與 Gate 寫入入口。所有命令均以 UTF-8 工作、拒絕 `--auto`，且不安裝 Git hooks。

## 核准與失效

`approve` 必須提供 `/approve`、scope、Phase、核准者、Gate 與逐一列出的 `TYPE=path` artifact。Ledger 會保存 byte SHA-256 與格式正規化後的語意 SHA-256。`refresh` 將語意變更標為 `STALE`；只含空白、空行或 HTML 註解的變更只追加 `NON_SEMANTIC` 分類事件。

可用 scope：`phase0_5w_alignment`、`phase0_exit`、`phase_exit`、`milestone_spec`、`phase_test_expansion`、`security_spec`。Phase 核准與 Milestone 規格核准彼此獨立。

## Phase 0

0A 先建立 `PM/Phase0_5W_Alignment.md`，取得 `phase0_5w_alignment`。之後才可執行 `check-architect-dispatch`，並建立 `Architect/Phase0_How_Architecture_Draft.md`。0C 必須有 SDD、TDD 的 PASS 報告與獨立 `phase0_exit` 核准，才可 `gate --from-phase 0 --to-phase 1`。

任何 5W 語意變更都會使 5W、How 與 Phase 0 Exit 狀態變成 `STALE`；純排版不會失效。

## DQA、TE 與測試目錄

Phase 3 以後需要 SDD、TDD、Claude 三重 DQA PASS。Claude DQA 的 CLI 執行需要另行取得成本同意；未執行或不可用一律是 `BLOCKED`，不可當作 PASS。TE 以 `validate-te` 驗證批次 Schema，且任何 `written_paths` 指向 `src/`、`specs/` 或 DQA 工具目錄會失敗。

`TDD_DQA/test_catalog.json` 的 `test_cases` 必須有唯一 `test_case_id`。Phase 3 合計上限 30、Phase 4 合計上限 50；超限不得刪減，PM 必須以列出允許數量的 `phase_test_expansion` 核准放行。測試重複只能以明確對應與去重理由處理。

## 狀態、Log 與 Migration

`.agents/project_state.json` 是唯一權威；`render-save-state` 產生 `Logs/Save_State.md`。`Logs/governance_events.jsonl` 為完整不可覆蓋事件歷史，包含時區、trace ID、Gate、DQA 與遮罩後的資料。`migrate` 預設只掃描，只有明確 `--apply` 才建立新檔案，且遇到不明確資料 fail-closed。
