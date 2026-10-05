# 範例頁核對紀錄

## 產生方式

- 日期：2026-10-05。技能與素材皆以 `git archive v0.1.3` 匯出到隔離目錄；每頁由一個獨立 agent 產生，只能讀取技能目錄與該頁素材，未取得規格、驗收條件或歷史評測成品。
- 請求原文：
  - ticket.html：「使用 answer-me，根據 ticket_api，做成離線靜態 HTML，讓我看懂 TicketService 與 FakeRepo 之間誰先呼叫誰、首次與再次讀取同一張票的差別，以及找不到票時怎麼回覆。（存檔路徑）完成後只給連結，不要自動開啟。」
  - model-article.html：「使用 answer-me，把 model.md 做成可離線開啟的互動 HTML 解說，文章式，讓我能調整 p、A、B，看懂 p 增加時 M 為什麼可能增加也可能減少。（存檔路徑）完成後只給連結，不要自動開啟。」
  - model-slides.html：「使用 answer-me，我要在讀書會上逐頁講解 model.md：做成可離線開啟的簡報式 HTML，其中一頁可以調整 p、A、B，讓大家看懂 p 增加時 M 為什麼可能增加也可能減少。（存檔路徑）完成後只給連結，不要自動開啟。」

## 發布處理（未改動解說內文）

- 各頁 `<body>` 開頭加入外框標示：返回介紹頁、「由 answer-me v0.1.3 產生 · 2026-10-05 · 經人工核對」、素材連結（固定於 v0.1.3）。
- model-slides.html：移除 Google Fonts 的 `<link>`，改用頁面既有的本機字型後備（範例頁不得有外部請求）。ticket.html 與 model-article.html 產生時已不含網路字型。
- 改寫的來源連結：
  - ../ticket/tests/answer-me/evidence/input/ticket_api/README.md -> https://github.com/CarlLee1983/AnswerMe/blob/v0.1.3/tests/answer-me/evidence/input/ticket_api/README.md
  - ../ticket/tests/answer-me/evidence/input/ticket_api/service.py -> https://github.com/CarlLee1983/AnswerMe/blob/v0.1.3/tests/answer-me/evidence/input/ticket_api/service.py
  - ../ticket/tests/answer-me/evidence/input/ticket_api/test_service.py -> https://github.com/CarlLee1983/AnswerMe/blob/v0.1.3/tests/answer-me/evidence/input/ticket_api/test_service.py

## 語意核對（人工）

- ticket.html：快取命中跳過 `FakeRepo.find`；找不到時 `get_ticket` 拋出 `NotFound`、`handle_get` 回 `(404, {"error": "not found"})`；明確指出 README 的 60 秒過期與 `service.py` 無過期邏輯衝突；註明材料中沒有真實資料庫或 HTTP 層；另兩項行為（查無結果不寫入快取、兩次讀取回傳同一 dict）標為臨時指令觀測，非測試證據。通過。
- model-article.html、model-slides.html：寫出 M = p·A + (1 − p)·B 與改寫 M = B + p·(A − B)；三種 A/B 情境俱全；A=20、B=80 時 p 由 0.5 到 0.6 使 M 由 50 降為 44 ms；標明為示意模型、非量測，並將改寫與斜率標為依來源公式的推導。通過。

## 自動檢查

- `python3 scripts/check.py`：通過。
- `node tests/answer-me/browser/verify-site.mjs`：4 頁、0 失敗（離線、零外部請求、桌面與 390 px 無溢出、range 控制項會改變頁面）。截圖已檢視：外框標示、介紹頁卡片、ticket 手機版。
- 首次執行時 model-slides.html 被誤判互動無效：互動頁位於隱藏投影片，`innerText` 不計隱藏文字。檢查改用 `textContent`，並先以「隱藏頁上的控制項」測試確認失敗再修正；`node:test` 16 項通過。
- 簡報翻頁屬按鈕互動，自動檢查不涵蓋；產生 agent 自述已測翻頁與鍵盤，本次未另行實測。列印版面未實測。

## 專案自我介紹

- 第一版未發布：缺口段落寫「`interactive/input/existing-explainer.html` 是 0 位元組的空檔」，實際為 304 bytes；且因匯出時移除 `.scratch/` 與 `tests/answer-me/*/output/`，把「`verify.mjs` 失敗」寫成專案現況。依規格不改內文，經維護者決定重新產生。
- 第二版素材：完整的 `git archive v0.1.3`，只移除先前的專案介紹成品 `.scratch/project-explainer-*`。請求原文與第一版相同：「使用 answer-me，幫我理解這個專案（Answer Me）是什麼、實際怎麼運作，做成可離線開啟的靜態 HTML，文章式，附上相關檔案位置。（存檔路徑）完成後只給連結，不要自動開啟。」
- 語意核對：上述兩項錯誤未再出現；`SKILL.md` 各節行號（1–4、10–15、17–21、23–41、43–52、54–60、62–82、84 起）與 v0.1.3 對得上；「五份 ADR 皆 accepted」屬實；`check.py`、`test_checks.py`（10 項）、`verify.mjs` 為產生 agent 在素材上的實測，未執行項目（模板檢查、語意演練、真實 Git hook）頁面已標明。通過。
- 發布處理：移除 Google Fonts `<link>`；20 個 `../repo2/` 相對連結改指 `https://github.com/CarlLee1983/AnswerMe/blob/v0.1.3/<同路徑>`；外框標示另說明文中「repo2 快照」即 v0.1.3 內容，且頁尾關於相對路徑的說明因連結改寫而不再適用（未改內文）。
- 發布時網站檢查把內文 `<code>file://</code>` 誤判為本機路徑；檢查器改為 `file://` 後須接路徑才算，先以測試確認失敗再修正，單元測試 27 項通過；網站瀏覽器檢查 5 頁、0 失敗。
