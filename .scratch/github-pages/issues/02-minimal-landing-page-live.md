# 02: 最小介紹頁上線

**What to build:** 訪客打開 GitHub Pages 網址，看到繁體中文介紹頁：一句話定位、概念學習與成果審視兩種用途、一行全域安裝指令（詳細步驟連到 README 安裝章節）、能力邊界（只有繁體中文、不製作旁白影片、HTML 為單檔離線），以及範例卡片的預留區塊。頁面沿用技能文章式模板的樣式。push 到預設分支且變更網站目錄時自動部署，也可手動觸發。repo homepage 欄位與 README 開頭都連到網站，README 文件索引表新增網站目錄一列。規格見 [spec.md](../spec.md)。

**Blocked by:** 01（網站檢查防線）

**Status:** ready-for-agent

- [x] 介紹頁為單檔 HTML，內容依「定位 → 兩種用途 → 範例卡片預留 → 安裝指令 → 能力邊界」排列，用語與 CONTEXT.md 及 ADR 0002、0003、0005 一致。
- [x] 安裝步驟只有一行指令與 README 連結，未在網站重複完整步驟。
- [x] GitHub Actions 工作流程只在網站目錄變更或手動觸發時部署，無建置步驟。
- [x] 變更 repo 設定（Pages 來源設為 GitHub Actions、homepage 欄位）前先取得維護者確認。
- [x] 部署成功，網址可實際開啟並顯示介紹頁。
- [x] README 開頭與文件索引表已更新。
- [x] 網站檢查防線通過。

## Comments

- 2026-10-05：介紹頁、部署工作流程與 README 連結完成（`bb90d12`）。維護者確認後啟用 Pages（來源 GitHub Actions）、設定 homepage 並 push；首次部署 run 37264934783 成功，網址回應 200。390 px 經 CDP 量測無水平溢出、離線開啟無執行期錯誤，唯一對外請求為 Google Fonts。工作流程只監看 `site/**`，只改工作流程本身時需手動觸發。
