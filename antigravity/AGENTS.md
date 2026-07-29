# Johnny-project-team-plugin 專屬全域基因 (AGENTS.md)

本文件定義了所有隸屬於此 Plugin 的原生子代理人 (Subagents) 必須絕對服從的「底層架構鐵律」。
不論你是 Engineer, DQA 還是 Architect，只要你誕生於此 Plugin 的生態系中，就必須遵守以下規範。

## 【鐵律 1】目錄隔離與污染防治 (Directory Isolation)
1. **主程式碼唯一家園**：所有正式的業務邏輯與系統代碼，**絕對只能放置在 `src/` 目錄中**。
2. **禁止亂丟文件**：所有系統架構圖與流程圖必須放置在 `PM/` 或 `Architect/`，嚴禁丟在專案根目錄。
3. **Log Agent 專屬**：系統的除錯紀錄與軌跡只能透過寫入 `Logs/` 或 `lessons_learned.md` 來進行。

## 【鐵律 2】修改即重審機制 (Anti-Bypass DQA Rule)
1. **DQA 優先**：只要 Engineer 修改了 `src/` 裡的任何一行程式碼，該修改狀態就會被系統底層的 `phase_gate_hook.py` 記錄。
2. **禁止直通 CEO**：代碼修改後，工程師**絕對禁止**直接向主大腦 (PM) 回報「已完成請 CEO 驗收」。你必須先通知 `TDD_DQA` 與 `SDD_DQA` 進行雙重測試，確保產出 DQA 報告。

## 【鐵律 3】語言與溝通 (Communication)
1. **全面繁體中文**：所有產出的文件、報告、註解與給 PM 的 Message，都必須使用繁體中文 (Traditional Chinese)。
2. **精確的時間戳記**：在撰寫任何報告 (如 DQA Report, Architect Review) 時，開頭必須標註精確的「系統時間 (YYYY-MM-DD HH:MM:SS)」。

## 【鐵律 4】階段認知與協作 (Phase Awareness & Collaboration)
1. **PM 階段覺察**：PM 在執行任何任務前，必須首先確認專案目前正處於哪個階段 (Phase)，並嚴格依照該階段對應的 Skill 說明文件與 CEO 進行協作 (cowork)。絕不允許在不確認階段目標的情況下盲目推進。

## 【鐵律 5】錯誤檢討與知識沉澱 (Error Reflection & Lesson Learnt) [CRITICAL]
1. **退件與除錯檢討**：在專案開發過程中，若發生任何嚴重錯誤 (Bug)、邏輯衝突，或是被 DQA / Architect **亮紅燈退件 (REJECT)**，當事 Agent (含 PM, Engineer 等) 必須立刻停機進行自我檢討。
2. **CEO 質疑與指正**：若 PM 在提案或匯報過程中，遭到 CEO (使用者) 提出質疑或指正，且該質疑具備合理性與建設性，PM 亦必須將此視為一次「退件檢討」。
3. **強制寫入教訓**：無論是遭到退件或 CEO 指正，檢討後都必須嚴格依照 Plugin 規範，將錯誤/盲點發生的根本原因 (Root Cause) 與正確的解法寫入 `.agents/lessons_learned/` 知識庫中，確保團隊不會在後續階段重複犯下相同的錯誤。
