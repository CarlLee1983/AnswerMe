---
status: accepted
---

# 技能指示維持繁體中文

`SKILL.md` 以繁體中文撰寫，不為了「對模型更友善」而改成英文。盲評 A/B 測試顯示兩版表現在雜訊範圍內打平（中文版 84/86、英文版 85/86 項驗收條件，皆無重大問題），英文版沒有可見收益。維持中文的理由包括：使用者以中文提出的觸發詞與 `description` 相符；「可能」不能寫成「一定」這類中文措辭範例翻譯後就失去作用；維護者以中文閱讀；改寫後需要重跑全部演練。方法、樣本與限制見 `.scratch/skill-language-ab/verification.md`。

**Falsified if:** 以 `.scratch/skill-language-ab/verification.md` 的方法擴大樣本，或加入 HTML 交付與自動觸發情境後，英文版 `skills/answer-me/SKILL.md` 在驗收條件或重大問題數上穩定優於中文版。
