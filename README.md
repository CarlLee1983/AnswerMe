# Answer Me

Answer Me 是協助理解概念與 agent 工作成果的解說技能，不限定特定 agent。它先理解需求，未指定格式時會詢問要 HTML、Markdown 文件或對話回答，再依問題組織文字、圖解與必要的互動，並在關鍵主張旁保留來源與驗證限制。預設使用繁體中文，保留必要的英文術語。

## 適合的問題

- **概念學習**：理解陌生概念、文章或程式庫，沿著具體流程看懂它如何運作。
- **成果審視**：對照方案、diff 與測試紀錄，理解前後行為、取捨，以及證據能支持哪些結論。

例如：

> 幫我理解這個 repo 收到請求後，如何一路讀取資料並回傳結果，附上相關程式位置。

> 解釋這次 diff 改變了什麼，以及現有測試能證明哪些行為。

> 用可離線開啟的互動 HTML，說明快取命中率如何影響平均延遲，並標明模型假設。

已指定格式時直接製作，單一事實查詢直接簡短回答。選擇 HTML 或 Markdown 會交付實際檔案與路徑；HTML 可用於靜態解說，只有互動能幫助理解時才加入控制項。完整 code review、修改程式及完整旁白影片不在這項技能的預設範圍內。

HTML 完成驗證後，會在可用的本機桌面環境自動開啟供閱讀；macOS 使用 `open`。可要求不要自動開啟，無法開啟時仍會交付檔案連結。詳見[技能的驗證與交付規則](skills/answer-me/SKILL.md#驗證與交付)。

## HTML 預設呈現

未指定外觀時採用共用的淺色閱讀樣式，不額外詢問。自行閱讀預設使用[文章式模板](skills/answer-me/assets/article.html)；明確要求簡報或逐頁講述時，使用[簡報式模板](skills/answer-me/assets/slides.html)。兩者都可離線開啟，模板中的內容是示例，產生成品時須換成本次解說與來源。

需求發起者的明確要求優先於內容情境與預設樣式，例如「用深色文章式 HTML」或「用品牌色做成逐頁 HTML 簡報」。配色、字體、間距、內容元件與調整流程見[樣式指引](skills/answer-me/references/html-style.md)。

## 技能內容

技能位於 [`skills/answer-me/`](skills/answer-me/SKILL.md)，包含：

- [`SKILL.md`](skills/answer-me/SKILL.md)：理解目標、形式選擇、來源核對與交付驗證規則。
- [`agents/openai.yaml`](skills/answer-me/agents/openai.yaml)：技能的顯示名稱與簡介。
- [`references/html-style.md`](skills/answer-me/references/html-style.md)：HTML 預設樣式、版型選擇與調整方式。
- [`assets/article.html`](skills/answer-me/assets/article.html)、[`assets/slides.html`](skills/answer-me/assets/slides.html)：可獨立開啟的文章式與簡報式起始模板。

`show-me`、`archify`、`visualize` 是環境中可選的製作能力，並非必要依賴。互動 HTML 使用內嵌資源，閱讀與操作不依賴 CDN、套件安裝、本機伺服器或執行期網路請求。

## 檢查與演練

從 repository 根目錄執行快速檢查：

```sh
python3 scripts/check.py
```

需要 Python 3.10+、PyYAML 與 Codex 的技能驗證器。依賴安裝、驗證器路徑、可選的 pre-commit hook 及其停用方式，見[檢查與回歸演練](docs/checks.md)。

快速檢查驗證技能 metadata 與文件相對連結。技能行為有變更時，還需依[演練說明](tests/answer-me/README.md)使用原始材料重新產出答案，核對語意與成果。保存的 HTML 通過瀏覽器檢查，只能證明該歷史成果仍符合檢查條件，不能證明目前技能會產生相同品質的答案。

## 文件導覽

| 路徑 | 內容 |
| --- | --- |
| [CONTEXT.md](CONTEXT.md) | 概念學習與成果審視的領域用語 |
| [docs/checks.md](docs/checks.md) | 檢查依賴、命令、hook 與驗證範圍 |
| [tests/answer-me/README.md](tests/answer-me/README.md) | 三組演練情境、語意驗收條件與瀏覽器檢查方式 |
| [AGENTS.md](AGENTS.md) | 在此 repository 工作的 agent 指引 |
