# 借鑑 ste-zht

日期：2026-10-22。使用者要求借鑑 dualface/ste-zht 改善技能；在提出的四個相容候選中選了「驗證狀態分辨」與「範圍外變更標示」，未選「封閉列舉」與「拆開名詞串」。

## 來源與取捨

以 [commit dd3ff6b](https://github.com/dualface/ste-zht/tree/dd3ff6b8d3fb74bc08a129e64e356ec7f92a7e41)（MIT）固定研究範圍；以 shallow clone 閱讀 `SKILL.md`、`references/terminology.md` 與 `examples/`，沒有執行上游程式（上游沒有程式）。

| 來源做法 | 本次吸收方式 |
| --- | --- |
| R20 如實寫驗證、terminology.md 第 4 節：已驗證／未驗證／失敗／未確認各有定義，附方法、結果與範圍；讀資料不代表運作驗證；工作狀態與驗證狀態分開。 | [技能](../../skills/answer-me/SKILL.md)「保留證據」新增一段定義四種驗證狀態；「驗證與交付」改為引用同一組狀態回報檢查，不另寫一套。 |
| `examples/result-report.md`：超出原範圍的 `auth/logger.ts` 改動單獨標出，交給使用者決定。 | 「找出理解目標」的成果審視補上：對照原始要求逐項核對，範圍外改動連同影響交給使用者決定。 |
| R7 句長上限、R11 情態詞只用三個、狀態詞「不得替換為」欄、全工作階段生效、固定回報模板與自檢清單。 | 不採用。句長與禁詞屬 [ADR 0004](../../docs/adr/0004-borrow-ste-without-compliance.md) 刻意拒絕的機械門檻；全域生效與固定模板屬回報風格，不屬解說用途。ADR 0004 的否證條件仍不成立（「寫清楚技術解說」一節未改，`check.py` 未加掃描）。 |

## 驗證

- `python3 scripts/check.py`：通過。`git diff --check`：通過。
- 新增演練素材 `tests/answer-me/scope/input/`：`ticket_api` 複製自 `evidence/input`；`change.diff` 讓 `get_ticket` 回傳副本（範圍內），並改寫 404 body（範圍外）。主 agent 在暫存副本以 `git apply` 套用並跑 `python3 -m unittest -v`：3 tests，`test_missing` FAIL，與 `test-output.txt` 一致。
- [Scope and verification states 演練](evaluation/scope.md)：獨立 agent 只收到更新後的技能與 `scope/input`，未讀驗收欄。成品逐項比對 request.md，標出 404 改動超出範圍並交給使用者決定；`test_returns_copy` 已驗證、`test_missing` 失敗並引用 tuple 差異、整合測試未驗證並附原因、lint 未確認並附確認方法；未宣稱整項完成。主 agent 逐行核對 13 處檔案與行號引用皆正確。符合全部驗收條件。附帶指出 `dict()` 淺層複製的限制，並標為推論。
- [evidence 回歸演練](evaluation/evidence.md)：同樣條件重跑既有 `evidence` 情境，符合原驗收欄（只說 `test_missing` 通過、不宣稱部署／全套／並行安全／TTL、索取缺少的 design note、404 簡答）。未提供原始需求時明說無法比對範圍。觀察到一處狀態用詞偏差：「fixes in production」與「concurrency safe」標為未驗證，依定義缺少執行證據應為未確認；不影響結論，但顯示兩者的界線在無需求材料時仍可能混用。該 agent 也正確指出既有 `evidence/input/change.diff` 的 hunk header（`+17,11`）與實際行數（8）不符，屬既有素材瑕疵，本次未修。

各情境單一樣本，不能證明所有審視都會分辨四種狀態或找出範圍外改動，也不能證明讀者因此更容易判斷。

## 邊界與回復

本次改動技能入口、README、[行為演練說明](../../tests/answer-me/README.md)，並新增 `tests/answer-me/scope/input/`；沒有修改 HTML 模板、檢查程式、hooks、網站或 ADR，未新增依賴，也未提交或發布。回復時反向套用上述差異並移除 `scope/` 與本紀錄。
