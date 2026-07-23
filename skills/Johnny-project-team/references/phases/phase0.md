# Phase 0: State Recovery, 5W1H Requirement Discovery & Global Strategy PRD

> **【定位與範圍】**：僅由 **PM 與 CEO** 進行戰略分析與需求收斂。暫不安插 Architect 或 DQA 介入。

---

## 1. 狀態恢復與新專案判定 (State Recovery Protocol)
- **存檔偵測**：檢查 `Logs/Save_State.md` 或 `PM/PRD.md`。
- **既有專案 (Resumed Project)**：
  - **Roster Recovery**：從 `PM/PRD.md` 恢復「模型矩陣 (LLM Team Roster)」。
  - **Rule Health Check**：確認 `.agents/AGENTS.md` 規則狀態。
  - **Critical Jump**：中斷 Step 2~8，直接跳轉至歷史存檔目標 Phase。
- **全新專案 (New Project)**：啟動 Git 與目錄初始化， proceed to Step 2。

## 2. 環境初始化 (Environment Bootstrapping)
1. **Git Init**：執行 `git init`。
2. **Scaffolding**：執行 `python .agents/scripts/workspace_init.py` 建立標準目錄架構。
3. **Toolkit Provisioning**：複製技能腳本至 `.agents/` 目錄。

## 3. 知識繼承與團隊適配 (Knowledge & Model Matrix)
1. **DIGEST 讀取**：載入 `.agents/lessons_learned/DIGEST.md` 吸收歷史經驗。
2. **Roster Matrix**：產生實體檔案 `PM/Model_Recommendation_Matrix.md` 設定團隊適配矩陣。

## 4. 5W1H 需求深度挖掘 (3-Pass 5W1H Requirement Discovery) [CRITICAL]
載入全域 **`5w1h-grill-me`** 技能，透過 3-Pass 協定收斂以下 6 大維度：
- **Why (Intent)**：商業動機與非目標邊界 (Non-goals)。
- **Who (Personas & RBAC)**：目標對象與角色權限矩陣。
- **Where (Topology)**：部署環境與執行拓撲 (GCP/AWS/Web/App)。
- **What (Aesthetics & Core Features)**：UI/UX 視覺導向、Must-have 核心功能與標竿對標 (Benchmark)。
- **When (Scale & Event Triggers)**：交付規模與 When-Action 事件觸發條件 (Event Triggers)。
- **How (Tech Stack & Proposals)**：技術選型與防通靈強勢單選提案 (Anti-Guessing Proposals)。

## 5. UI/UX 視覺探索 (Visual Direction Exploration)
- 利用 `generate_image` 產生 3 標的 UI 風格圖檔供 CEO 選定，選定後立刻銷毀剩餘 2 張。

## 6. 全局規格書擬定 (System Intent & Scope Specification)
撰寫 `PM/PRD.md` 全局規格書，必須強制包含：
1. **Intent (開發目的)**：驗收最高準則。
2. **Non-goals (非目標)**：劃定邊界，防止需求蔓延 (Scope Creep)。
3. **User Stories & Feature Matrix**：功能清單與使用者故事。
4. **LLM Team Roster**：團隊適配矩陣。

## 7. CEO 簽核與閘門跳轉 (CEO Approval & Phase Gate)
1. PM 呈交 `PM/PRD.md` 與 `PM/Model_Recommendation_Matrix.md`。
2. 要求簽核：「**若您同意上述計畫，請在對話框輸入 `/approve`。**」
3. 執行閘門：`python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 0 --to_phase 1 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
4. [GREEN LIGHT] 後正式進入 Phase 1。
