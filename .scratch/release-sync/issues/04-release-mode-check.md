# 04: 發布模式檢查

**What to build:** 維護者推送 tag 前，可在本機以 tag 名稱執行檢查器的發布模式，確認這個 tag 可以發布。檢查項目逐項收集，有錯一次全部列出並以非零狀態結束；通過時以零結束。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] tag 不存在或不是 annotated tag 時失敗
- [ ] tag 訊息沒有以「文件與網站：」開頭且冒號後有內容的一行時失敗
- [ ] 網站範例頁中「由 answer-me vX.Y.Z 產生」標記的版本若不是已存在的 tag 則失敗；舊但存在的版本通過
- [ ] 範例頁與快速檢查都以 tag 指向的 commit 內容為準，工作區修改不影響結果
- [ ] 該 commit 的快速檢查失敗時，發布模式也失敗
- [ ] 測試涵蓋上述每個情境，以及多項錯誤同時列出；沿用既有暫存 git repo 加 subprocess 的模式
- [ ] 對目前 repo 的 v0.1.3 執行時的結果記入本 ticket 的 Comments（預期：tag 訊息缺「文件與網站」一行而失敗）
- [ ] 檢查說明文件補上發布模式的用法與檢查項目
