# Phase 1: Milestone 執行拆解與微觀規劃 (Milestone Detailed Planning)

本階段發生在 Phase 0 確立全局架構，或是前一個 Milestone 剛執行完畢之時。
PM 必須將抽象的「全局目標」具體轉化為工程師與 DQA 能立刻動手的「微觀規格」。

## 1. 鎖定當前 Milestone
- PM 必須讀取 `PM/PRD.md` (全局 PRD)。
- 找出目前尚未完成的下一個 Milestone (例如：`Milestone 2: User Authentication`)。
- **邊界確認**：明確定義這個 Milestone 的範圍 (In-Scope) 與不做的部分 (Out-of-Scope)。

## 2. 撰寫 Milestone 專屬 PRD
- PM 針對這個選定的 Milestone，撰寫一份詳細的 `PM/Milestones/M<N>_PRD.md`。
- 內容必須包含：
  - 核心 User Stories。
  - 需要實作的 UI 畫面與互動邏輯 (精確描述)。
  - 需要串接的後端 API 或資料存取邏輯。
  - **【強制】驗收標準 (Acceptance Criteria) 與邊界條件**：PM 必須提供足夠詳盡的細節，確保後續 SDD DQA 有明確的依據可進行業務邏輯驗證。若細節不足，SDD DQA 有權在 Phase 2 將計畫書退回。

## 3. Architect 微觀架構設計 (Component Design)
- PM 必須呼叫 **Architect Agent**，針對 `PM/Milestones/M<N>_PRD.md` 進行微觀架構設計。
- Architect 必須輸出以下內容：
  - **資料結構 (Data Schema)**：定義關聯式資料庫的 Table 或是 NoSQL 的 Document 結構。
  - **API 規格約定 (API Contracts)**：定義前端與後端的 Request/Response JSON 格式。
  - **元件樹 (Component Tree)**：若是前端專案，定義要切解多少個 React/Vue Components。

## 4. 準備進入測試驅動規劃 (Transition to Phase 2)
- 當 PM 與 Architect 產出完整的微觀規劃後，PM **必須**在 `PM/Milestones/M<N>_PRD.md` 的最底部加上以下簽核區塊：
  ```markdown
  ## 授權狀態 (Authorization Status)
  - [ ] CEO 授權同意 (CEO Approved)
  - [ ] SDD DQA 授權同意 (SDD DQA Approved)
  ```
- **【狀態感知與主動提示】(State Awareness)**：
  - PM 在提交 `PM/Milestones/M<N>_PRD.md` 給 CEO 過目時，必須主動提示目前的系統狀態，例如：「目前系統預設為【手動簽核模式】。請問是否要啟用全自動模式？」
  - 若 CEO 先前使用了 `/goal` 但中途退出，PM 必須主動發問：「偵測到您剛退出 `/goal`，請問接下來的開發是否要切換回【手動簽核模式】？還是維持全自動？」
- **簽核與跳轉 (Phase Gate Execution)**：
  - PM 在展示完 Milestone PRD 後，必須主動向 CEO 說明：「請您確認本次 Milestone 開發計畫。若同意請輸入 `/approve`，我將帶領團隊進入 Phase 2 (DQA 規劃階段)。」
  - 取得 CEO 的 `/approve` 指令後，PM 代為將 CEO 的欄位打勾 `[x]` (全自動模式則無需打勾)。
  - PM 必須強制執行階段閘門腳本：
    `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 1 --to_phase 2 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
  - 腳本回傳 `[GREEN LIGHT]` 後，正式進入 **Phase 2 (DQA Planning & Boundary Handshake)**。
