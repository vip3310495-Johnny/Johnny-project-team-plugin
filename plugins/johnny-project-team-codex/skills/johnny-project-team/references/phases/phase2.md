# Phase 2：Milestone 垂直切片與 DQA 開工前審查

> PM 將 PRD 與架構拆成可獨立展示、測試與合併的 tracer-bullet Milestone；DQA 只做開工前可測性與規格審查，不撰寫正式 verdict。

## 1. Milestone 拆解與開發準備

- 每個小 Milestone 與 Ticket 一對一並共用穩定 ID `Mxx`。
- 每片必須涵蓋適用的資料、業務邏輯、API 與 UI／互動，能形成可展示的端到端 outcome。
- 禁止按 DB、API、UI 等技術層水平拆分。
- 建立依賴圖、Contract Matrix mapping 及一頁版 `PM/Context/Mxx.md`。
- 盤點工具、帳號、權限、硬體、測試資料、skills、開發環境及外部依賴。
- 若需從 GitHub 尋找免費工具，先執行 GitHub 安全審核與相容性檢查，取得 CEO 同意後才安裝。

## 2. DQA Pre-View

- SDD DQA 審查每片是否對應完整 user journey、observable outcome、Non-goals 與 UI 驗收方式。
- TDD DQA 審查是否能用獨立 oracle 測試、是否有清楚 failure path、相容性與回歸基線。
- TDD DQA 為每片標出適用的 stress／load／soak 或 monkey／fuzz 韌性維度、資源上限與
  停止條件；同時具負載與互動風險時兩類都要規劃。
- 涉及實際硬體時，Context Pack 必須列出測試設備、韌體、安全 envelope、emergency
  stop、非 production backend、operator、setup／teardown 與前後狀態證據。
- 發現水平切片、空泛架構、不可測 outcome 或缺少依賴時必須 REJECT，PM 重新切割。
- 每個 requirement 分類為 `FIXED`、`CONTROLLED` 或 `DISCRETIONARY`。任何角色可提出一次有證據的 challenge，最終由 PM 決定。

## 3. 複雜專案群組化

複雜度依跨系統、硬體、安全、UI 及依賴判斷；達十個小 Milestone 或同等複雜度時，將三至五個相依 Ticket 組成大 Milestone。Grouping 只影響管理與 DQA continuity，不得合併或抹除原垂直切片。

## 4. Phase 3 execution policy

PM 取得 DQA Green Light 後，只提供兩種方案：

- `SUPERVISED`：每個 Milestone 完成 TDD → SDD PASS 後，仍須 CEO 明確核准，才能 controlled merge 與解鎖下一片。
- `AUTONOMOUS`：CEO 在 Phase 2 gate 一次授權；每片完成必要 DQA 後，PM 引用此授權 controlled merge 並繼續。不得偽造新的 CEO 核准。

兩種模式都不會降低品質門檻。FIXED 衝突、第五次同角色 FAIL、DQA escalation、範圍變更或高風險外部動作仍必須停止並提交 CEO。

## 5. 兩階段提報與 Phase gate

1. PM 先提交 Milestone／Ticket 藍圖、依賴圖、Contract Matrix、Context Packs、工具盤點與 DQA 結論。
2. 詢問 CEO 選擇 `SUPERVISED` 或 `AUTONOMOUS`，然後停止，不能同一則訊息偷渡 `/approve`。
3. CEO 選定後，PM 記錄 policy，再請求最終核准。
4. 建立 Phase 2 evidence，執行 `johnny_phase_gate.py --to-phase 3 --execution-policy SUPERVISED|AUTONOMOUS --approval "<CEO approval>" --evidence <phase2-evidence.json>`。
