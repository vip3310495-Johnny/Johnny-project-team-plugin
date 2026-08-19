# Codex Edition 工作流程

## Phase gates

| Transition | 必要 evidence |
|---|---|
| Phase 0 → 1 | intent、non-goals、observable outcomes、risks |
| Phase 2 → 3 | Scope Contract、Milestones、Task Context Packs、Model Matrix |
| Phase 3 → 4 | Phase 3 完成證據與 CEO 核准；進入後先停在 Phase 4 規劃段 |
| Phase 4 規劃 → 實作 | Architect 架構檢討、Phase 4 PRD、垂直切片、回歸基線與 CEO `/approve`；由 `johnny_phase4_start.py` 解鎖 |
| Phase 4 → 5 | 全部 P4 Milestone、Phase 3 回歸證據、Architect 詳細 As-Built 與 CEO 核准 |

使用 `johnny_phase_gate.py --evidence <json>`。Phase 2 → 3 另需
`--execution-policy SUPERVISED|AUTONOMOUS`。Evidence 請依 transition 使用
`assets/templates/phase0-evidence.json`、`phase2-evidence.json`、
`phase3-completion-evidence.json` 或 `phase4-evidence.json`。Phase 4 規劃完成後，
另用 `phase4-plan-evidence.json` 解鎖實作。

Phase 3 → 4 gate 會實體檢查核准計畫內所有 Milestone 已 merge、完整回歸證據存在、
沒有 active DQA escalation，且 evidence 的 `commit_tree` 等於目前 Git tree。Phase 4 → 5
則會再檢查核准與完成的 `P4-Mxx` 集合完全相同、所有切片已 merge，以及 As-Built
報告具備所有必要章節與 `- Verdict: VERIFIED`。Phase 4 每個 `P4-Mxx` 都採
ticket-scoped TDD → SDD DQA，禁止以舊式整機 `PHASE4-FINAL` 證據取代垂直切片驗證。

## Phase 3 Milestone

1. PM 啟動一個 dependency-ready Ticket/Milestone。
2. Engineer 僅在 `src/` 實作；永久測試放在 `src/tests/`。依賴、migration、
   runtime config 與產品腳本也放在 `src/` 對應目錄。
3. Engineer 執行 `johnny_rules_refresh.py --paths ...`，讀取 selection 中所有
   ECC rules。
4. Engineer 遵守 `references/tdd-integration.md` 完成可驗證 vertical slice，依
   `assets/templates/engineer-handoff.md` 在 `Engineer/` 寫入本 review cycle Handoff，
   記錄修改、測試、工具、非預期失敗與流程問題，完成 smoke test／最接近 probe 後，
   把報告路徑、commit 與 tree 交給 PM。填寫深度可參考
   `assets/examples/engineer-handoff-example.md`。
5. PM 驗證 Handoff 後，將同一 tree 路由給 TDD DQA；TDD DQA 使用相同 selection
   hash，依 `references/tdd-dqa-review.md` 審查並執行適用的有界壓力／猴子韌性測試，
   需要時只能寫
   `TDD_DQA/tool/` 與 `TDD_DQA/` evidence。
6. TDD PASS 後，SDD DQA 使用相同 selection hash 審查；需要時只能寫
   `SDD_DQA/tool/` 與 `SDD_DQA/` evidence。兩者皆遵守
   `references/dqa-test-environment.md`；受控實際硬體可以測試，無法安全隔離時必須
   `BLOCKED_ENVIRONMENT`。
7. TE 唯讀執行 DQA 工具，不建立或修改測試程式。
8. DQA PASS 後，只 stage `src/**`，再執行 `johnny_milestone_gate.py`。
9. PM 執行：

```powershell
python scripts/johnny_pm_merge.py --project <repo> `
  --ticket M01 --target feature/<release> --push
```

受控 merge 會核對 Milestone approval、來源 commit、DQA escalation、tracked
working tree 與 merge conflict。`--push` 只透過此受控命令略過一般
protected-branch pre-push，並把 merge／push 結果寫入 `.johnny/merge-status.json` 及
append-only merge history。

### Engineer TDD loop

Engineer 的 TDD 方法只以 `references/tdd-integration.md` 為準；每輪證據格式使用
`assets/templates/tdd-cycle-evidence.md`，完整交付摘要另使用
`assets/templates/engineer-handoff.md`，兩者不得互相取代。TDD DQA 獨立檢查結果，
不共同設計 Engineer 的測試或實作。

## DQA FAIL

- 第 1～4 次：返回 Engineer 修正，AUTONOMOUS 流程仍繼續。
- 第 5 次相同 Milestone、相同 role FAIL：只凍結該 Milestone 與相依鏈，
  必須由 CEO resolution 解鎖。
- SDD FAIL 開新 review cycle，重新要求 TDD → SDD。
- Product tree 改變會使既有 PASS 失效。

## ECC rule gate

Selector 以 active path 所屬最近 `package.json` 為 package boundary。混合
monorepo 中：

- `apps/mobile/App.tsx` → `common + typescript + react-native`
- `apps/web/App.tsx` → `common + typescript + react + web`

Selection schema v2 記錄 package roots、active paths、rule hashes 與
`selection_sha256`。Session、Subagent、Engineer、DQA 與 Claude 使用同一份
`.johnny/ecc-selection.json`。
