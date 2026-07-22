# Phase 0：Grill-me 5W1H、設計方向與雙重核准

## 0A：PM／CEO Grill-me 對齊

PM 必須先讀取 `references/grill-me-phase0.md`，以 Grill-me 模式逐項引導 CEO 回答 Why、Who、What、Where、When-Action，以及「希望的設計風格」。每輪先複述已確認資訊、指出矛盾或缺口，再提出一組可直接回答的問題；CEO 可修正、補充或要求 PM 記錄假設。

PM 建立兩份產物：

- `PM/Phase0_GrillMe_Transcript.md`：完整問答、追問、CEO 決定與未解項。
- `PM/Phase0_5W_Alignment.md`：可核准的摘要。Why、Who、What、Where、When-Action 與設計方向各節都必須包含已確認事項、假設、待確認問題、Non-goals、驗收方向、CEO 決定與最後更新時間。

設計方向只定義期望的視覺／互動成果、品牌語氣、可近用性、參考案例與排除風格；不得在 0A 選定框架、元件庫、資料模型或其他 How。若產品沒有 UI，CEO 必須明確決定「不適用」及原因。

完成後，CEO 只可透過綁定 `PM/Phase0_5W_Alignment.md` 的 `phase0_5w_alignment` 核准 5W 與設計方向；此核准不等於 Phase 0 Exit。

## 0B：Architect How

先執行 `project_governance.py check-architect-dispatch`。通過後 Architect 才可建立 `Architect/Phase0_How_Architecture_Draft.md`，並以 `5W-TRACE: <decision-id> -> <5W-id>` 逐項記錄架構、技術、資料流、錯誤處理、可觀測性與風險決策對已核准 5W 的追溯。不可行或衝突時退回 PM／CEO；不得自行改寫 5W 或設計方向。

## 0C：完整套件 Exit

SDD DQA 與 TDD DQA 確認 5W、設計方向與 How 一致，How 可追溯且可測試，When-Action 可轉為 BDD。PM 彙整風險後取得獨立 `phase0_exit` 核准，再執行 Phase 0 Gate。5W 或設計方向的語意變更會使相關核准、How 與 DQA 結論 stale；純排版不會。