---
status: accepted
---

# 既有知識圖只當線索索引，不當證據

專案已有 Understand Anything 產生的 `.ua/knowledge-graph.json` 時，技能可用它找起點與候選關係，但每條寫進解說的關係都回原始碼確認並引用原始碼位置。讀過其實作（commit `532a2e9`）後確認：`calls` 邊由 LLM 依 import 與命名推斷，沒有證據或信心欄位；過期只能從 `gitCommitHash` 與 HEAD 比對得知。後來者可能想「省一步」直接引用圖的邊，或乾脆內建圖的產生流程；刻意不做，是因為前者會把推論包裝成事實，後者要引入 tree-sitter、多代理管線與 LLM 呼叫，與核心輕量、跨 agent 的定位相衝突。圖缺席、格式不符或過時時，回到逐跳讀原始碼的流程。取捨與實測見 `.scratch/understand-anything-borrowing/verification.md`。

**Falsified if:** `skills/answer-me/references/code-tracing.md` 允許直接引用圖的邊或摘要作為依據，或要求安裝、執行 Understand Anything；或 `skills/answer-me/scripts/ua_graph.py` 開始寫入檔案、呼叫網路或產生圖。
