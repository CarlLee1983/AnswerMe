# answer-me 實作與驗證紀錄

## 交付

依[已完成的決策地圖](../karpathy-concept-skill/map.md)建立技能；使用者在地圖交接後確認進入建立與驗證階段。

- [SKILL.md](../../skills/answer-me/SKILL.md)：理解目標、媒介選型、來源依據、可選能力、離線 HTML 及驗收與回饋。
- [agents/openai.yaml](../../skills/answer-me/agents/openai.yaml)：Codex 顯示名稱與簡述；保留自動選用，沒有必要工具依賴。
- 安裝連結：`/Users/carl/.codex/skills/answer-me` → `/Users/carl/Dev/CMG/AnswerMe/skills/answer-me`。已核對連結目標及入口內容；技能原始檔只有一份。
- 沒有新增套件、scripts、assets 或額外參考檔。技能主體足以承載目前需求。

## 結構與獨立審查

- 來源目錄及安裝連結均通過 `skill-creator/scripts/quick_validate.py`。
- 顯示資訊通過 YAML 解析、簡述長度檢查；預設自動選用，沒有宣告必要 MCP 或其他技能依賴。
- 同一位獨立 reviewer 完成技能與已定案決策的對照，以及後續單一修正的複查；沒有未解決的重大發現。

## 行為驗證

獨立代理只取得技能、任務與原始材料，不取得預期答案或先前結論。產物放在隔離的暫存目錄；可選媒介技能在這些演練中視為不可用。這驗證了核心獨立執行的路徑，沒有實際整合呼叫其他技能。

| 情境 | 實際結果 |
| --- | --- |
| 陌生 repo | 正確追蹤第一次讀取、重複命中與查無資料；指出 README 的 60 秒過期宣稱沒有程式實作。 |
| Agent diff 與測試報告 | 說清缺值分支的前後行為；將紀錄中的單一測試通過，與全部測試、正式環境、並行安全及 TTL 等無證據宣稱區分。依請求沒有重跑輸入測試。 |
| 指定來源缺失 | 發現指定設計筆記不存在，要求必要材料；沒有從程序內快取推造跨程序鎖定設計。 |
| 單一事實問題 | 對 HTTP 404 給出簡短解釋，沒有多餘的媒介產製。 |
| 互動 HTML | 產生可直接開啟的三參數解說頁；公式、單位、示意性質與適用限制可見。 |
| 離線成果修復 | 保留原檔，修復外部 script 依賴及錯誤的初始數值；修復版的滑桿能更新結果。 |
| 成立條件重測 | 新代理使用不同的兩路徑模型，能說明提高比例時平均耗時可能增加、減少或不變，並給出正確數值例子。 |

前四項文字成果另經獨立 reviewer 核對原始程式、diff、文件及測試紀錄，沒有重大發現。

## 離線瀏覽器實測

使用已安裝的 Chrome 與 Node 內建 WebSocket，透過隔離瀏覽器 profile 及 Chrome DevTools Protocol 驗證；沒有安裝瀏覽器套件或啟動網站服務。

- 以 `file://` 開啟 HTML，停用快取、繞過 service worker，設定離線模式。
- 負向基準：原始破損頁載入外部 script，滑桿改到 100% 後仍顯示 31 ms；檢查能偵測這個失效。
- 新解說頁：10 組數值情境通過，涵蓋 0%／100% 命中、變更兩條路徑時間、零值及結論反轉；另通過 4 個情境按鈕與鍵盤方向鍵操作。
- 修復頁：初始值正確為 33 ms；命中率 0%、100%、50%、75% 分別得到 120、4、62、33 ms。
- 兩個最終頁面均無 HTTP(S) 請求或 JavaScript 執行期錯誤。已檢視桌面截圖；互動解說在 390 px 寬度下沒有水平溢出，並檢視手機版截圖。

## 發現與修正

首次互動演練的數值運作正確，但說明將命中路徑一概稱為較快，沒有交代參數可令結論反轉。技能在既有的模型限制指引中補上「核對可操作範圍，寫明成立條件」；示例說明同步修正。新的獨立文字演練與 reviewer 複查均通過。HTML 功能未改動，沿用已通過的瀏覽器結果。

離線檢查程式本身曾因重複宣告頂層變數而中止；改為區域作用域後重跑通過。這是暫存驗證程式的問題，並非解說頁的執行錯誤。

## 證據與範圍

原演練使用 `/tmp/answer-me-eval-3vauikwo/`。2026-10-04 回顧改善已將輸入、代表輸出與原始 JSON 結果保存到 `tests/answer-me/`，並將瀏覽器檢查程式改為可攜版本；原截圖仍屬暫存產物，不作為必須存在的證據。下列連結改指向專案內保存的材料。

- [文字情境輸出](../../tests/answer-me/evidence/output/)
- [互動解說](../../tests/answer-me/interactive/output/explainer.html)與[修復版](../../tests/answer-me/interactive/output/repaired.html)
- [原離線檢查結果](../../tests/answer-me/browser/verification.json)與[原負向基準](../../tests/answer-me/browser/broken-baseline.json)
- [成立條件重測](../../tests/answer-me/conditions/output/response.md)
- [重跑命令與獨立行為演練方式](../../tests/answer-me/README.md)。重跑保存範例不等於重測更新後的技能行為。

這些是代表性演練與指定 Chrome 情境的驗證，沒有測量使用者是否理解、完整跨瀏覽器相容性，或其他技能的實際整合。安裝驗證涵蓋檔案系統連結與內容，沒有另外啟動新 Codex 對話測試自動載入。

最終來源 SHA-256：

- `SKILL.md`：`d57382dffb8c1d6131aca943e84b233eded35d026f4b05b998beede48584cb03`
- `agents/openai.yaml`：`de6e032ca762ec3eb225fbecb1618c10efbf6a18ba2e4f04da1d1c560a37c7c3`
