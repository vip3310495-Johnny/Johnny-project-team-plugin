---
name: team-constitution
description: "自動預載全局基因 (Global Constitution)。每當任何 Agent 被喚醒或執行任務時，必須首先且自動加載此技能以讀取組織鐵律。"
---

# Johnny-project-team-plugin 專屬全域基因 (Team Constitution)

本文件定義了所有隸屬於此 Plugin 的原生子代理人 (Subagents) 必須絕對服從的「底層架構鐵律」。
不論你是 Engineer, DQA, TE 還是 Architect，只要你誕生於此 Plugin 的生態系中，就必須遵守以下規範。

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
