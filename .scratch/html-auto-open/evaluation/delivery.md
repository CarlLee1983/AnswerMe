# 交付紀錄

- 情境要求：將 `tests/answer-me/conditions/input/model.md` 解說為可離線開啟的 HTML，僅用靜態文字與圖解。
- 成果：`model explanation.html`。使用內嵌 CSS、SVG，無 JavaScript、遠端字型或外部套件。起始條件的計算為 `0.5 × 20 + 0.5 × 80 = 50` 毫秒；比例變化的例子固定 A = 20、B = 80 毫秒。
- 渲染證據：`render.png`。使用 `tests/answer-me/browser/cdp.mjs` 的 `withOfflinePage`，從本機 `file://` 開啟並模擬離線網路，擷取 1200 × 900 視窗的全頁截圖；已實際檢視截圖，文字、SVG、公式和來源連結呈現正常。
- 瀏覽器檢查：Node 命令結束碼 `0`。頁面標題與主標題均為「兩條處理路徑的平均耗時」；初始結果顯示 50 毫秒；SVG 可見；頁面寬度 1200 等於視窗寬度 1200；來源連結解析到原始 `model.md`；`runtimeErrors: []`、`remoteRequests: []`。
- 桌面開啟：驗證後執行 `open '/Users/carl/Dev/CMG/AnswerMe/.scratch/html-auto-open/evaluation/model explanation.html'` 一次，結束碼 `0`。
- 限制：`open` 成功只證明 macOS 接受開啟要求，無法證明使用者已看到或理解頁面。瀏覽器渲染檢查為桌面尺寸；未另測小螢幕視窗。內容為原文示意模型，非產品量測資料。
