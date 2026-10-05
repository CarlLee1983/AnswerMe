# SVG 圖示驗證紀錄

## 01 圖示 sprite 與連結箭頭

### 改動

- `site/index.html` 加入隱藏 sprite（`arrow-up-right`、`arrow-right` 兩個 symbol）與共用 `.ico` 樣式（`currentColor`、1em、線寬 1.75、圓端點、`vertical-align: -.125em`）。
- 外部連結（頁首與頁尾 GitHub、頁尾 Releases、hero repo 連結、頁尾安裝說明與 Skills CLI）帶 `arrow-up-right`；四張「打開範例」與 CTA「先看範例」帶 `arrow-right`；原文字「→」已移除。hero 終端機的「✓」與「交付 →」維持文字。
- 圖示一律 `aria-hidden="true"`、`focusable="false"`。
- 授權：Lucide 為 ISC，但 `arrow-up-right`、`arrow-right` 列在 Lucide LICENSE 的 Feather 衍生清單內，需另附 MIT（Cole Bemis）聲明，兩份聲明皆寫入 sprite 註解，並註明 repo 與 commit SHA。後續票若用到 `check` 等同屬 Feather 清單的圖示，註解已涵蓋；其他圖示僅需 ISC。

### 已實測

- `python3 scripts/check.py`：通過（含網站靜態掃描）。
- `node tests/answer-me/browser/verify-site.mjs site <暫存目錄>`：5 頁、0 失敗（無執行期例外、桌面與手機無水平溢出）。
- 人工目視 index 桌面與手機截圖（含局部放大）：圖示約與文字同高、貼齊基線、顏色跟隨連結（含 hero 的灰色連結）、底線不延伸到圖示；手機頁尾「安裝說明」換行時圖示跟著文字，未單獨成行；終端機文字符號未變。

### 僅靜態確認

- 無障礙屬性（`aria-hidden`、不可聚焦）只確認於 HTML 原始碼，未以螢幕閱讀器或 Tab 鍵實測。
- 連結文字的可見內容僅少了「→」，以 grep 確認，未做自動比對。
- 截圖未提交。

## 02 類別圖示：用途卡與能力邊界

### 改動

- `site/index.html` 既有 sprite 新增 `book-open`、`git-compare`、`languages`、`video-off`、`file-code`、`target` 六個 symbol（取自同一 Lucide commit）；不另建 sprite。
- 「概念學習」「成果審視」h3 與限制 `dl` 的四個 `dt`（language、media、html、scope）前各加圖示，`aria-hidden="true"`、`focusable="false"`，文字不變。
- 新增一條 CSS：`.mode h3 .ico, .limits dt .ico { margin-right: .45em; }`，其餘沿用 `.ico`（1em、線寬 1.75）。
- 授權註解：`target` 屬 Feather 衍生清單，註解有列舉圖示，已把 `target` 加進 MIT 段的列舉；其餘五個僅需 ISC。

### 已實測

- `python3 scripts/check.py`：通過。
- `node tests/answer-me/browser/verify-site.mjs site <暫存目錄>`：5 頁、0 失敗。
- 人工目視 index 桌面與手機截圖（用途卡與限制區局部放大）：圖示與標題／mono 標籤同高、顏色跟隨文字（dt 為 accent 綠）、間距一致、無溢出；手機限制區 dd 換行正常。

### 僅靜態確認

- 無障礙屬性僅確認於 HTML 原始碼，未以螢幕閱讀器實測。
- 文字內容不變僅以 diff 目視確認，未自動比對。
- 截圖未提交。

## 03 複製按鈕圖示與狀態

### 改動

- `site/index.html` sprite 新增 `copy`、`check` 兩個 symbol（同一 Lucide commit）；授權註解的 Feather 列舉加入 `check`（`copy` 僅 ISC）。
- 兩個複製按鈕改為「`<svg class="ico">` + `<span class="copy-text">`」；`.copy` 改 `inline-flex`、`gap: .45em`，並以 `.copy .ico` 覆寫連結用的 margin 與 vertical-align。`aria-label` 與 `.sr-status` 不變。
- 腳本只更新文字 span 與 `<use>` 的 href：成功 `copy` → `check` 並顯示「已複製」；剪貼簿被拒時維持 `copy`、文字「已選取」、狀態區宣告與選取行為照舊。還原延遲由 2 秒改為 3 秒，還原 `copy` 與原文字。
- 計時器每顆按鈕一個；每次點擊先 `clearTimeout` 再重設，連按時以最後一次點擊起算 3 秒，不會被舊計時器提早還原。

### 已實測

- `python3 scripts/check.py`：通過。
- `node tests/answer-me/browser/verify-site.mjs site <暫存目錄>`：5 頁、0 失敗。
- 人工目視 index 桌面與手機截圖（hero 與 CTA 兩顆按鈕局部裁切）：預設狀態的 copy 圖示與文字同高、置中，按鈕尺寸合理，手機未溢出。

### 待主 agent 以 Playwright 實測

- 點擊後 `copy` → `check`、3 秒後還原、連按不提早還原、剪貼簿被拒時圖示維持 `copy`：尚未實測，僅經程式碼閱讀確認。
- 無障礙屬性僅確認於 HTML 原始碼。截圖未提交。

### 03 複製按鈕點擊實測（主代理，Playwright）

以本機 HTTP server（127.0.0.1，安全來源，剪貼簿 API 可用）開啟介紹頁，以 Playwright 實測，全部符合規格：

- 初始：兩顆按鈕皆為 `#i-copy`、文字「複製」、各含 1 個 SVG。
- 成功路徑（兩顆按鈕各測）：點擊後 0.3 秒為 `#i-check`、「已複製」、狀態區「已複製」，SVG 仍為 1 個；3.3 秒後恢復 `#i-copy`、「複製」、狀態區清空。
- 連按：第一次點擊後 1 秒再點一次，距第一次 3.3 秒時仍為勾選、4.3 秒時恢復，證實計時器以最後一次點擊重新起算。
- 剪貼簿被拒（以腳本讓 `writeText` reject）：文字「已選取」、圖示維持 `#i-copy`、狀態區「已選取，請按 ⌘C／Ctrl+C」，安裝指令被選取；3.2 秒後恢復。
- 截圖：hero 區複製後顯示勾選圖示與「已複製」，與指令列對齊（截圖未存入 repository）。

未實測：真實使用者手勢下各瀏覽器的剪貼簿權限差異；`file://` 開啟時的行為（依既有退路應走「已選取」）。
