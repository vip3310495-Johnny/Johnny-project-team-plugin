# Phase 1：總體架構設計與規則路由

> 將 Phase 0 核准的 MVP PRD 交給 Architect，建立足以約束方向、但不壓死實作彈性的架構骨架。

## 1. PRD 交接

PM 將 `PM/PRD/PRD.md`、`PM/Planning/5W1H_Requirement_Digest.md`、`PM/Flows/User_Flow.md`、Non-goals、tolerances 與已知風險完整交給 `johnny_architect`。Architect 必須先確認缺漏與矛盾，不能自行補需求。

## 2. Architect 架構設計

Architect 應：

- 定義系統邊界、核心 module、外部 interface、資料／控制流及主要整合點。
- 評估技術選型、runtime、資料庫、部署與安全邊界。
- 針對重大且難以回復的選擇建立 ADR。
- 使用 `codebase-design` 的 module、interface、implementation、depth、seam、adapter、leverage、locality 語彙。
- 避免過度設計：不得把可由 Engineer 決定的類別布局、設計模式或微觀步驟誤列為 FIXED。

產出 `Architect/System_Architecture.md`、必要 ADR、高階架構圖與 System Flow。所有 acceptance constraint 必須可驗證。

## 3. Architect Green Light

PM 必須取得 Architect 對架構可行性、PRD 對齊與風險揭露的明確 Green Light，才可向 CEO 提案。未通過則回到 Architect／PM 修正文責文件，不得提前進入 Phase 2。

## 4. ECC 規則路由與 CEO gate

- PM 向 CEO 說明架構、替代方案、風險及 Architect 結論。
- CEO 核准後，使用 `johnny_rules_refresh.py --paths <planned-product-paths>` 建立 common、language、framework 的 ECC selection；規則仍保持獨立，不改寫 `AGENTS.md`。
- 使用 `johnny_phase_gate.py --to-phase 2 --approval "<CEO approval>"` 進入 Phase 2。
