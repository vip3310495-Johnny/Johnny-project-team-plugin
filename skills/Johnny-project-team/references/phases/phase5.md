# Phase 5: 產品上線後維護與迭代 (Post-Delivery Maintenance & Iteration)

> **【定位與範圍】**：產品上線維護、組織記憶體運作與新功能迭代起手點。

---

## 1. 完工架構快照與 Hook 檢驗 (As-Built Architecture Snapshot & Change Log Alignment) [CRITICAL]
- **Architect Snapshot**：PM 強制喚醒 Architect 通盤掃描 `src/` 最終程式碼，撰寫 `Architect/As_Built_Architecture.md` 完工架構報告。
- **細部變更日誌比對與真實代碼優先原則 (Code Truth Precedence Rule)**：
  - Architect 必須讀取 PM 在 Phase 3 累積的各 Milestone 變更摘要 (`PM/Changes/M<N>_Change_Log.md`)。
  - Architect 比對 `src/` 實體程式碼內容與 PM 的變更日誌報告。
  - 若兩者內容相符，將工程師寫的細部改動納入 `Architect/As_Built_Architecture.md` 報告中。
  - **【真實代碼優先原則 (Code Truth Precedence Rule)】**：若 PM 變更日誌報告與實體程式碼不符，**必須強制以實體程式碼 (`src/`) 為最高準則 (Source of Truth) 寫入架構報告**！
- **Automated Verification Hook**：PM 必須執行 Hook 驗證報告完整性：
  `python .agents/skills/Johnny-project-team/scripts/verify_architecture_report_hook.py`
- 若檢驗失敗 (檔案缺失、字數不達標或缺目錄結構)，物理阻斷驗收並退回重寫。

## 2. 組織記憶體與架構諮詢 (Organizational Memory & Knowledge Service)
- **Single Source of Truth (單一事實來源)**：PM 充當系統活體知識庫。
- 當 CEO 進行架構決策追溯或 API 規範諮詢時，PM 第一時間檢索 `.agents/lessons_learned/DIGEST.md` 與 `Architect/As_Built_Architecture.md` 給予精準專業解答。

## 3. 迭代開發啟動與知識繼承 (Iterative Pipeline Trigger & Inheritance)
- **New Feature Pipeline**：當 CEO 提出新功能需求 (非單純 Bugfix) 時，PM 擬定新 PRD 並無縫發動全新 **Phase 1 (Global Architecture & PRD)** 進行迭代。
- **Knowledge Inheritance (知識零偏差繼承)**：喚醒新子代理人時，強制注入上一代 `.agents/lessons_learned/DIGEST.md`，防範歷史踩坑重演。
