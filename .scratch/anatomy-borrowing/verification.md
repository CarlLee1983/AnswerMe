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
