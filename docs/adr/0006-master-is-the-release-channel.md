---
status: accepted
---

# master 即發布管道，tag 只是 changelog 檢查點

README 的主要安裝方式是 skills CLI，而它在未指定 ref 時抓預設分支，並以技能資料夾的 tree hash 判斷有無更新，不讀 tag 或 GitHub Release（查證自 vercel-labs/skills 原始碼）。因此技能資料夾的變更一進 master 就已到達使用者；tag 與 Release 只是給手動下載者與讀者的 changelog 檢查點，版本只以 tag 表示，不另設版本欄位。網站也隨 master 部署，與 CLI 使用者實際拿到的內容一致。文件是否跟上，要在變更進 master 前把關，不能等到打 tag。決策過程見 `.scratch/release-sync/spec.md`。

## Considered Options

- **README 改以固定 ref（`#vX.Y.Z`）安裝**：tag 會成為真正的發布，但 CLI 的 `update` 沿用安裝時的 ref，使用者必須重新安裝才能升級，更新指令形同失效。
- **另設 release 分支作為預設分支**：可保留 master 作開發用，但多一層分支管理與 GitHub 預設分支設定，對單人直推的專案代價過高。
- **網站只在 release 時部署**：網站會對應已發布版本，卻與 CLI 使用者從 master 拿到的技能脫節。

**Falsified if:** `README.md` 的安裝或更新指令改為指定 ref，或 `.github/workflows/pages.yml` 改為只在 tag 或 Release 時部署；或 skills CLI 改為預設安裝最新 tag 或 Release。
