# Phase 0：狀態恢復、5W1H 需求探索與 MVP PRD

> 本階段只由 PM 與 CEO 收斂需求；尚不讓 Architect、Engineer 或 DQA 介入設計與實作。

## 1. 狀態恢復與專案判定

- 先執行 `johnny_project_hooks.py status`，讀取 `.johnny/state.json`、`Logs/Save_State.md`、`PM/PRD/PRD.md` 與 `.agents/context-manifest.json`。
- 已啟用的既有專案以實際 state 為準，恢復 Model Matrix、Task Context、未結事項及目前 Phase；不得依聊天記憶猜測，也不得偽造跳關。
- 若 state 顯示剛由 Phase 5 回到 Phase 0，先讀取上一輪的 handover、As-Built、Lessons Learned 與 open items；它們是下一輪需求探索的輸入，不得覆寫或視為本輪已核准需求。
- 全新專案才執行 `johnny_new_project.py`，檢查標準 `src/` 骨架後建立乾淨 baseline commit，再執行 `johnny_project_hooks.py enable`。
- 不覆寫既有 `AGENTS.md`、`.gitignore` 或 repository hooks。

## 2. 知識繼承與團隊適配

- 讀取 `.agents/lessons_learned/DIGEST.md`（若存在）。
- 產出 `PM/Planning/Model_Recommendation_Matrix.md`，列出 PM、Architect、Engineer、TDD DQA、SDD DQA、TE 及選用角色的模型、可用性、reasoning、預算與時間。
- 推薦值只是初始建議；必須驗證模型實際可用並由 CEO 核准。

## 3. 三輪 5W1H 需求探索

使用 `5w1h-grill-me` 產出 `PM/Planning/5W1H_Requirement_Digest.md`：

- Why：Intent、商業動機與 Non-goals。
- Who：Personas、RBAC、利害關係人。
- Where：執行、部署與整合拓撲。
- What：核心功能、視覺方向、benchmark 與 observable outcomes。
- When：規模、時程、事件觸發與容忍值。
- How：技術限制、方案、依賴、風險及驗證方式。

至少進行三輪：探索、矛盾追問、摘要確認。不得把未確認的推測寫成需求。

## 4. 縮小範圍並找出 MVP

- 讀取 5W1H Digest，使用 `grilling` 技能挑戰必要性、依賴與非目標。
- 將本輪 MVP 與後續 Backlog 分開；每個 MVP outcome 必須可觀察、可驗證。

## 5. UI／UX 視覺探索（適用時）

- 與 CEO 討論操作流程，產出 `PM/Flows/User_Flow.md` 與低擬真 wireframe。
- 需要視覺方向時，使用 image generation 產出三個候選；CEO 選定後只保留核准方向。
- CEO 尚未核准使用者流程與視覺方向前，不得定稿 PRD。

## 6. MVP 全局 PRD

產出 `PM/PRD/PRD.md`，至少包含 Intent、Non-goals、personas、user journeys、observable outcomes、tolerances、feature matrix、風險、依賴、驗證方式與已核准 Model Matrix。不得在 PRD 中過度指定內部類別或函式布局。

## 7. CEO 核准與 Phase gate

PM 提交 PRD、5W1H Digest、User Flow／視覺方向（適用時）及 Model Matrix，要求 CEO 明確核准。建立 schema-valid Phase 0 evidence 後，使用 `johnny_phase_gate.py --to-phase 1 --approval "<CEO approval>" --evidence <phase0-evidence.json>`。未核准不得進入 Phase 1。
