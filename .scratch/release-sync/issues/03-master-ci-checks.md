# 03: master CI 檢查 workflow

**What to build:** 每次推送到 master，GitHub Actions 自動執行快速檢查與網站瀏覽器檢查，讓沒裝 hook 或繞過 hook 的提交也會被發現，並保留瀏覽器檢查的截圖與結果供失敗時判讀。這是事後揭露，不阻擋推送。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] 推送到 master 時觸發，不限路徑；另可手動觸發
- [x] skill validator 從 openai/codex repo 的 skill-creator 範例資料夾以固定 commit SHA 下載，透過既有環境變數交給檢查器；SHA 只寫在共用下載腳本中（ticket 05 抽出，供 CI 與 release workflow 共用）並附註解說明來源
- [x] 下載失敗或缺 validator 時 workflow 失敗，不略過
- [x] 執行快速檢查與網站瀏覽器檢查（Node 22+、runner 內建 Chrome）
- [x] 瀏覽器檢查的輸出目錄上傳為 workflow artifact，失敗時也上傳
- [x] 實際推送一次確認綠燈，並取得 artifact 截圖；結果記入本 ticket 的 Comments
- [x] 檢查說明文件補上 CI 的範圍與它是事後檢查的性質

## Comments

- 2026-10-05：workflow 於 `6d64173`，validator 下載於 `15cdfa0` 抽成共用腳本，`5a63a13` 關閉 checkout 的 persisted credentials。本機已驗證：actionlint 無警告；固定 SHA 的 validator 下載成功、錯誤網址時 `curl` 失敗；`check.py` PASS；`verify-site.mjs` 5 頁 0 失敗。未驗證（待推送 master）：runner 上的 Chrome 啟動、PyYAML 安裝、artifact 上傳。剩餘兩項勾選待實際推送後補上。
- 2026-10-05：推送 master 後首次執行（run 37283244583）全綠，artifact `site-check` 含 10 張截圖與 `results.json`，Chrome 在 runner 上正常啟動。但截圖中文多為方框：runner 無 CJK 字型、離線檢查載不到 Google Fonts。`d1a1842` 於瀏覽器檢查前安裝 `fonts-noto-cjk`（約 12 秒），重跑（run 37283469699）全綠，介紹頁手機截圖中文正常，頁高由 4339 px 變為 4858 px，可見缺字確實影響版面量測。
