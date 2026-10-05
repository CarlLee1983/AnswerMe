# 技能語言 A/B：中文版與英文版 SKILL.md

- 日期：2026-10-05。
- 問題：把 `SKILL.md` 全文改成英文，是否讓 agent 執行得更好。
- 方法：子代理逐句翻譯出 [英文版](SKILL.en.md)，保留規則、條件與語氣強度；封存時只把 `references/html-style.md` 連結改指 repo 內實際位置，測試時英文版不含該參考檔，所測情境也不需要它。兩版各以 clarity 的 actors、claims、brief 與 conditions 小篇幅情境跑兩輪；中文版第一輪沿用 commit `3b27691` 保存的回答。每輪由獨立子代理只讀技能與原始素材作答。16 份回答打亂並以隨機 id 命名後存於 [answers/](answers/)，由一名看不到 [對照表](key.tsv) 的評審依 `tests/answer-me/README.md` 驗收條件評分，結果見 [grades.json](grades.json)。
- 結果：中文版通過 84/86 項驗收條件、平均 4.63 分、7 個小瑕疵；英文版 85/86 項、4.50 分、12 個小瑕疵；兩版都沒有重大問題。未通過的項目都是同版本兩輪結果不一致，評審判定各情境差異在雜訊範圍內（conditions 例外，但差異同樣出自同版本兩輪之間）。
- 限制：每版每情境只有兩個樣本；只測對話文字，未測 HTML、Markdown 交付與追問修改；題目明確點名 answer-me，未測 `description` 語言對自動觸發的影響；只有一名評審，且與受測者是同一系列的模型。
