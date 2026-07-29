# Phase 1: 總體架構設計 (Global Architecture & Rule Auto-Injection)

> **【定位與範圍】**：將 Phase 0 的全局 PRD 交付 Architect 進行架構約束設計與 ADRs 擬定，並在簽核授權後進行全域基因規則自動注入。

---

## 1. 交付全局規格 (Global PRD Handoff)
- PM 在 Phase 1 開頭，將 Phase 0 的 `PM/PRD.md` (包含 **Intent 開發目的** 與 **Non-goals 非目標**) 完整交付給 **Architect (架構師)**。

## 2. 總體架構設計 (System Architecture & ADRs)
- PM 喚醒 **Architect (架構師)** 設計全局架構 (System Architecture)。
- **Architect Prompt Guard (架構約束與防過度設計守護)**：
  - **核心骨架對齊**：必須嚴格依據 PRD 確立核心元件與系統邊界，確保戰略方向不偏離。
  - **防過度設計 (Anti-Overengineering)**：**嚴禁制定死板、過度微觀的技術規格**。保持適度彈性與擴充空間，避免工程師在 Phase 3 因細微規格差異而被 DQA 硬性退件。
  - **🎯 Few-Shot 範例引導 (Architect Guidance Examples)**：
    - ❌ **BAD (過度設計反模式)**：「所有 API 強制使用 gRPC-Web 與 Protocol Buffers，狀態機硬性拆分 15 個微觀狀態，資料存取強制 4 層 Repository 抽象介面，每步寫入分佈式鎖。」➔ *極易導致 Phase 3 工程師與 DQA 陷入微觀規格卡死與無謂退件。*
    - ✅ **GOOD (合適架構推薦範例)**：「採用標準 REST/JSON 介面，定義 Auth, Item, Order 三大模組高階邊界與資料流 (System Flow)；資料庫選用 PostgreSQL 並定義核心 ER 關係草案；內部介面實作細節與設計模式留給工程師彈性發揮。」➔ *精準抓牢戰略骨架，給予足夠實作彈性。*
- **產出物**：評估技術選型、撰寫 ADRs (Architecture Decision Records)、產出高階架構圖與系統流程圖 (System Flow Diagram)。

## 3. 全域基因注入與 CEO 簽核跳轉 (Rule Auto-Injection & Phase Gate)
1. **取得架構師綠燈 (Architect Approval) [CRITICAL]**：PM 必須先與 Architect 確認架構無誤，並明確取得 Architect 的「綠燈 (Green Light)」放行。若無 Architect 綠燈，PM **絕對禁止**向 CEO 提案。
2. PM 向 CEO 報告總體架構藍圖與潛在風險，並聲明已取得 Architect 放行。
3. **簽核授權**：請求 CEO 輸入 `/approve` 授權跳轉。
4. **Layer 2 Domain Rule Auto-Injection (技術棧雙軌規則動態生成) [CRITICAL]**：
   - 取得授權後，PM **必須主動執行腳本**，將 Architect 確立的技術棧規則精準拆解為 Layer 2 獨立檔案。
   - **完全與 Layer 1 (AGENTS.md) 分開**，保持 Layer 1 純淨獨立。
   - 執行命令 (帶入架構師確立的語言，如 python)：
     `python .agents/skills/Johnny-project-team/scripts/auto_load_rules_hook.py --tech_stack <對應語言>`
   - 腳本將會在 `.agents/rules/` 目錄中自動產出帶有 YAML Header 的雙軌規範：
     1. `.agents/rules/dev_rules.md` (寫 Code 專屬規範)
     2. `.agents/rules/review_rules.md` (Review/驗收專屬規範)
5. **執行跳轉**：PM 強制執行階段閘門腳本：
   `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 1 --to_phase 2 --ceo_signature "/approve"`
6. [GREEN LIGHT] 後正式進入 Phase 2。
