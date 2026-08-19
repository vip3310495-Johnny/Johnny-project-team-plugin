# SDD DQA 審查規範

SDD DQA 驗證已完成產品是否符合核准意圖與契約，不評判偏好的內部實作。只能在
相同 stable ID、subject tree 與 review cycle 已取得 TDD PASS 後開始。

## 必要輸入與優先順序

1. 核准的 Ticket／Milestone PRD、FIXED 意圖、可觀察結果、容忍值與非目標；
2. Contract Matrix、Task Context Pack、User Flow 與核准的 UI reference；
3. Engineer Handoff、目前 commit／tree、TDD verdict 與含 hash 的證據；
4. active product paths、ECC selection 與所有適用規則；
5. Phase 4 時再加入 Architect review、Phase 4 PRD 與凍結的 Phase 3 契約。

輸入缺漏、版本矛盾或無法綁定目前 tree 時回報 `BLOCKED_INPUT`，交 PM 修正；不得自行
補寫契約或推測核准內容。

## 必驗維度

- 每個可觀察結果、FIXED 容忍值與關鍵使用者流程；
- 非目標與未授權功能擴張；
- CONTROLLED surface 是否留在 FIXED 範圍內並維持向後相容；
- API／CLI／資料格式、狀態轉移、錯誤訊息、恢復路徑與外部整合行為；
- UI 的內容、層級、互動、狀態、響應式呈現、無障礙性與核准視覺差異；
- 真實操作流程與產品 build，而非只讀測試或程式碼；
- Phase 4 是否保留 Phase 3 行為且沒有新增使用者可見功能。

不重跑未變更的完整 TDD suite；先驗證其 evidence hash，再集中於契約差異與實際
使用體驗。測試環境遵守 `references/dqa-test-environment.md`，UI 遵守
`references/sdd-ui-review.md`。

## Findings 與結果

使用 `assets/templates/sdd-dqa-review-report.md`。每項發現必須包含 contract ID、嚴重程度、
重現條件、預期、實際、證據與影響；不能因偏好另一種合法設計而 FAIL。

- `PASS`：所有適用契約與實際流程均有可信證據。
- `FAIL`：目前 tree 有可重現的契約、意圖、非目標、UX 或相容性違反。
- `BLOCKED_INPUT`／`BLOCKED_DEPENDENCY`／`BLOCKED_ENVIRONMENT`：無法完成可信審查，
  不得呼叫 verdict。

FAIL 建立新 review cycle，交 PM 路由回 Engineer；修改產品後重新 TDD → SDD。
