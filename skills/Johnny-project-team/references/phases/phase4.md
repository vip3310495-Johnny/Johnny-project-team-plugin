# Phase 4: 全局驗收與發布上線 (Final Intent Audit & Release Deployment)

> **【定位與範圍】**：全局成品質量覆核與發布點。專注於「雙 DQA 全產品系統測試與戰略意圖覆核 (Dual DQA Full-Product Audit)」、「UAT 實機盲測 (Dogfooding)」與「自動化發布部署 (Release Deployment)」。

---

## 1. 雙 DQA 全局覆核與全產品功能測試 (Dual DQA Full-Product System Testing)
- PM 強制喚醒 **`SDD_DQA`** 與 **`TDD_DQA`**，並導入 **Phase 2 審查後的 PRD (`PM/Phase2_Reviewed_PRD.md`)**。
- **雙 DQA 職責分工**：
  - **`TDD_DQA` (全產品端到端功能測試)**：依據 Phase 2 審查後的 PRD 進行**全系統級別的整合功能測試 (Full-Product End-to-End System Testing)**，驗證跨模組、跨 Milestone Group 的完整功能流轉與業務閉環，而非先前單一 Milestone 的單點區域測試。
  - **`SDD_DQA` (戰略意圖與非目標覆核)**：對齊 Phase 2 審查後 PRD 中的 **Intent (開發初衷)** 與 **Non-goals (非目標邊界)**。
- **測試項目超標審核協定 (Phase 4 Exceed Limit Review Protocol)**：
  - 預設 Phase 4 全局驗收測試項目上限為 50 項。
  - **若 DQA 評估有必要超過 50 項**，DQA 嚴禁擅自擴充，**必須提交 PM 自動進行內部審查與核准 (本 Phase 4 全局驗收最多允許提交申請 2 次)**。PM 審查放行後寫入 `specs/.pm_exceed_approved` 驗證 Token 即可放行過關！
- **一票否決 (Single Veto)**：若全產品功能測試出現致命缺陷、或成品質量違背戰略初衷/侵犯 Non-goals，DQA 必須亮紅燈阻斷發布 (REJECT)。

## 2. CEO 實機盲測與 UAT 驗收 (User Acceptance Testing / Dogfooding)
- 雙 DQA 均放行過關後，PM 彙整成品封裝檔 (Build Artifacts)、Web 端點或文件呈交 CEO。
- **UAT 實機盲測 (Dogfooding)**：CEO 進行端到端盲測。
- 若發現致命阻斷型 Bug (P0/P1)，退回 Phase 3 修正。

## 3. 全員一致同意與發布解鎖 (Unanimous Consent & Pre-Release Guard)
- CEO 滿意並輸入 `/approve` 簽核。
- **Pre-Release Guard (全體一致同意檢查)**：
  - PM 執行預發布攔截腳本：
    `python .agents/skills/Johnny-project-team/scripts/pre-release.py`
  - 確保所有工程師與 DQA 全員無異議同意、且當前鎖檔處於 Phase 4+ 始解鎖發布權限。

## 4. 階段閘門與自動化部署 (Phase Gate Transition & Automated Release)
1. **執行閘門**：PM 強制執行階段閘門腳本：
   `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 4 --to_phase 5 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
2. **Automated Release Deployment**：[GREEN LIGHT] 後，PM 呼叫 `release_manager.py` 執行自動化 Git Merge, Version Tagging & Production Push。
3. 發布成功後，正式進入 **Phase 5 (Post-Release Audit & Maintenance)**。
