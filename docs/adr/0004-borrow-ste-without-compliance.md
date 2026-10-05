---
status: accepted
---

# 借用 STE 減少歧義，不追求符合度

技術解說借用 Simplified Technical English 的固定名稱、明確主體、短句與可照做步驟，但不聲稱符合 ASD-STE100，也不設句長上限、禁詞比例或自動檢查器。後來者可能想「補上」這些量化規則；刻意不做，是因為解說的價值在保留原意，機械規則容易把「可能」改成「一定」、刪掉反轉結論的條件。驗收改用語意演練，見 `tests/answer-me/README.md` 的 Technical clarity evaluations。

**Falsified if:** `skills/answer-me/SKILL.md` 的「寫清楚技術解說」一節加入句長、禁詞或符合度門檻，或 `scripts/check.py` 開始對解說文字做禁詞或句長掃描。
