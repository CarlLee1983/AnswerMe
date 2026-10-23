# 借鑑 humanize-writing

日期：2026-10-23。依[逐項評估](assessment.md)，使用者同意借用前三組候選：直譯腔（28，併 22、25 的道具用語）、意義膨脹（20）、假洞見標記與空泛收尾（3、7、8），另修正「示意數據」用字。第 4、5 組未採用，保留在評估紀錄。

## 改動

| 來源做法 | 吸收方式 |
| --- | --- |
| 28 直譯腔、22 繫詞迴避、25 比喻道具用中文說法 | [技能](../../skills/answer-me/SKILL.md)「寫清楚技術解說」新增「用會對同事說的中文」：不逐字搬英文的句構、動詞用法或比喻；找不到自然的中文詞時保留英文原詞。 |
| 20 意義膨脹與尾巴分析 | 新增「不替事實加價」：不追加來源沒說過的意義；作者的評價標為作者說法，自己的判斷寫成推論並附依據。後半句接上既有的「區分來源事實與推論」。 |
| 3 假洞見標記、7 轉場贅語、8 空泛收尾 | 新增「不放空殼句」：標記語刪掉後句子站不住，就換成具體機制；正文講完最後一個有依據的結論就停。明寫可追加項與預測問題照常提供，避免和「驗證與交付」衝突。 |
| 台灣用語（基線 6 次命中的來源） | 「保留證據」的「示意數據」改為「示意資料」。 |

README 加一段致謝。humanize-writing 沒有公開 repository，所以沒有附連結。字詞清單、破折號規則和 `check_zh.py` 都沒有引入。ADR 0004 的否證條件仍不成立：「寫清楚技術解說」沒有加句長、禁詞或符合度門檻，`scripts/check.py` 未改。三條原則各舉一兩個例子，例子都放在動作描述裡，沒有列成清單。

## 驗證

- `python3 scripts/check.py`：通過。`git diff --check`：通過。
- 新增演練素材 [`tests/answer-me/clarity/input/pr-description.md`](../../tests/answer-me/clarity/input/pr-description.md)，是虛構的英文 PR 說明，刻意放了五個容易直譯的說法（first-class citizen、surfaces、plays the role of、the shape of、load-bearing）、一句沒有證據的自我評價，以及有條件的數字、未執行的 CI、未量測的推測與排程中的工作。驗收欄寫在[演練說明](../../tests/answer-me/README.md)的 Technical clarity evaluations。
- [英文來源演練](evaluation/english-source.md)：獨立 agent 只拿到 scratchpad 裡的技能複本與這份輸入，沒有讀驗收欄。主 agent 逐項核對結果：
  - 五個說法都按意思改寫或省略。「load-bearing in the worst way」保留英文原句並解釋成「系統在壞的情況下反而靠它撐著」，也標為作者的描述。這個解釋稍微偏離原意（原意比較接近「影響最大的關鍵點，而且是壞的那種」），但沒有直譯成「承重」。
  - milestone 那句標為沒有證據的作者評價。
  - 840 → 310 ms 的五個條件都保留。38 個測試標為未確認（作者自述，沒附紀錄），CI 標為未驗證（已知沒跑）。on-call 是未量測的預期，Redis 不變，eviction 排程中、沒有日期。
  - 開頭直接回答，沒有標記語；結尾是可追加項和預測問題，沒有整體評價；沒有詢問格式。
  - 結論：符合全部驗收條件。附帶兩個有用的推論，都標了推論：一是「前後 p99 都低於 2 秒的 origin 延遲，表示至少 99% 的請求沒有打到 origin」，主 agent 核對過推理成立；二是 PR 沒寫重試用完後 `read` 的行為。
- [conditions 回歸](evaluation/conditions.md)：同樣條件重跑。公式、斜率 `A − B`、三種 A／B 情況、p=0.5 時 50 ms 都在，引用的第 4–7、9 行逐一核對無誤，也標明是示意。p=0.6 時的 44 ms 沒有直接寫出，只用「p 每增加 0.1，M 減少 6 ms」間接表達。新規則沒有砍掉推翻結論的條件。
- 用 `check_zh.py` 輔助掃描兩份成品：命中 7 個冒號（條列引言和標籤，屬允許用法）和 1 個「量測數據」（引用來源原文）。沒有需要處理的命中。

各情境都只有一個樣本，不能證明每次解說都不會直譯或加價，也不能證明讀者因此更容易看懂。

## 邊界與回復

本次改動 `skills/answer-me/SKILL.md`、`README.md`、`tests/answer-me/README.md`，並新增 `tests/answer-me/clarity/input/pr-description.md`；沒有修改 ADR、檢查程式、hooks 或網站。同一工作區的字體改動屬於另一件事，已單獨提交為 `0d0fadc`。回復時反向套用上述差異，並移除新素材與本目錄。
