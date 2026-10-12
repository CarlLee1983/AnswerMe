# 借鑑 SeeCode

日期：2026-10-12。使用者要求評估 Aryanutkarsh/SeeCode 是否值得借鑑，同意吸收「前後差異圖」與「節點層級出處」兩點；圖的規模上限（約 9 節點、12 連線）未納入。

## 來源與取捨

以 [commit 82c33b6](https://github.com/Aryanutkarsh/SeeCode/tree/82c33b68be60578aeb21f429de5662a7d892a99f)（MIT）固定研究範圍；以 shallow clone 閱讀 `SKILL.md`、`references/` 與 `scripts/lib` 的遠端網址，沒有執行上游程式。

| 來源做法 | 本次吸收方式 |
| --- | --- |
| `references/types/architecture-delta.md`：同一張圖以 `added`／`removed`／`changed` 標出變更，只畫變更鄰域加一層，新路徑標為主線。 | [技能](../../skills/answer-me/SKILL.md)選型表新增「變更新增、移除或改寫了元件與呼叫路徑 → 前後差異圖」一列；行為差異仍交給文字或比較表。 |
| `references/repo-evidence.md`：節點與連線附 `{file, line}`；推論而未見的元件以虛線標示。 | 「文件、圖解與 HTML」的圖解規則補上：依據程式時每個節點與連線附檔案與行號，推論部分與已確認部分視覺區分。 |
| 整個技能：JSON spec → Node 渲染腳本、45 種類型、品牌、匯出、預設浮水印。 | 不內建、也不列為可選製作能力。渲染頁載入 Google Fonts，GIF／MP4 匯出從 jsdelivr 載入 muxer，與 [ADR 0002](../../docs/adr/0002-offline-self-contained-html.md) 的零依賴目標不合；預設浮水印也需額外關閉。依 [ADR 0001](../../docs/adr/0001-core-with-optional-production-skills.md) 只吸收選型與證據原則，該 ADR 的否證條件仍不成立。 |

## 驗證

- `python3 scripts/check.py`：通過。`git diff --check`：通過。
- 新增演練素材 `tests/answer-me/delta/input/`：`ticket_api` 複製自 `evidence/input`，`extract-cache.diff` 把 dict 快取抽成有 TTL 的 `TicketCache`。主 agent 在暫存副本以 `git apply` 套用並跑 `python3 -m unittest -v`：2 tests OK，與 `test-output.txt` 一致；兩個測試都不觸及過期。
- [Structural change 演練](evaluation/structural-change.html)：獨立 agent 只收到更新後的技能與 `delta/input`，未讀驗收欄。成品以一張差異圖標出 `TicketCache` 新增、`TicketService` 修改、inline dict 移除，`handle_get` 與 `FakeRepo.find` 為未變的相鄰一層，get／put 為主線；圖下表格列出每個節點與連線的 diff 行號，主 agent 逐行核對 13 處引用皆正確。沒有虛構 Redis、網路或清理工作者，並說明圖中無推論元件。行為比較表與 agent 說法核對指出 TTL 已實作但未被測試驗證。耗時約 15.5 分鐘，其中約 5 分鐘耗在 headless Chrome 卡住。
- 主 agent 以 `verify-site.mjs` 複查該檔：離線、無 HTTP(S) 請求、無執行錯誤、1200 與 390 px 無水平溢出，通過；檢視[桌面截圖](evaluation/structural-change-desktop.png)與 [390 px 截圖](evaluation/structural-change-390.png)。

單一樣本，不能證明所有結構性變更都會選出差異圖，或讀者因此更容易理解。未測列印與鍵盤焦點。成品中指向 `../delta/input/` 的來源連結是在演練目錄產生的，存到此處後不再有效。

## 邊界與回復

本次改動技能入口、README、[行為演練說明](../../tests/answer-me/README.md)，並新增 `tests/answer-me/delta/input/`；沒有修改 HTML 模板、檢查程式、hooks 或 ADR，未新增依賴，也未提交或發布。回復時反向套用上述差異並移除 `delta/` 與本紀錄。

## 後續：圖的規模上限

使用者同意加入第三點。[樣式指引](../../skills/answer-me/references/html-style.md)的「流程或關係圖」元件補上：一張圖以約 9 個節點、12 條連線為上限，重點節點 1 到 2 個，超過時依子問題拆圖或先畫概覽再分區展開。寫成閱讀建議，不加檢查器，理由與 [ADR 0004](../../docs/adr/0004-borrow-ste-without-compliance.md) 拒絕機械門檻相同。README 的借鑑段同步。

只做靜態核對：`check.py` 與 `git diff --check` 通過；上方 Structural change 成品約 9 個節點、9 條連線，已在上限內。沒有用超過上限的素材重跑行為演練，因此未驗證 agent 會因這條建議而拆圖。
