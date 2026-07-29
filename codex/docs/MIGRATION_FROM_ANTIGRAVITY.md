# 從 Antigravity Edition 遷移到 Codex Edition

兩個 Edition 共用 Johnny Project Team 的產品理念，但 runtime contract
不同。請將遷移視為重新啟用工作流，不要直接複製 Hook 或 Agent 設定。

## 不可直接搬移

| Antigravity | Codex |
|---|---|
| 根目錄 `plugin.json` | `.codex-plugin/plugin.json` |
| `agents/*.json` | `.codex/agents/*.toml` |
| Antigravity hooks | Codex lifecycle hooks + `.johnny/git-hooks` |
| 舊 DQA status | schema v2 tree-bound DQA status |
| Claude 預設 gate | Claude DQA 手動、預設非必要 |

## 建議遷移步驟

1. 在原專案建立可回復的 Git commit。
2. 安裝 Codex Edition，但不要覆寫 Antigravity Plugin 目錄。
3. 在新 branch 或乾淨 clone 中執行 Codex `enable`。
4. 將既有需求、架構與 Milestone 文件作為參考輸入。
5. 由 PM 重新產生 Scope Contract Matrix、stable Ticket IDs 與 Task
   Context Packs。
6. 從 Phase 2 gate 選擇 `SUPERVISED` 或 `AUTONOMOUS`。
7. 重新建立 DQA evidence；不要匯入舊版 PASS 狀態。

## 可以保留

- PRD、架構決策、驗收條件與使用者可觀察結果。
- Git commit history。
- 已驗證的測試指令與測試資產，但必須重新綁定目前 tree。
- Lessons Learned 內容；先去重並轉為 Codex 的結構化 entries。

## 回滾

Codex Edition 使用 repository-local hooks path。執行
`johnny_project_hooks.py disable` 可還原啟用前的 hooks path，且保留
`.johnny` evidence 供稽核。
