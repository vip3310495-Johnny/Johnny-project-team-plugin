# Phase 4: 全局驗收與發布上線 (Final Intent Audit & Release Deployment)

> **【定位與範圍】**：全局成品質量覆核與發布點。專注於「雙 DQA 全產品系統測試與戰略意圖覆核 (Dual DQA Full-Product Audit)」、「UAT 實機盲測 (Dogfooding)」與「自動化發布部署 (Release Deployment)」。

---

## 1. 雙 DQA 全局覆核與全產品功能測試 (Dual DQA Full-Product System Testing)
- PM 強制喚醒 **`SDD_DQA`** 與 **`TDD_DQA`**，並導入 **Phase 2 審查後的 PRD (`PM/Phase2_Reviewed_PRD.md`)**。
- **客製化發布檢核腳本撰寫 (Custom Release Check Script)**：PM 必須在 Phase 4 開頭，負責撰寫一支專屬於該 Phase 4 的 Python 驗證腳本存至 `PM/Scripts/verify_Phase4.py`。該腳本必須能**物理檢查**以下項目的完成度（注意：Phase 4 不需要檢查流程圖與資料流向圖）：
  1. SDD DQA PASS (檢查對應的 `sdd_spec.md` 是否驗收完畢，無遺漏之 `[ ]`)
  2. TDD DQA PASS (檢查對應的 `tdd_spec.md` 是否驗收完畢)
  3. Claude DQA PASS (若有觸發，檢查審查報告是否存在)
  4. CEO Approve 狀態 (腳本需能判斷若目前處於 `/goal` 全自動模式則印出 `[x] CEO 自動打勾`，否則印出 `[ ] 等待 CEO 手動簽核`)
- **雙 DQA 職責分工**：
  - **`TDD_DQA` (全產品端到端功能測試)**：依據 Phase 2 審查後的 PRD 進行**全系統級別的整合功能測試 (Full-Product End-to-End System Testing)**，驗證跨模組、跨 Milestone Group 的完整功能流轉與業務閉環，而非先前單一 Milestone 的單點區域測試。
  - **`SDD_DQA` (戰略意圖與非目標覆核)**：對齊 Phase 2 審查後 PRD 中的 **Intent (開發初衷)** 與 **Non-goals (非目標邊界)**。
- **測試項目超標審核協定 (Phase 4 Exceed Limit Review Protocol)**：
  - 預設 Phase 4 全局驗收測試項目上限為 50 項。
  - **若 DQA 評估有必要超過 50 項**，DQA 嚴禁擅自擴充，**必須提交 PM 自動進行內部審查與核准 (本 Phase 4 全局驗收最多允許提交申請 2 次)**。PM 審查放行後寫入 `specs/.pm_exceed_approved` 驗證 Token 即可放行過關！
- **一票否決 (Single Veto)**：若全產品功能測試出現致命缺陷、或成品質量違背戰略初衷/侵犯 Non-goals，DQA 必須亮紅燈阻斷發布 (REJECT)。

## 2. 提報發布檢核表與 CEO 實機盲測 (Release Checklist & UAT Dogfooding)
- 雙 DQA 均放行過關後，PM 必須彙整成品封裝檔 (Build Artifacts)、Web 端點或文件準備呈交 CEO。
- **執行客製化發布檢核腳本 (Execute Custom Release Check Script) [CRITICAL]**：PM 在提報前，必須強制執行在第一步產出的 `python PM/Scripts/verify_Phase4.py`。
  - 腳本將會自動印出完整的 Release Checklist，確認 SDD/TDD/Claude DQA 等內部關卡皆已亮綠燈。
  - 嚴禁 PM 自行捏造 Check list，必須原封不動將腳本物理掃描後輸出的結果呈現給 CEO。
- **UAT 實機盲測 (Dogfooding)**：PM 將腳本印出的 Checklist 連同測試環境提交給 CEO，強烈建議 CEO 進行端到端盲測。
- 若發現致命阻斷型 Bug (P0/P1)，退回 Phase 3 修正。

## 3. 全員一致同意與發布解鎖 (Unanimous Consent & Pre-Release Guard)
- 提報上述 Checklist 與驗證步驟後，請 CEO 滿意並輸入 `/approve` 簽核。
- **Pre-Release Guard (全體一致同意檢查)**：
  - PM 執行預發布攔截腳本：
    `python .agents/skills/Johnny-project-team/scripts/pre-release.py`
  - 確保所有工程師與 DQA 全員無異議同意、且當前鎖檔處於 Phase 4+ 始解鎖發布權限。

## 4. 階段閘門與自動化部署 (Phase Gate Transition & Automated Release)
1. **執行閘門**：PM 強制執行階段閘門腳本：
   `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 4 --to_phase 5 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
2. **Automated Release Deployment**：[GREEN LIGHT] 後，PM 呼叫 `release_manager.py` 執行自動化 Git Merge, Version Tagging & Production Push。
3. 發布成功後，正式進入 **Phase 5 (Post-Release Audit & Maintenance)**。
