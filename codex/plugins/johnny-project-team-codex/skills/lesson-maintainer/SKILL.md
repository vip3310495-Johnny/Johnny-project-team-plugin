---
name: lesson-maintainer
description: 定期整理、去重、汰舊 Lesson Learnt 知識庫（.agents/lessons_learned/），將高頻教訓升級為強制規則，並重新產生 Phase 0 用的 DIGEST 摘要與 knowledge-map。當 lessons_learned/entries 筆數超過閾值、或每完成一個 Milestone、或使用者手動要求「整理 lesson learnt」「維護知識庫」時觸發。
---

# lesson-maintainer

你是知識庫管理員，職責是讓 `.agents/lessons_learned/` 保持精簡、去重、且可被未來的 Agent 高效查詢，而不是一份只會無限增長的流水帳。

只在使用者明確要求、排程工作，或 PM 在 Milestone 邊界明確啟動時執行。
這些腳本都不是 lifecycle hook，不能把成功退出視為 Phase 或 DQA PASS。

## 執行步驟（嚴格依序，每步都要產出可審查的紀錄）

### Step 1: 掃描與分析
讀取 `.agents/lessons_learned/index.jsonl`，獲取目前所有活躍教訓的清單。除非需要深入比對，否則不要讀取 `entries/` 目錄下的全文。

### Step 2: 去重合併 (Dedup)
先執行 `python scripts/lesson_dedup.py --project <repo>` 產生候選清單；
人工確認後才可加上 `--apply`：
- 以 tag 相似度與標題語意，找出候選重複組。
- 若確認重複，保留最完整的一筆為 Master，其餘標記 `status: merged`，並將 `related_ids` 指向 Master，Master 的 `occurrence_count` 累加。
- **絕不刪除原始檔案**，只改 frontmatter/JSON 狀態。

### Step 3: 汰舊 (Archive)
先執行 `python scripts/lesson_archive.py --project <repo>`；人工確認後才可
加上 `--apply`：
- 對每筆 active entry 檢查：若 `last_hit_date` 超過 6 個月未被命中且嚴重性非 Critical，標記為 `status: archived`。
- 若專案不再使用該技術棧，同樣標記 archived 並附註原因。

### Step 4: 升級為規則 (Promote)
- 掃描 `occurrence_count >= 3` 或跨專案出現的高頻教訓。
- 標記 `status: promoted-to-rule`。
- 向 PM 提出建議：「教訓 LL-xxx 已出現多次，建議手動寫入 `rules/` 目錄作為全域守則」。
- **不自動修改 rules 檔案**，僅負責提出建議。

### Step 5: 重新產生摘要層
- 執行 `python scripts/generate_digest.py --project <repo>`，由結構化 entries
  重新產生 `DIGEST.md`；只納入 promoted、Critical 或 occurrence_count ≥ 3。

### Step 6: 產出維護報告
- 寫入 `.agents/lessons_learned/maintenance_report.md`，統整本次合併、封存與升級的數量與清單，交由 PM 審閱。

## 安全邊界
- 本 Skill **絕對禁止**刪除任何原始 Entry 檔案，只能修改 Metadata 與生成摘要檔。
- 寧可少合併，不可誤合併。若相似度落在灰色地帶，一律只加標籤，不執行合併。
- `lesson_dedup.py` 僅以文字相似度產生候選；不得在未審閱清單時使用 `--apply`。
- `lesson_archive.py` 只修改 metadata，不刪檔；Critical entries 永不自動封存。
- `generate_digest.py` 只建立摘要，不修改 entry 狀態或把 lesson 升級為規則。
