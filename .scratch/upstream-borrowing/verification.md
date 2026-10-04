# 借鑑 answer-me-with-html

日期：2026-10-04。使用者要求參考 QingYunA/answer-me-with-html，並選擇直接吸收適合的做法、小幅改善現有技能。

## 來源與取捨

以 [commit 8a50e9b](https://github.com/QingYunA/answer-me-with-html/tree/8a50e9b6da20edb8d9e11748264a30b3b5c75aec) 固定研究範圍；透過 authenticated `gh api` 閱讀原始碼與文件，另以網頁工具查看公開 README。沒有執行上游程式。

| 來源做法 | 本次吸收方式 |
| --- | --- |
| [SKILL 的內容稿與元件選型](https://github.com/QingYunA/answer-me-with-html/blob/8a50e9b6da20edb8d9e11748264a30b3b5c75aec/skills/answer-me-with-html/SKILL.md#L61-L149)：先組織內容、每面板一個問題，依資訊關係選元件。 | [本地技能](../../skills/answer-me/SKILL.md) 先整理答案、子問題與依據，細分流程、時序、層級、時間線與比較表的適用關係。章節數依內容決定；既有格式選擇仍優先。 |
| [render.js](https://github.com/QingYunA/answer-me-with-html/blob/8a50e9b6da20edb8d9e11748264a30b3b5c75aec/src/render.js) 將內容解析、檢查、元件與模板渲染分開。 | [HTML 指引](../../skills/answer-me/references/html-style.md) 明確要求重用現有模板的 CSS、元件與導覽，按內容或明確外觀要求調整。這是製作流程上的借鑑，沒有引入編譯器、DSL 或套件。 |
| [SKILL 的局部面板修訂](https://github.com/QingYunA/answer-me-with-html/blob/8a50e9b6da20edb8d9e11748264a30b3b5c75aec/skills/answer-me-with-html/SKILL.md#L95-L104)：讀取源稿再替換對應面板。 | 現有文件需更新時先讀取成品，局部修改並保留其他內容與使用者調整；共同前提改變時同步修正受影響內容。沒有假設 AnswerMe 成品含上游的內嵌源稿。 |

上游 [README 的 Karpathy 歸因](https://github.com/QingYunA/answer-me-with-html/blob/8a50e9b6da20edb8d9e11748264a30b3b5c75aec/README.md#L199-L207) 與本專案的理解模型輸出方向相近。本輪未重新驗證 Karpathy 原貼文；既有來源考證見[研究紀錄](../karpathy-concept-skill/research/source-findings.md)。本次取捨是 AnswerMe 的設計判斷，並非 Karpathy 的逐字要求。

上游 [benchmark](https://github.com/QingYunA/answer-me-with-html/blob/8a50e9b6da20edb8d9e11748264a30b3b5c75aec/bench/README.md) 的 token 與速度數據不能直接套用到本次指引修改，亦未證明讀者理解程度。本次沒有宣稱同樣的效益。完整影片、固定面板數、自動出頁門檻及 STE 符合度不納入這次小幅改善。

## 驗證

- `python3 scripts/check.py`：通過技能 metadata、validator 與文件相對連結檢查。
- `git diff --check`：通過。
- 新生成演練：獨立 agent 只收到更新技能包、原始 `ticket_api` 與 HTML 要求，未讀驗收欄或歷史答案。產生[票券解說](evaluation/ticket.html)，依子問題組織時序圖、首次／再次讀取比較、404 分支，並區分 README 的 60 秒到期宣稱與程式未實作的落差。
- [瀏覽器紀錄](evaluation/verification.json)：以 `file://` 離線載入，桌面與 390 px 手機無 HTTP(S) 請求、執行錯誤或整頁水平溢出。圖與表在手機的各自容器內水平捲動。演練 agent 檢視渲染截圖；主 agent 亦檢視初版桌面與手機畫面。保存的[桌面](evaluation/desktop.png)及[手機](evaluation/mobile.png)截圖是局部修訂後的成品。遵循模擬使用者要求，沒有自動開啟桌面瀏覽器。
- [局部修訂差異](evaluation/followup.diff)：主 agent 先在比較段落加入讀者筆記，保存[修訂前版本](evaluation/ticket.before-followup.html)，再請同一 agent 補充找不到票時為何不寫入 cache。最終補上 `raise NotFound` 先於 cache 賦值的解釋與對應行號。主 agent 的[比對結果](evaluation/followup-check.json)確認只有 `missing` 區塊變更，其他內容逐位元組相同，讀者筆記保留。修訂後重新通過離線呈現檢查。
- [原始材料測試紀錄](evaluation/fixture-tests.txt)：主 agent 實際執行 `ticket_api` 的 `python3 -m unittest -v`，兩項通過，用來核對新頁面中的執行結果主張。此結果與既有單一測試歷史紀錄不同，不能當成其他測試已通過。
- [純對話演練](evaluation/short-answer.md)：同一演練 agent 在另一個純文字請求中保留 A < B、A > B、A = B 三種情況、50 → 44 ms 的例子與示意模型標示，未強加圖解、產檔或詢問格式。主 agent 核對回覆與原始 model.md。

獨立 reviewer 審查文件差異與 HTML／局部修訂證據。它指出新驗收條件應明確區分 README 的 TTL 宣稱與實作，已修正；同一 reviewer 複查後無剩餘重大發現。純對話回覆由主 agent 核對，未納入該次獨立審查。

沒有修改模板、checker 或 hooks，因此未重跑這些未變更元件的既有回歸套件。本次未重跑所有舊語意情境，也未演練共同前提改變時的跨段落更新。這些有限樣本不能證明所有生成結果的品質、token 節省或讀者已理解。保存的 HTML 來源連結指向本機原始材料；頁面內容可離線閱讀，移到另一台機器後來源檔案連結需重新定位。

## 邊界與回復

本次改動技能入口、HTML 指引、README 與[行為演練說明](../../tests/answer-me/README.md)，沒有修改 HTML 模板、檢查程式、hooks、全域設定或已安裝的技能副本。當次實作驗證未新增依賴，也未提交或發布。回復時反向套用上述文件的本次差異，保留後續編輯；本紀錄及演練證據可一併移除。
