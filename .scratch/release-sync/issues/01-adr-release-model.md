# 01: ADR 0006：發布模型

**What to build:** 新增一份 ADR，讓日後的維護者與 agent 知道：透過 skills CLI 安裝的使用者取得的是預設分支上技能資料夾的最新內容，所以 master 就是發布管道；tag 與 GitHub Release 是 changelog 檢查點；版本只以 tag 表示，不設版本欄位；網站維持隨 master 部署。依據與被否決的替代方案見 [spec](../spec.md) 的 Implementation Decisions。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] ADR 依 `docs/adr/` 既有格式與編號接續，狀態為已接受
- [ ] 寫明依據：skills CLI 未指定 ref 時抓預設分支，並以技能資料夾的 tree hash 判斷更新（註明查證來源為 vercel-labs/skills 原始碼）
- [ ] 列出被否決的三個替代方案與否決理由：固定 ref 安裝、release 分支作預設分支、網站只在 release 時部署
- [ ] 以 `**Falsified if:**` 段落收尾，條件可檢查，且以反引號標出依賴的檔案（README 與網站部署 workflow）
- [ ] 快速檢查通過
