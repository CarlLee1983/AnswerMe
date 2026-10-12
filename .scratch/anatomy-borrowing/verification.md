# 借鑑 anatomy

日期：2026-10-12。使用者要求參考 wheresryan22/anatomy，並選擇「原則吸收＋列為可選能力」：小幅修改技能入口，不內建上游 kit。

## 來源與取捨

以 [commit 689dcf9](https://github.com/wheresryan22/anatomy/tree/689dcf966e63d92be10a5d593c6e19e10acd4422) 固定研究範圍（MIT）；以 shallow clone 閱讀 `SKILL.md` 與 kit 檔案清單，沒有執行上游程式。

| 來源做法 | 本次吸收方式 |
| --- | --- |
| [SKILL 的「The object is the explanation」](https://github.com/wheresryan22/anatomy/blob/689dcf966e63d92be10a5d593c6e19e10acd4422/SKILL.md#L27-L46)：以運作方式即概念的真實機構取代方塊與箭頭，例如以鎖的銷子說明快取鍵。 | [本地技能](../../skills/answer-me/SKILL.md) 的選型表新增「具體實物示意」一列，用於抽象機制以方塊箭頭仍難以想像時。加上本專案的證據要求：標明是示意，並指出對應不成立之處。 |
| [SKILL 開頭](https://github.com/wheresryan22/anatomy/blob/689dcf966e63d92be10a5d593c6e19e10acd4422/SKILL.md#L12)與 [workflow 第 2 步](https://github.com/wheresryan22/anatomy/blob/689dcf966e63d92be10a5d593c6e19e10acd4422/SKILL.md#L63)：圖上每個數字與動作都由同一個模型產生。 | 互動 HTML 規則新增：讀數、圖形與動態從同一個模型計算，不另外手寫數值。 |
| 整個技能：等角 SVG 實物圖的製作流程、kit、審查腳本、WebGL／3D 模式。 | 只在「製作與可選能力」列為可選製作能力，README 同步。依 [ADR 0001](../../docs/adr/0001-core-with-optional-production-skills.md) 不把 kit 或媒介指引複製進技能目錄。上游 kit 不載入遠端資源，產物仍要通過本技能的離線與驗證標準。 |

不納入：零件數下限、Figure／Hero／Epic 的工時分級、4× 放大審查與幾何 audit。這些屬於精緻插畫的製作標準，放進核心會讓簡單解說也背上製作負擔；需要時由 `anatomy` 本身承擔。

## 驗證

- `python3 scripts/check.py`：通過技能 metadata、validator 與文件相對連結檢查。
- `git diff --check`：通過。
- [實物示意演練](evaluation/concrete-object.md)：獨立 agent 只收到更新後的技能與 `conditions/input/model.md`，未讀驗收欄或歷史答案。它以直尺上兩堆硬幣的平衡點對應 p、A、B、M，保留 `M = pA + (1-p)B` 與 A < B、A > B、A = B 三種情況，p = 0.5 → 0.6 時 M 為 50 → 44 ms；標明示意，並列出直尺重量、硬幣離散、沒有單次處理真的花 M 毫秒三處不成立。全程在對話中回答，未強加圖解或產檔。主 agent 依新驗收條件核對。
- [互動 HTML 演練](evaluation/latency.html)：另一個獨立 agent 只收到技能與 `interactive/input/model.txt`。頁面以 `model(h, C, D)` 單一函式算出讀數、兩條路徑貢獻、判讀斜率、折線與圓點，沒有另外手寫計算值；初始值 33 ms。agent 以 headless Chrome 離線操作控制項並自行修正標籤重疊與手機字級。主 agent 另以 `tests/answer-me/browser/verify-site.mjs` 對該檔重跑：離線、無 HTTP(S) 請求、無執行錯誤、1200 與 390 px 無水平溢出、滑桿改值後頁面文字變化，通過；並檢視 [390 px 截圖](evaluation/latency-390.png)。[桌面](evaluation/latency-desktop.png)與[反轉狀態](evaluation/latency-reversed.png)截圖由演練 agent 產生。

兩次演練都是單一樣本，不能證明所有生成結果都會選出合適的實物，或讀者因此更容易理解。演練 agent 未檢查 JavaScript 停用、列印預覽與實體觸控裝置。沒有實際呼叫 `anatomy` 製作圖，因此未驗證其產物與本技能離線標準的相容性，只做了靜態閱讀（kit 不載入遠端資源）。

## 邊界與回復

本次改動技能入口、README 與[行為演練說明](../../tests/answer-me/README.md)，沒有修改 HTML 模板、檢查程式、hooks、ADR 或已安裝的技能副本。未新增依賴，也未提交或發布。回復時反向套用上述文件的本次差異；本紀錄及演練證據可一併移除。

## 後續：未指定形式時先交核心形式

使用者看過排隊令牌示意頁後反映製作過久。分析演練 agent 的執行紀錄：7 分 38 秒中約 2 分鐘構思模型、2.6 分鐘寫出 57 KB 頁面、2.7 分鐘驗證並修正四輪，工具本身只占數秒；那次 brief 明確要求三種形式，範圍是主因。

[技能](../../skills/answer-me/SKILL.md)因此改為：使用者未指定呈現形式時，以文字加一張最能回答主要子問題的圖或表交付，並列出可追加的圖解或互動；選型表的互動 HTML 改由使用者要調整參數、比較情境或逐步操作時觸發。[演練說明](../../tests/answer-me/README.md)新增 Core forms first 情境。

- 第一版規則只寫「一兩種形式」，獨立 agent 仍加入互動模型（3.5 分鐘），未通過；原因是選型表互動列「確實有助理解」仍會觸發。
- 改為觸發式後重跑（2.6 分鐘）：無控制項，文字加一張靜態圖；但演練題目寫了「只給連結」，未能檢查可追加項，題目已修正。
- 修正題目後重跑（1.8 分鐘）：[成果](evaluation/core-forms.html)無 input、button、select，只有一張主圖；交付回覆列出可追加的互動版；三種 A/B 情況與示意標示俱在。主 agent 以 `verify-site.mjs` 複查：無執行錯誤，1200 與 390 px 無水平溢出；唯一失敗是 Google Fonts 請求，此為網站範例頁規則，技能允許預設模板載入並在離線時退回本機字型。

各為單一樣本，耗時也受題目大小影響，不能證明所有請求都會變快。

## 後續：網站說明與實物示意範例

發布 v0.1.5 後，使用者指出網站只改了兩句文案。介紹頁因此新增「怎麼選呈現方式」區塊（理解需求對應形式的清單、未指定時的預設、anatomy 出處），並加入第五個範例。

- 產生方式比照 `.scratch/github-pages/verification.md`：以 `git archive v0.1.5` 匯出 `skills/answer-me` 與 `tests/answer-me/conditions/input` 到隔離目錄，獨立 agent 只能讀該目錄。請求：「使用 answer-me，根據 tests/answer-me/conditions/input/model.md，用一個具體的實物幫我理解 p 改變時 M 怎麼移動，做成可離線開啟的靜態 HTML，文章式。完成後只給連結，不要自動開啟。」另要求不得有外部請求、不用 Google Fonts。
- 成品以尺上兩塊砝碼的平衡支點對應 M，沒有控制項。主 agent 人工核對：p = 0.2、0.5、0.8 對應 68、50、32 ms，p = 0.25、0.75 對應 65、35 ms，反轉例 A = 80、B = 20、p = 0.8 時 M = 68；三處類比不成立與示意標示俱在。通過。
- 發布時只在 `<body>` 開頭加入外框標示（v0.1.5、2026-10-12、素材連結固定於 v0.1.5），內文未改。首屏截圖 `site/assets/concrete-object.webp` 由 headless Chrome 1280×800 截圖再以 `cwebp -q 80` 轉檔。
- 網站檢查：`check.py` 通過；`verify-site.mjs` 6 頁、0 失敗；介紹頁新區塊的桌面與 390 px 截圖、手機分頁列、範例頁首屏皆已檢視。列印版面未實測。
