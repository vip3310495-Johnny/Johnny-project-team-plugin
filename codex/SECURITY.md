# Codex Edition 安全政策

## 回報安全問題

請優先使用 GitHub 的 private security advisory。不要在公開 Issue 貼出：

- API keys、tokens、cookies 或私鑰；
- 使用者個資；
- 可直接利用的破壞性 payload；
- 未遮蔽的完整環境或日誌。

若無法使用 private advisory，請只建立不含敏感細節的 Issue，請
maintainer 提供私下回報管道。

## 安全邊界

- Plugin hooks 必須保持短、可稽核，且不得自動啟動外部 LLM。
- Repository gate 不得修改全域 Git configuration。
- DQA PASS 必須綁定實際 Git tree，不接受僅以 exit code 或 timestamp
  充當品質證據。
- Claude、Security DQA 與 Log Agent 預設不得擴大權限或改寫產品程式碼。
- 使用者仍應在允許 Hook trust、安裝依賴或執行破壞性操作前檢視內容。
