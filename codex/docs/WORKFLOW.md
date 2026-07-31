# Codex Edition 工作流程

## Phase gates

| Transition | 必要 evidence |
|---|---|
| Phase 0 → 1 | intent、non-goals、observable outcomes、risks |
| Phase 2 → 3 | Scope Contract、Milestones、Task Context Packs、Model Matrix |
| Phase 4 → 5 | Integrated TDD/SDD PASS、FIXED tolerance、As-Built inputs |

使用 `johnny_phase_gate.py --evidence <json>`。Phase 2 → 3 另需
`--execution-policy SUPERVISED|AUTONOMOUS`。Evidence 範本位於
`assets/templates/phase0-evidence.json`、`phase2-evidence.json` 與
`phase4-evidence.json`。

## Phase 3 Milestone

1. PM 啟動一個 dependency-ready Ticket/Milestone。
2. Engineer 僅在 `src/` 實作；永久測試放在 `src/tests/`。依賴、migration、
   runtime config 與產品腳本也放在 `src/` 對應目錄。
3. Engineer 執行 `johnny_rules_refresh.py --paths ...`，讀取 selection 中所有
   ECC rules。
4. Engineer 完成可驗證 vertical slice。
5. TDD DQA 使用相同 selection hash 審查；需要時只能寫
   `TDD_DQA/tool/` 與 `TDD_DQA/` evidence。
6. TDD PASS 後，SDD DQA 使用相同 selection hash 審查；需要時只能寫
   `SDD_DQA/tool/` 與 `SDD_DQA/` evidence。
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

每個 vertical slice 由一連串「一個可觀察行為」的 Red → Green → Refactor cycle 組成。
Engineer 先以公開介面寫一個會失敗的永久測試，預期值必須來自 Ticket、PRD、Contract
Matrix 或已驗證範例；以最小產品程式碼讓它通過，僅在綠燈後重構。不得先批次寫完測試。
每一輪使用 `assets/templates/tdd-cycle-evidence.md` 保存 RED／GREEN／REFACTOR 證據。
TDD DQA 獨立檢查結果，不共同設計 Engineer 的測試或實作。

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
