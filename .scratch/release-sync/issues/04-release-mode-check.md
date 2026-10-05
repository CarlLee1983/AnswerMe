# 04: 發布模式檢查

**What to build:** 維護者推送 tag 前，可在本機以 tag 名稱執行檢查器的發布模式，確認這個 tag 可以發布。檢查項目逐項收集，有錯一次全部列出並以非零狀態結束；通過時以零結束。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] tag 不存在或不是 annotated tag 時失敗
- [x] tag 訊息沒有以「文件與網站：」開頭且冒號後有內容的一行時失敗
- [x] 網站範例頁中「由 answer-me vX.Y.Z 產生」標記的版本若不是已存在的 tag 則失敗；舊但存在的版本通過
- [x] 範例頁與快速檢查都以 tag 指向的 commit 內容為準，工作區修改不影響結果
- [x] 該 commit 的快速檢查失敗時，發布模式也失敗
- [x] 測試涵蓋上述每個情境，以及多項錯誤同時列出；沿用既有暫存 git repo 加 subprocess 的模式
- [x] 對目前 repo 的 v0.1.3 執行時的結果記入本 ticket 的 Comments（預期：tag 訊息缺「文件與網站」一行而失敗）
- [x] 檢查說明文件補上發布模式的用法與檢查項目

## Comments

- 2026-10-05：實作於 `6ebc15d`，code review（Standards / Spec 兩軸）指出「文件與網站：」判斷可跨行等問題，修正於 `65c21e4`：比對限同一行、快照改以暫時 index 取出並與 `--staged` 共用、tag 名稱先驗證。`test_checks.py` 39 項通過。
- 對 v0.1.3 實跑：`tag v0.1.3 message needs a line starting with 「文件與網站：」 followed by text.`，exit 1；四個範例頁的 v0.1.3 標記有效、該 commit 快速檢查通過。此為既有 tag 早於本規則所致，不需補救。
