# Phase 2: Milestone 切割與 DQA 守門員審查 (Milestone Planning & DQA Gate)

> **【定位與範圍】**：由 PM 拆解小 Milestone，經 DQA 進行垂直切片審查 (Vertical Slicing)，並於複雜專案進行層級群組化 (Milestone Grouping)。

---

## 1. Milestone 拆解與規劃 (Milestone Decomposition)
- PM 根據 Phase 1 架構圖與 PRD，將總體範疇拆解為多個可獨立驗收的小 Milestone。

## 2. DQA 守門員審查 (Pre-View Audit & Vertical Slicing) [CRITICAL]
- PM 強制喚醒 `SDD_DQA` 與 `TDD_DQA` 進行 Pre-View 審查 (不寫具體測試代碼)。
- **Vertical Slicing Enforcement (垂直切片強制驗收 - to-tickets 鐵律)**：
  - **垂直切片 (Vertical Slice)**：每個 Milestone 必須包含「資料層 + 業務邏輯 + 端到端 UI/交互 (若適用)」，呈現獨立可運作、可展示的端到端完整功能 (例：M1 為「使用者登入與驗證」端到端通路，含 DB + API + 畫面)。
  - **水平切片反模式 (Horizontal Slice Anti-Pattern - 嚴禁)**：禁止按技術層級拆分 (例如 M1 只建 DB Schema、M2 只寫 API、M3 才做 UI)。
  - **DQA 退件權 (Veto Right)**：若發現水平切片或空泛架構，DQA **必須立刻亮紅燈退件 (REJECT)** 要求 PM 重新切割。
- **審查重點**：
  - **SDD_DQA**：獨立可展示之垂直功能切片與 User Journey。
  - **TDD_DQA**：獨立可測試性與解耦程度。

## 3. 衝突排解與 CEO 決策 (Conflict Resolution)
- 若 DQA 與 PM 發生意見分岐，PM 整理「選項與優缺點矩陣」呈報 CEO 進行單選決策。

## 4. 複雜專案層級群組化 (Composite Milestone Hierarchy)
- **發動時機**：在取得 DQA 審查同意後發動。
- **門檻判定**：若拆解出的小 Milestone 總數量 **>= 5 個**，PM 自動判定為「複雜專案 (Complex Project)」。
- **Grouping 機制**：PM 將 2~3 個主題相關的小 Milestone 歸類合成大 Milestone Group (例：Group M1 包含 `M1.1`, `M1.2`；Group M2 包含 `M2.1`, `M2.2`, `M2.3`)。
- **鐵律**：群組化僅為管理與呈報層級，**絕對不減少、抹平或改變原本小 Milestone 的實際數量與垂直切片範疇**。

## 5. 藍圖提交與 CEO 簽核跳轉 (Topology Diagram & Phase Gate)
1. PM 產出該階段 Milestone (或 Group) 的視覺化「流程圖 + 資料流向圖」。
2. 呈交 CEO 並請求授權：「**若您同意上述計畫，請在對話框輸入 `/approve`。**」
3. 執行跳轉：
   `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 2 --to_phase 3 --ceo_signature "/approve"`
4. [GREEN LIGHT] 後正式進入 Phase 3 (Dev & Acceptance Loop)。
