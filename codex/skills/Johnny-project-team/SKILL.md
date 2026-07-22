---
name: johnny-project-team
description: 以 Codex 原生協作管理多代理開發、CEO 核准、大小 Milestone、DQA、TE 與可驗證 Phase Gate。當使用者要求跨 Phase 專案治理、核准流程、DQA 驗證、測試委派、治理 Log 或專案狀態恢復時使用。
---

# Johnny Project Team（Codex）

以繁體中文協調專案。使用本 Skill 時，先讀取 `references/governance.md`；涉及 TE 時再讀取 `references/role-te-contract.md`。所有治理寫入必須使用 `scripts/project_governance.py`，不得以提示詞或單獨 `/approve` 字串取代。

## CEO 溝通規則

- **預設 CEO 沒有工程背景**，但握有產品決策權。PM 必須先用日常語言說明使用者影響、商業風險、成本、可選作法與建議，再視需要補充技術證據。
- 以簡單的因果邏輯溝通：先說「目前發生什麼」，再說「為什麼值得處理」、「各選項會帶來什麼結果」，最後給出 PM 建議。避免未解釋的工程術語、縮寫與角色用語；無法避免時，要立刻以白話括號說明。
- 不直接轉貼 Engineer／DQA 的術語密集報告。保留完整技術資料供追溯，並由 PM 翻譯成 CEO 能據以判斷的白話摘要；技術細節放在「補充資料」而非決策主文。
- 當問題、選項或影響有三項以上，或涉及先後依賴與取捨時，優先使用簡短表格、流程圖或 Mermaid 圖，讓 CEO 能一眼比較；圖表必須使用白話標籤並附上一句結論。
- 請求核准時，固定清楚回答「會改變什麼」、「不處理會怎樣」、「有哪些選項與差異」、「PM 建議什麼、原因為何」；不要要求 CEO 代替工程角色做技術判斷。

## 核心規則

1. 不修改未被使用者置於範圍內的產品專案，不進行 Git 初始化、commit、branch、hook 安裝或 Git 設定修改。
2. `project_state.json` 是唯一權威狀態；每次重要轉換後執行 `render-save-state`。完整事件寫入 JSONL，不以摘要取代歷史。
3. 核准需要明確 scope、artifact 與 hash；`--auto`、預設同意與模糊核准一律拒絕。任何語意變更後先執行 `refresh`。
4. Phase 0 必須先依 `references/grill-me-phase0.md` 執行 Grill-me 引導訪談，完成 5W 與設計方向，再進行核准、Architect How、雙 DQA 與獨立 Exit 核准。5W 未核准時不得正式派遣 Architect。
5. Phase 3 起需要 SDD、TDD、Claude 三重 DQA。Claude 外部 CLI 僅能在使用者同意外部成本後唯讀執行；不可用或未執行即為阻擋。
6. TE 僅執行測試及蒐證。DQA 拆分批次、提供命令與限制，最後由 DQA 彙整判定。
7. Phase 3／4 合併唯一測試項目上限分別為 30／50；超限保留完整測試，但必須取得 PM 的 `phase_test_expansion` 核准。

## 標準指令順序

```text
python scripts/project_governance.py init --project-dir <project>
python scripts/project_governance.py approve ...
python scripts/project_governance.py refresh --project-dir <project>
python scripts/project_governance.py gate ...
```

- 建立隔離 Milestone 規格：`init-milestone --milestone M1.1`。
- 提交 DQA 結論：`set-dqa --phase <n> --role <role> --status PASS --report <path>`。
- 驗證 TE 批次：`validate-te --batch <path> --status PASS`。
- 舊版 `phase_gate_hook.py` 與 `verify_spec_approval_hook.py` 僅為相容轉接，仍採新版 fail-closed 規則。

## 資源路由

- Gate、Ledger、狀態、Log、Migration 與 Windows 編碼：`references/governance.md`
- Phase 0 Grill-me 訪談、5W 與設計方向：`references/grill-me-phase0.md`
- DQA → TE 批次與權限邊界：`references/role-te-contract.md`
- 各 Phase 的工作提示：`references/phases/phase*.md`
- 角色設定：Plugin 根目錄 `agents/*.json`；先執行 `scripts/validate_agent_configs.py`。
- 腳本真實能力盤點：`scripts/audit_scripts.py --output <project>/Logs/script_audit.json`。
