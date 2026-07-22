# Phase 1: 總體架構設計 (Global Architecture & PRD)

本階段發生在 Phase 0 確立戰略後。PM 負責進行全局的 PRD 撰寫與整體架構定義。

## 1. 撰寫總體 PRD (Global PRD)
PM 必須產出 `PM/PRD.md`，並強制包含以下兩大 OpenSpec 精神區塊：
- **【強制】開發目的 (Intent / Development Purpose)**：清楚定義「我們為何做這件事 (Why we are doing this)」。這將作為 Phase 4 最終成品質量覆核的最高準則。
- **【強制】Non-goals (非目標)**：明確界定「這次絕對不做的範圍」，從源頭徹底根除需求蔓延 (Scope Creep)。
- 核心功能與使用者故事 (User Stories)。

## 2. 總體架構設計 (Global Architecture)
- PM 呼叫 Architect，請其根據 PRD 設計全局架構 (System Architecture)。
- 產出高階架構圖、主要資料庫草案與模組劃分。

## 3. CEO 簽核跳轉 (Phase Gate Execution)
- 產出全局規劃後，PM 向 CEO 報告總體規劃與潛在風險。
- **簽核要求**：PM 必須請 CEO 檢視計畫，並輸入 `/approve` 授權進入下一階段。
- **執行跳轉**：取得 CEO 的 `/approve` 指令後，PM 必須強制執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 1 --to_phase 2 --ceo_signature "/approve"`
- 腳本回傳 `[GREEN LIGHT]` 後，正式進入 **Phase 2 (Milestone Planning & DQA Gate)**。
