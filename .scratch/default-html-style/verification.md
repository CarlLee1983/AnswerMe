# 預設 HTML 樣式驗證

日期：2026-10-04。使用者授權建立共用預設樣式，以及文章式、簡報式兩個起始模板；明確要求優先，未指定樣式直接使用預設。

## 變更邊界

- [技能入口](../../skills/answer-me/SKILL.md) 在製作 HTML 前引導讀取[樣式指引](../../skills/answer-me/references/html-style.md)。預設閱讀版型為文章式；明確的簡報情境使用簡報式。
- [文章模板](../../skills/answer-me/assets/article.html) 與[簡報模板](../../skills/answer-me/assets/slides.html) 為可移動的單檔資源，使用同一套色彩 tokens、系統字體與內嵌樣式；簡報另有原生 JavaScript 導覽。沒有新增套件或執行期外部依賴。
- README 改為不限定 agent 的定位，補上兩個模板與使用說明；保留前一任務的自動開啟規則。
- 更新演練文件與[模板檢查](../../tests/answer-me/browser/verify-templates.mjs)。未更動 checker、hooks、npx 安裝副本、全域設定，也未提交或發布。

## 檢查結果

- `python3 scripts/check.py`：通過 metadata 與文件連結檢查。
- `python3 -m unittest discover -s tests -p 'test_checks.py'`：10 項通過。
- `node tests/answer-me/browser/verify.mjs`：歷史互動頁檢查通過；本次輸出位置為 `/var/folders/mp/2hbmdcp15qjfn3fhgctttgl40000gn/T/answer-me-browser-Co0cpy`，不代表重新生成的技能答案。
- `node tests/answer-me/browser/verify-templates.mjs skills/answer-me/assets .scratch/default-html-style/verified`：通過；[JSON 結果](verified/verification.json) 保存兩模板離線、色彩一致、桌面/390 px、簡報按鈕/方向鍵/Home/End/首尾邊界/控制項鍵盤隔離、無 JavaScript 全文與列印結果。所有頁面無 HTTP(S) 請求、無執行錯誤。
- 實際列印 PDF：模板簡報為五頁，獨立 reviewer 用 pdfinfo/pdftotext 核對各頁文字；主 agent 也檢視桌面、手機、列印與客製演練截圖。新增自動檢查確認模板每頁對應一個 PDF 頁面。
- `git diff --check`：通過。

## 新生成演練與審查

獨立 agent 只收到更新的技能包、原始 model.md 與兩個情境要求，未讀驗收欄或歷史輸出。它產出[預設文章](evaluation/article.html)及[深色橘色簡報](evaluation/slides.html)，保留來源、示意模型標示和 A 小於、大於、等於 B 的三種條件。依模擬使用者要求沒有自動開啟這兩份演練。

[演練紀錄](evaluation/delivery.md) 與 [JSON](evaluation/verification.json) 記錄離線、數值、版面、簡報導覽及降級閱讀。主 agent 另檢視成品，補驗 p = 0.6 時 M = 44 ms，輸出文章三頁及簡報五頁 PDF，結果見[補充檢查](evaluation/parent-check.json)。本次未重新執行所有其他技能語意情境，也未測實體印表機。

獨立審查發現列印樣式以固定配色蓋過客製顏色。新增回歸檢查在舊版本失敗；移除強制列印色彩後通過，並驗證注入深色橘色 tokens 時列印仍沿用它們。樣式指引說明深色列印需檢視背景圖形設定。相同 reviewer 複查此差異後確認無剩餘重大發現。

## 回復方式

回復本次新增的 HTML 樣式入口、文件段落，移除 references/html-style.md、assets 下兩個模板與 verify-templates.mjs，即可回到無預設樣式的行為；保留前一任務的 HTML 自動開啟修改。全域與已安裝副本不需還原。
