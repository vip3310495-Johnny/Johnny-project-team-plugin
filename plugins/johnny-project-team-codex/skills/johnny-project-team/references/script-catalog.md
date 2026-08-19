# 腳本目錄

呼叫隨附程式碼前，請先閱讀本目錄。腳本不會因舊檔名或舊文件稱它為 hook，就自動成為 hook。

## 生命週期 dispatcher

| 腳本 | 事件 | 用途與限制 |
|---|---|---|
| `hooks/johnny_session_context.py` | `SessionStart` | 讀取啟用狀態、Phase、context manifest、專案規則及適用的 ECC rule 路由，回傳精簡的 developer context。不得寫入檔案或推測缺少的核准。 |
| `hooks/johnny_subagent_context.py` | `SubagentStart` | 將 subagent 路由至其角色、Task Context Pack 及相同的適用 ECC rule 檔案。不得複製完整專案歷史或推進狀態。 |
| `hooks/johnny_tool_guard.py` | `PreToolUse` | Phase 3 之後，在受保護 branch 拒絕直接編輯及 Git commit／push。檢查必須快速且唯讀。 |

## Repository Git gate

| 腳本 | 用途 |
|---|---|
| `scripts/johnny_new_project.py` | PM 僅在確認為全新專案後執行。腳本拒絕非空目標，建立標準 `src/` 產品樹與被忽略的 PM／DQA／流程工作區，在 `main` 初始化 Git，並刻意不建立 baseline commit，留待人工檢查。 |
| `scripts/johnny_initialize.py` | 對已啟用 repository 重新執行可稽核初始化：migrate managed contracts、刷新 ECC selection，並以 JSON 回報 Phase、approval、routes 與 agents。不得用來略過 CEO gate。 |
| `scripts/johnny_project_hooks.py` | 執行 `enable`、`status`、`migrate` 或 `disable`。`migrate` 會升級受管理的 config 與 context route，但不會取代無關的專案選擇。 |
| `scripts/johnny_guard.py` | 僅由產生的 `pre-commit` 與 `pre-push` 呼叫。驗證 branch、staged paths、DQA schema、產品 `subject_tree`、完整 `commit_tree` 與必要 verdict。Phase 3／4 construction 會拒絕 `src/` 外的所有 staged path；不得把它當 reviewer 手動呼叫。 |

## 會變更狀態的命令

| 腳本 | 用途 |
|---|---|
| `scripts/johnny_phase_gate.py` | 明確核准後只推進一個 Phase。轉入 Phase 1、3、4、5 時必須提供結構化 `--evidence`；Phase 2→3 另須 `--execution-policy`。唯一例外是 Phase 5 完成後取得 CEO approval 的 `5→0` restart transition，它保留 audit history，並清除本輪 execution policy、Phase 4 execution 與 prerequisite evidence。Phase 3→4 會實際驗證每個已核准 Milestone merge、回歸證據、目前 Git tree，並確認沒有進行中的 escalation，之後只開放 Phase 4 規劃。Phase 4→5 另會驗證精確的 P4 計畫／完成集合，以及完整且標為 VERIFIED 的 As-Built 報告。 |
| `scripts/johnny_phase4_start.py` | 已在 Phase 4 時，驗證 Architect review 與 Phase 4 PRD 證據、記錄 CEO 明確核准，並解鎖實作；不會變更 Phase。 |
| `scripts/johnny_dispatch_gate.py` | PM 派工前，驗證目標角色 TOML、Milestone PRD、流程圖、資料流圖及 Context Pack，並建立 ticket／角色綁定的 dispatch authorization。SUPERVISED 必須提供 `/approve`；AUTONOMOUS 只略過此核准文字。 |
| `scripts/johnny_phase_prerequisites.py` | 僅供 import 的 validator，用於 Phase 0、Phase 2 Model Matrix、Phase 4 架構計畫與 Phase 4 完工證據。不得直接執行。 |
| `scripts/johnny_dqa_record.py` | `verdict` 是 TDD、SDD 或 Claude 判定的唯一入口；明確退件 cycle 使用 `reopen`；同一 Milestone 同角色第五次 FAIL 後使用 `resolve-escalation`。必須提供證據，並將每次狀態轉換附加至 `.johnny/dqa-history.jsonl`。 |
| `scripts/johnny_milestone_gate.py` | 在 Phase 3 或 Phase 4 中，於 DQA 後記錄一次綁定 tree 的 Milestone 核准。Phase 4 使用 `P4-Mxx`。SUPERVISED 模式必須提供 `--approval`；AUTONOMOUS 模式使用 Phase 2 的 CEO 委派。 |
| `scripts/johnny_pm_merge.py` | 通過 clean tree、approval、DQA、escalation、branch ID 與衝突檢查後，將一個已核准的 Phase 3 `codex/milestone-Mxx` 或 Phase 4 `codex/phase4-Mxx` 合併至 `feature/*` 或 `main`。發布至 origin 時必須明確使用 `--push`。 |
| `scripts/claude_dqa.py` | TDD 與 SDD PASS 後，手動執行真正的 Claude CLI。保存原始證據，並透過 `johnny_dqa_record.py` 提交結果；絕不得從 hook 執行。 |
| `scripts/johnny_rules_refresh.py` | 使用 `--paths <active-product-paths>` 執行，寫入共享的 `.johnny/ecc-selection.json` hash 與 `.agents/session-context.json`。Engineer 與所有 reviewer 使用同一份 selection。 |
| `scripts/johnny_lesson_record.py` | 以原子方式驗證並儲存一則結構化 lesson，以及僅附加的歷史紀錄。用它取代分離的先驗證再寫入流程。 |
| `scripts/log_aggregator.py` | 明確將已審查的 Log Agent artifact 附加至 `Logs/Master_Log.md`。不得將 timestamp 視為工作流完成的證明。 |
| `scripts/run_log_agent.py` | 使用 `--input <reviewed-artifact.md>` 明確彙整 `references/log-agent.md` 所述、範圍受限且已審查的 Log Agent evidence；不得自行產生綠燈，也不得掛接到 lifecycle 或 Git hook。 |

## 唯讀 validator 與決策輔助工具

| 腳本 | 用途 |
|---|---|
| `scripts/johnny_ecc_rules.py` | 偵測 repository 技術棧、維持 `common` 為必選、將每個 ECC 檔案 frontmatter 的 `paths:` 套用至 active product paths，並以 JSON、路徑或 hook context 輸出精確的 rule route。Engineer 實作前及每次 code DQA review 前都要執行；此腳本唯讀且不會核准程式碼。 |
| `scripts/dqa_test_limit.py` | 依 `.johnny/config.json` 的 Phase 上限計算 Markdown checklist 項目；失敗只代表規劃訊號，不是 DQA verdict。 |
| `scripts/pm_context_compressor.py` | 交接前檢查 Context Pack 或 Digest 大小；不會摘要內容或核准正確性。 |
| `scripts/te_dispatch_plan.py` | 計算上層 DQA 可使用、範圍受限的 TE 容量；不會建立 agent 或寫入狀態。 |
| `scripts/analysis_paralysis_breaker.py` | 僅供 PM 在決策卡住時按需使用的問題框架輔助工具；會輸出選項，但絕不代為選擇或記錄 CEO 核准。 |
| `scripts/socratic_challenger.py` | 僅供 PM 按需使用的可行性提問與範圍受限 repository 探索工具；成功結束不代表取得 Phase、DQA 或架構核准。 |
| `scripts/johnny_common.py` | 僅供 import 的 library，提供 Git、原子 JSON、僅附加 JSONL、file lock 與 tree hash 功能。絕不得直接執行。 |

## 封裝規則

只有本目錄列出且已實作的 runtime script 可以封裝。新腳本在發布前必須具備真實輸入驗證、
確定性的失敗條件、測試，以及正式的目錄項目；不發佈 placeholder。
