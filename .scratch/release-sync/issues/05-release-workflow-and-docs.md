# 05: release workflow 與發布文件

**What to build:** 維護者推送符合 `v*` 的 annotated tag 後，GitHub Actions 先跑發布模式檢查，通過後以 tag 訊息為 notes 建立 GitHub Release，標題沿用「Answer Me vX.Y.Z」。維護者與 agent 都有一份發布步驟文件可依循，AGENTS.md 指向它並寫明 agent 的界線。

**Blocked by:** 01 (ADR 0006：發布模型), 04 (發布模式檢查)

**Status:** ready-for-agent

- [ ] 推送 `v*` tag 時觸發；檢查失敗則不建立 Release
- [ ] 通過時以 tag 訊息建立 Release，權限僅給所需的 `contents: write`
- [ ] 不重跑瀏覽器檢查，以 master 的 CI 結果為準
- [ ] 發布文件涵蓋：發布模型摘要（連結 ADR 0006，不重述取捨）、tag 訊息格式與「文件與網站」一行的寫法（含「無需變更（理由）」）、推送前在本機執行發布模式、推送 tag、檢查失敗後刪除並重推 tag
- [ ] AGENTS.md 新增一節指向發布文件，註明 agent 不推送 tag、不建立 Release，可起草 tag 訊息並執行檢查
- [ ] 由維護者推送測試 tag（agent 只提供指令，不自行推送）驗證失敗路徑（缺「文件與網站」一行）與成功路徑，事後刪除測試 tag 與 Release；結果記入本 ticket 的 Comments
- [ ] 快速檢查通過
