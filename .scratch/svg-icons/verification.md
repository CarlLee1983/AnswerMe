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
