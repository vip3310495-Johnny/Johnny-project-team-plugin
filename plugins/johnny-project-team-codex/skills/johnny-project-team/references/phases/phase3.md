# Phase 3：實作與驗收雙迴圈

> 一次只執行一個 dependency-ready `Mxx`，以規格契約、Context Pack、RED → GREEN → REFACTOR、TDD DQA → SDD DQA 及 controlled merge 完成交付。

## 1. Milestone 微觀規格

PM 讀取 PRD、System Architecture／ADRs、Contract Matrix 與 `PM/Context/Mxx.md`，以 `assets/templates/milestone-prd.md` 建立 `PM/Milestones/Mxx_PRD.md`，並建立 `PM/Flows/Mxx_Flow.md` 與 `PM/DataFlows/Mxx_Data_Flow.md`。Milestone PRD 必須包含垂直 outcome、非目標、依賴、CEO 手動驗證步驟、回復方式與交付 checklist；其 `Acceptance Criteria` 每列必須具備驗收對象、操作步驟、預期結果、容忍值、證據／測試命令及負責 DQA。流程及資料流文件必須各含可讀圖示。穩定 ID 必須在所有文件與 evidence 一致。

PM 每次派出 Engineer、TDD DQA 或 SDD DQA 前，執行 `johnny_dispatch_gate.py --ticket Mxx --role <role>`；`SUPERVISED` 額外提供 `--approval /approve`。兩種 execution policy 都驗證角色 TOML 與 Milestone 文件，`AUTONOMOUS` 唯一略過的是明確 `/approve` 核准文字。

## 2. 開工前上下文與衝突檢查

- Engineer 必讀架構資料、Milestone PRD、Context Pack、TDD integration 及目前 ECC selection。
- 若 PRD、架構、Contract Matrix、DQA acceptance 或 Context Pack 互相衝突，Engineer 立即停止受影響工作並通知 PM。
- PM 協調相應 owner 先修正文責文件；無法決定時交 CEO。文件一致後才可重新開工。

## 3. Engineer TDD 實作

- 使用 `codex/milestone-Mxx`，只修改／stage／commit `src/**`。
- 全程遵守 `references/tdd-integration.md`；本 Phase 文件不重複定義 TDD 方法。
- 永久回歸測試放在 `src/tests/`；DQA 工具不得混入產品 commit。
- 提交可重跑的 build、lint、type、test、acceptance 命令與輸出摘要，並完成
  `references/tdd-integration.md` 規定的 smoke test 或最接近 probe。
- 依 `assets/templates/engineer-handoff.md` 在 `Engineer/` 建立本 review cycle 的
  Handoff 報告，標題使用 `<Wave>_<Milestone>_Engineer Hand off — Review Cycle <N>`，
  再把報告路徑、commit 與 tree 交給 PM。Engineer 不得直接派工 DQA。

## 4. DQA 驗收

1. PM 驗證 Engineer Handoff 完整且綁定目前 commit／tree 後，才派 TDD DQA 審查行為、
   邊界、failure paths、回歸、相容性、TDD evidence，以及適用的 stress／load／soak
   或 monkey／fuzz 韌性測試，並以 `assets/templates/tdd-dqa-review-report.md` 記錄
   tree-bound 結果。
2. 同一 tree 的 TDD PASS 後，SDD DQA 才依 PRD、Intent、Non-goals、tolerance、User Flow 與實際 UI／流程審查。
3. UI 先使用實際截圖；無法精準判定時才使用 OmniParser，timeout 只是操作建議，不得降低標準。
4. SDD FAIL 會開新 review cycle，產品變更會使舊 PASS 失效，必須重新 TDD → SDD。
5. 每個 DQA checklist 預設上限 30 項；超過須由 PM 記錄一次有理由的例外，不需 CEO，但不可刪減必要驗證。

兩個 DQA 都必須遵守 `references/dqa-test-environment.md`。受控實際硬體可以驗證；正式
運轉、與真實使用者共享、只能連 production 或無法安全復原時，回報
`BLOCKED_ENVIRONMENT` 且不得記錄 PASS／FAIL verdict。SDD 報告使用
`assets/templates/sdd-dqa-review-report.md`。

Claude DQA 與 Security DQA 都是 CEO 手動要求才加入，不屬於預設 gate。

## 5. 五次退件與 Scope 規則

- 同一 Milestone、同一 DQA role 的第 1～4 次 FAIL 返回 Engineer 修正。
- 第 5 次凍結該 Milestone 與相依鏈，必須由 CEO 明確解決 escalation。
- FIXED 問題立即交 PM；CONTROLLED 必須向 PM送 Change Notice；DISCRETIONARY 由 Engineer 判斷。

## 6. 提報、核准與 controlled merge

所有必要 DQA PASS 後，PM 準備 Review Package：實際變更、測試結果、DQA evidence、CEO 驗證步驟、已知限制與 rollback。

- `SUPERVISED`：CEO 明確核准後執行 `johnny_milestone_gate.py`。
- `AUTONOMOUS`：引用 Phase 2 delegation 執行 gate，不製造新核准。

只使用 `johnny_pm_merge.py` 合併至核准的 `feature/*` 或 `main`。PM 將實際變更摘要記入 `PM/Changes/Mxx_Change_Log.md`，供 Phase 4 架構檢討追溯。

## 7. Phase 3 完成

重複以上迴圈直到所有 Milestone 完成。PM 依
`assets/templates/phase3-completion-evidence.json` 建立 Phase 3 完工證據，至少記錄
核准的 Phase 2 計畫、完整回歸證據及目前 `commit_tree`。Gate 會實體檢查計畫內
所有 Milestone 已出現在 `.johnny/merge-history.jsonl`、回歸證據存在、沒有未解決的
DQA escalation，且 evidence 綁定目前 Git tree。取得 CEO 核准後執行：

```powershell
python scripts/johnny_phase_gate.py --project <repo> --to-phase 4 `
  --approval "<CEO approval>" --evidence <phase3-completion-evidence.json>
```

通過後進入 Phase 4 規劃段；此時尚未授權 Phase 4 修改產品程式。
