# 避坑知識庫 (Lesson Learnt Registry)

本團隊致力於打造「絕不犯同一個錯誤兩次」的工程文化。此文件定義了 RCA (Root Cause Analysis) 與 Lesson Learnt 的紀錄規範。

## 1. 誰可以提出教訓？
所有人 (PM、Engineer、DQA) 都可以提出教訓！
工程師在踩坑時、PM 在規劃失誤時、DQA 發現高頻 Bug 時，都擁有提出防呆規則的權利與義務。

## 2. 絕對禁令：禁止直接寫入
為了避免系統被灌水或被寫入過度防禦的「幻覺規則」，**絕對禁止任何 Agent 直接修改知識庫或呼叫底層寫入腳本。**
所有的知識點都必須經過「知識驗證官 (Lesson Verifier)」的獨立審核。

## 3. 如何寫入 (強制 Hook 流程)
當你想寫入教訓時，你**只能**執行以下指令觸發 Hook (必須指定 `--role`)：
```bash
python .agents/skills/Johnny-project-team/scripts/verify_lesson_hook.py --role Engineer --proposal "您的具體教訓與防呆 SOP"
```
（如果是在全域使用，請替換為正確的絕對路徑：`C:\Users\User\.gemini\config\skills\Johnny-project-team\scripts\verify_lesson_hook.py`）

**Hook 運作機制**：
1. 它會在背景喚醒 Verifier 子代理人。
2. 進行「爆炸半徑控制 (Blast Radius)」、「可執行性 (Actionable)」、「通用性 (Generic)」三項嚴格審查。
3. 若通過 (`[APPROVED]`)，Hook 會自動將你的教訓晉升寫入至 `.agents/lessons_learned/` 中。
4. 若被駁回 (`[REJECTED]`)，請閱讀駁回原因並重新執行 Hook 提交。
5. **[警告]**：如果同一提案連續被駁回 5 次，系統會觸發致命錯誤，屆時你必須停止動作，並呼叫 CEO (人類) 尋求幫助。

## 4. 知識繼承 (Knowledge Inheritance) - 按需查詢
- 為了節省 Token 消耗並避免 Agent 記憶體超載，**絕對禁止**要求 Agent 閱讀整份全域歷史教訓。
- 新 Agent 被喚醒時，PM **必須先執行 `python scripts/query_lesson.py <角色標籤> <相關關鍵字>`** (例如：`python scripts/query_lesson.py Engineer 資料庫鎖`)。
- 只有與本次任務高度相關且符合角色的「歷史教訓查詢結果」，才會被注入至新 Agent 的初始 Context 中。
