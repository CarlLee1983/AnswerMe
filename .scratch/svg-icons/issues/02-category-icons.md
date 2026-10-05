# 02: 類別圖示：用途卡與能力邊界

**What to build:** 兩張用途卡與能力邊界的四項前各加上代表圖示，讓訪客捲動時一眼分辨概念學習與成果審視，以及 language、media、html、scope 四項限制。沿用 01 建立的 sprite 與樣式。

**Blocked by:** 01（圖示 sprite 與連結箭頭）

**Status:** ready-for-agent

- [x] 「概念學習」`book-open`、「成果審視」`git-compare`
- [x] language `languages`、media `video-off`、html `file-code`、scope `target`
- [x] 新 symbol 加入既有 sprite，不另建第二份
- [x] 圖示裝飾性（`aria-hidden="true"`），文字內容與改版前相同
- [x] 網站靜態檢查與瀏覽器檢查通過；桌面與手機截圖人工目視確認對齊、間距與無溢出，結果記入驗證紀錄

## Comments

- 2026-10-05：實作於 `89835b6`；`target` 加入授權註解的 Feather 衍生列舉。網站靜態檢查與瀏覽器檢查通過；主代理另跑 verify-site 並放大目視桌面截圖的用途卡與能力邊界，圖示與標題、mono 標籤同高、間距一致。驗證紀錄見 [verification.md](../verification.md)。
