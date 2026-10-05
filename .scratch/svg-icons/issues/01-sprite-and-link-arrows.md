# 01: 圖示 sprite 與連結箭頭

**What to build:** 介紹頁加入一份隱藏的 Lucide 圖示 sprite（含授權註解）與共用圖示樣式，並以它取代連結文字中的「→」：外部連結改用外連箭頭，站內連結改用向右箭頭。訪客一眼分得出哪些連結會離開網站。規格見 [spec.md](../spec.md) 的 Implementation Decisions。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] sprite 以 HTML 註解寫明 Lucide、ISC copyright 聲明、來源 repo 與 commit SHA；本票只定義用到的 symbol
- [x] 外部連結（頁首與頁尾的 GitHub、Releases，hero 的 repo 連結，頁尾的 README 安裝說明與 Skills CLI）帶 `arrow-up-right`
- [x] 站內連結（四張範例卡的「打開範例」、CTA 的「先看範例」）的「→」由 `arrow-right` 取代
- [x] hero 模擬終端機的「✓」與「交付 →」維持文字
- [x] 圖示用 `currentColor`、約 1em、線寬 1.75、對齊基線，`aria-hidden="true"` 且不可聚焦
- [x] 網站靜態檢查通過；網站瀏覽器檢查全頁通過，桌面與手機截圖經人工目視，結果記入本功能目錄的驗證紀錄

## Comments

- 2026-10-05：實作於 `590b917`。所選兩個箭頭在 Lucide LICENSE 中列為 Feather 衍生，sprite 註解因此同時保留 ISC 與 MIT（Feather）聲明（已對照 LICENSE 查證）。頁首導覽原本只有 GitHub，未新增 Releases。網站靜態檢查與瀏覽器檢查通過；主代理另跑一次 verify-site 並目視桌面全頁截圖，外連與站內箭頭位置正確。驗證紀錄見 [verification.md](../verification.md)。
