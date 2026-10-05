# 05: release workflow 與發布文件

**What to build:** 維護者推送符合 `v*` 的 annotated tag 後，GitHub Actions 先跑發布模式檢查，通過後以 tag 訊息為 notes 建立 GitHub Release，標題沿用「Answer Me vX.Y.Z」。維護者與 agent 都有一份發布步驟文件可依循，AGENTS.md 指向它並寫明 agent 的界線。

**Blocked by:** 01 (ADR 0006：發布模型), 04 (發布模式檢查)

**Status:** ready-for-agent

- [ ] 推送 `v*` tag 時觸發；檢查失敗則不建立 Release
- [ ] 通過時以 tag 訊息建立 Release，權限僅給所需的 `contents: write`
- [x] 不重跑瀏覽器檢查，以 master 的 CI 結果為準
- [x] 發布文件涵蓋：發布模型摘要（連結 ADR 0006，不重述取捨）、tag 訊息格式與「文件與網站」一行的寫法（含「無需變更（理由）」）、推送前在本機執行發布模式、推送 tag、檢查失敗後刪除並重推 tag
- [x] AGENTS.md 新增一節指向發布文件，註明 agent 不推送 tag、不建立 Release，可起草 tag 訊息並執行檢查
- [ ] 由維護者推送測試 tag（agent 只提供指令，不自行推送）驗證失敗路徑（缺「文件與網站」一行）與成功路徑，事後刪除測試 tag 與 Release；結果記入本 ticket 的 Comments
- [x] 快速檢查通過

## Comments

- 2026-10-05：`release.yml` 於 `385c206`（`5a63a13` 補 `persist-credentials: false`），發布文件 `docs/release.md` 於 `1e74375`（`cfcecd4` 修正 immutable releases 說法：本 repo 未啟用），AGENTS.md 於 `5585cbe`、`83dc8f8`。checkout 在 tag 推送時可能把 annotated tag 改成輕量 tag（actions/checkout#290），workflow 於 checkout 後強制重抓 tag ref；本機模擬確認重抓前為輕量、重抓後為 annotated，含與不含「文件與網站」一行分別 exit 0 / 1。Release notes 用 `gh release create --notes-from-tag --verify-tag`。未驗證（待維護者推送測試 tag）：觸發、失敗路徑不建 Release、成功路徑建立 Release。
