# machine-skill 借鑑：修改與驗證

## 採納範圍

依本次使用者授權，修改 `skills/answer-me/SKILL.md` 的既有段落：

- 互動解說突出主要輸入與觀察結果，依問題保留其他必要參數。
- 有來源案例時核對條件、輸入、單位與預期結果，區分推導與執行。
- 有助理解時選取有依據的邊界或失效情境，沿分岔解釋後果。
- 互動驗證涵蓋相關狀態與既有重設操作，核對文字、讀數與圖形。

README 補上固定版本的上游來源；tests/answer-me/README.md 增加四個演練情境，causality/input/model.md 是新增的原始教材。沒有引入 runtime、套件、影片流程或修改模板，也沒有變更 ADR、提交或發布。

## 獨立行為演練

兩個獨立 agent 只收到更新後的 skill package、原始素材及請求，沒有收到驗收表或先前答案。HTML 一個 session；三個文字請求在另一個 session 中分別回答。演練在隔離暫存目錄進行，完成後原樣保存到 [evaluation](evaluation/)。

| 請求 | 實際結果 | 證據 |
| --- | --- | --- |
| 用 model.md 做可調命中率的離線 HTML，不自動開啟 | 指出圖說 31 ms 與公式不符，正確結果為 33 ms；以 50%／62 ms 核對來源案例，維持教學示意標示 | [HTML](evaluation/html/cache-latency.html)、[交付回覆](evaluation/html/delivery.md) |
| 用 service.py 與 test_service.py 解說缺票流程，對話回答 | 追到 None → NotFound → 404，說明略過快取寫入；區分程式與測試依據，未宣稱真實 HTTP 服務已驗證 | [回覆](evaluation/text/response-1.md)、[實際測試輸出](evaluation/text/test-output.txt) |
| 用 conditions.md 說明增加 p 的結果，對話回答 | 保留 A<B、A>B、A=B 三種結果，例子標示為推導，沒有編造實測基準或故障 | [回覆](evaluation/text/response-2.md) |
| 問命中路徑延遲 C，對話回答 | 簡短回答 4 ms 並附來源，沒有擴張成完整流程 | [回覆](evaluation/text/response-3.md) |

完整演練請求與語意驗收條件見 [演練說明](../../tests/answer-me/README.md)。原始素材副本保存在 evaluation/html/input 與 evaluation/text/input。

## 執行結果

- `python3 scripts/check.py`：通過 skill frontmatter、顯示 metadata、文件連結與網站靜態檢查。
- `git diff --check`：通過。
- `node tests/answer-me/browser/verify-site.mjs`：6 頁、0 失敗。此次沒有修改網站，沿用這次執行結果。
- 獨立 agent 的 HTML 瀏覽器檢查：file:// 離線開啟，0／50／75／100% 分別得到 120／62／33／4 ms，重設回 75%／33 ms；390 px 無整頁水平溢出，零遠端請求與執行期例外。見 [verification.json](evaluation/html/verification.json)。
- 主 agent 補查：實際 CDP 鍵盤 ArrowRight 將 75% 改為 76%，得到 31.84 ms；核對四個狀態的讀數、公式、動態說明、圖說與標記位置。見 [parent-check.json](evaluation/parent-check.json)。
- 主 agent 檢視桌面、手機及四個狀態的截圖；獨立 reviewer 亦檢視四個狀態圖，確認鍵盤與畫面檢查缺口已補齊。此次固定差異的獨立審查沒有剩餘實質發現。

驗證腳本與原始回覆保留當次暫存目錄的絕對路徑，屬歷史證據；重跑時須將路徑改到新的演練位置，或依演練說明重新產生。此次結果只證明這批獨立答案與成果的行為，不代表所有新答案都會通過，也不證明讀者理解提升或模型具備真實系統精度。
