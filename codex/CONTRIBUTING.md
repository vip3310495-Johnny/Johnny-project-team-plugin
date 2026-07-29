# 貢獻 Codex Edition

Codex Edition 的所有變更必須留在 `codex/`。

## 開發流程

1. 從 `main` 建立功能 branch。
2. 修改 `codex/plugins/johnny-project-team-codex/`。
3. 每個正式 script 都必須在
   `skills/johnny-project-team/references/script-catalog.md` 說明用途。
4. 概念性或未完成腳本只能放在 `experimental/`，不得由 Hook 或正式
   Skill 呼叫。
5. 新增或修改狀態機時，補上整合測試。
6. ECC rules 必須保留原始目錄層次與 `paths:` frontmatter；新增 ruleset
   時同步更新 `RULESET_ORDER`、context manifest 與 selector 測試。
7. 執行全部測試與 Plugin/Skill validator。
8. PR 必須說明變更、原因、影響與驗證結果。

## 不得混用

- 不要修改根目錄 Antigravity manifest 來啟用 Codex 功能。
- 不要把 Antigravity JSON Agent profiles 複製進 Codex Plugin。
- 不要讓 Hook 呼叫外部 LLM、產生 approval 或寫入 DQA verdict。
- 不要把所有語言規則無條件注入 context；先偵測技術棧，再依產品路徑選擇。
- 不要對 React Native 套用假設 DOM 存在的 Web React rules。

## Commit

使用簡潔、可讀的 semantic commit，例如：

```text
feat(codex): add milestone execution policy
fix(codex): preserve DQA rejection escalation
docs(codex): clarify local marketplace installation
```
