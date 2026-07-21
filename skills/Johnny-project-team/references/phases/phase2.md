# Phase 2: Milestone 切割與 DQA 審查 (Milestone Planning & DQA Gate)

本階段的主要目的是由 PM 將總體架構切割成可獨立驗收的「小 Milestone」，並交由 DQA 進行合理性審查，確保每一塊都能被有效地開發與測試。

## 1. 進行小 Milestone 切割與規劃
- PM 根據 Phase 1 的總體 PRD 與架構圖，將工作切分為多個小 Milestone。
- 每個 Milestone 需要有初步的範疇描述。

## 2. 喚醒 DQA 進行「守門員審查」 (Pre-View)
- PM **強制喚醒** `SDD_DQA` 與 `TDD_DQA`。
- **注意**：在此階段，DQA **不需要**撰寫具體的測試代碼或詳細測試計畫 (那是在 Phase 3 做的事)。
- DQA 的任務是**審查 Milestone 的合理性**：
  - **SDD_DQA**：檢視這個 Milestone 是否太大步，導致畫面或流程難以分段 Review？是否具備可展示的產出？
  - **TDD_DQA**：檢視這個 Milestone 的產出是否具備可測試性？是否過度耦合？

## 3. 衝突排解與 CEO 決策
- **若發現問題**：DQA 會向 PM 提出修改建議。若 DQA 與 PM 的意見出現衝突，PM 必須整理出「選項與優缺點」，並向 CEO 報告請求決策。
- **若審查無誤**：DQA 同意 Milestone 切割。

## 4. 提交視覺化藍圖與 CEO 簽核跳轉
- DQA 審核通過後，PM 產出這個 Milestone 的**「流程圖 + 資料流向圖」**。
- PM 將此藍圖呈交給 CEO，並說明：「請您確認 Milestone 規劃。若同意請輸入 `/approve`。」
- 取得 CEO 的 `/approve` 指令後，PM 必須強制執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 2 --to_phase 3 --ceo_signature "/approve"`
- 腳本回傳 `[GREEN LIGHT]` 後，正式進入 **Phase 3 (Dev & Acceptance Loop)** 進行該 Milestone 的實作。
