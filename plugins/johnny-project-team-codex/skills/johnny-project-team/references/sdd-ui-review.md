# SDD DQA UI 審查規範

## 先控制比較條件

記錄 build／commit、OS、viewport、DPI、縮放、主題、語系、字型、測試帳號與資料狀態。
使用相同條件取得核准 reference 與實際產品截圖；不得以 mockup 或設計稿取代實際
build 的操作證據。

至少覆蓋適用的預設、載入中、空白、錯誤、停用、focus／keyboard、響應式呈現
與關鍵互動後狀態。每份證據綁定 stable ID、review cycle、subject tree、步驟與
畫面狀態。

## 截圖優先

先以實際截圖對照核准 reference，檢查資訊層級、文字、位置、尺寸、間距、色彩、
可讀性、互動可理解性、截斷、overflow、focus、響應式呈現與無障礙性。若截圖
足以判定，就不得為了形式額外使用 OmniParser。

## OmniParser 備援審查

只有截圖不足以判定 FIXED requirement，或無法精準定位視覺差異時，才使用可用的
`omniparser` skill，並保存結構化報告、帶標籤的 overlay、原圖與參數。不可用時
回報 `BLOCKED_DEPENDENCY`，不得聲稱存在 OmniParser 證據。

Timeout 只是非強制操作建議：小型視窗 120 秒、一般主頁或設定視窗 300 秒、高解析度
全頁或密集表格 480 秒；GPU 通常 120–180 秒。CPU 首次可使用
`--max-dimension 640 --box-threshold 0.4` 與 300 秒；仍逾時或 FIXED 差異不清楚時，
改用 480 秒及較高解析度或裁切圖重試，不得直接降低驗證標準。
