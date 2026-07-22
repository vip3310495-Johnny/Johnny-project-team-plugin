# 🤝 貢獻指南 (Contributing to Johnny-Project-Team)

歡迎來到 **Johnny-Project-Team Plugin**！我們非常高興能與您一起打造這個開源專案。

## 🎯 我們的核心使命

在您準備發起 Pull Request (PR) 前，請先了解我們專案的核心精神：

**「給沒有軟體工程背景的人，一個有效且穩固的開發流程。」**

我們不把重點放在單純的「防爆」或「限制」，而是專注於**賦能決策者**。我們希望透過系統化的流程與角色定義，讓不懂程式碼的 CEO 也能透過邏輯判斷帶領 AI 團隊完成大型專案。

## 💡 我們歡迎哪些貢獻？

為了達成上述使命，我們特別歡迎以下三個領域的貢獻：

### 1. 優化 PM 的「選擇題」決策模型
我們希望系統不會把工程細節塞給使用者。如果您能優化 PM 的提示詞 (Prompt) 或腳本，讓它能更好地將複雜的技術問題翻譯成**「帶有優缺點分析的選項 (A/B/C)」**，這將是極大的貢獻。

### 2. 豐富視覺化輔助 (Visualizations)
CEO 需要透過視覺化來掌握進度。如果您能擴充 `Architect` 或 `PM` 產出 **Mermaid 流程圖、架構圖、與資料流向圖** 的能力，幫助非技術人員快速審視系統全貌，我們非常歡迎。

### 3. 擴充動態基因防線 (ECC Rules)
我們正在持續建立一套防呆機制 (Error Correction Code)。如果您發現 LLM 在開發特定框架時經常踩坑，歡迎將其歸納並貢獻至 `.agents/lessons_learned/`。系統會根據架構自動載入這些 Rules，讓未來的開發流程更加穩固。

## 🚀 如何發起 Pull Request

1. **Fork 本專案**：在您的帳號下建立分支。
2. **切換開發分支**：`git checkout -b feature/your-feature-name`。
3. **對齊核心使命**：確保您的修改是為了讓「非工程背景使用者」的體驗更加順暢，而非單純增加技術複雜度。
4. **提交變更**：`git commit -m "feat: your awesome feature"` (請遵守 Semantic Commit Messages)。
5. **發起 PR**：在 GitHub 上發起 Pull Request，並描述您的修改如何幫助決策者更輕鬆地掌控專案。

感謝您的貢獻，讓我們一起把 AI 專案管理變得更親民、更強大！
