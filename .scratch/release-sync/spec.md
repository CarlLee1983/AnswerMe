# 發布同步：文件與網站跟上技能變更

Status: ready-for-agent

## Problem Statement

維護者每次改了技能，都得靠記憶確認 README、介紹頁與網站有沒有跟上，專案裡沒有任何機制保證這件事。發布流程沒有文件，tag 與 GitHub Release 全是手動建立；`check.py` 只檢查格式與連結，看不出使用者文件是否落後於技能；網站的瀏覽器檢查不在 pre-commit 裡，只能手動執行。

更根本的是，「發布」在這個專案的意義從未寫下。透過 skills CLI 安裝的使用者，取得的是預設分支上技能資料夾的最新內容，不看 tag 或 Release；技能資料夾的變更一進 master 就等於發出。若維護者以為「打 tag 才算發布」，就會把文件同步的把關放在太晚的位置。

## Solution

先把發布模型寫成決策紀錄：master 就是 CLI 使用者的發布管道，tag 與 GitHub Release 是 changelog 檢查點，版本只以 tag 表示，不另設版本欄位；網站維持隨 master 部署。

把關分三層，各自落在最可能補救的時點：

- **提交時（pre-commit）**：既有檢查照舊是真正的關卡；另加一則只提醒不阻擋的警告——變更動到技能卻沒動到使用者文件時提醒維護者。
- **進 master 後（CI）**：補跑 pre-commit 不涵蓋的檢查（含網站瀏覽器檢查），並抓出繞過 hook 或未安裝 hook 的提交。這是事後揭露，不是阻擋。
- **打 tag 時（release workflow）**：維護者推送 annotated tag，tag 訊息即 Release notes。workflow 先確認 notes 含「文件與網站」審視紀錄、範例頁標示的產生版本都是已存在的 tag，通過才建立 GitHub Release。

範例頁維持歷史成品的定位：標示由哪個版本產生，不隨每次發布重做。發布步驟寫成文件，並在 AGENTS.md 註明 agent 可準備 notes 草稿與執行檢查，但不自行推送 tag。

## User Stories

1. As a 維護者, I want 發布模型寫成 ADR, so that 日後不會有人誤以為打 tag 才是發布而把把關移到太晚的位置
2. As a 維護者, I want ADR 寫明 master 即 CLI 使用者的發布管道, so that 我在推送技能變更前就知道它會立即到達使用者
3. As a 維護者, I want ADR 附上可檢查的推翻條件, so that skills CLI 改為讀取 tag 或專案改用固定版本安裝時，這個決定會被重新檢視
4. As a 維護者, I want 版本只以 tag 表示, so that 不必在多處同步一個版本號
5. As a 維護者, I want 提交時若技能有變更但 README 與介紹頁都沒動就看到提醒, so that 我在最容易補文件的時刻想起這件事
6. As a 維護者, I want 這則提醒不阻擋提交, so that 不需要改文件的技能變更（例如修錯字）不被卡住
7. As a 維護者, I want 提醒只看即將提交的內容, so that 工作區裡未暫存的文件修改不會讓提醒誤以為文件已更新
8. As a 維護者, I want 只動文件或只動網站的提交不出現提醒, so that 提醒保持訊號價值
9. As a 維護者, I want 提醒在既有 pre-commit 流程中出現, so that 不必安裝或記得另一個 hook
10. As a 維護者, I want 每次推送到 master 都在 CI 跑完整快速檢查, so that 沒裝 hook 或用 `--no-verify` 繞過的提交也會被發現
11. As a 維護者, I want CI 也跑網站瀏覽器檢查, so that pre-commit 刻意不跑的瀏覽器檢查不會只靠我手動記得
12. As a 維護者, I want CI 使用與本機相同來源的 skill validator, so that 本機通過的檢查在 CI 上不會因 validator 不同而結果不同
13. As a 維護者, I want CI 的 validator 固定在指定的上游 commit, so that 上游變動不會讓 CI 無預警轉紅
14. As a 維護者, I want CI 缺 validator 時明確失敗, so that 延續「不略過檢查」的既有立場
15. As a 維護者, I want CI 失敗時能看到瀏覽器檢查的截圖與結果, so that 我不必在本機重現就能判斷問題
16. As a 維護者, I want 推送 annotated tag 就自動建立 GitHub Release, so that 不必手動執行建立 Release 的步驟
17. As a 維護者, I want tag 訊息直接成為 Release notes, so that 不需要另外維護 CHANGELOG 檔
18. As a 維護者, I want tag 訊息缺少「文件與網站」審視紀錄時 Release 不建立, so that 每次發布都留下文件是否跟上的明確揭露
19. As a 維護者, I want 審視紀錄可以寫「無需變更」加理由, so that 不需改文件的版本也能合法發布
20. As a 維護者, I want 輕量 tag（非 annotated）被拒絕, so that 不會出現沒有 notes 的 Release
21. As a 維護者, I want 範例頁標示的產生版本若不是已存在的 tag 就擋下發布, so that 範例頁不會宣稱由不存在的版本產生
22. As a 維護者, I want 範例頁標示舊版本仍可通過, so that 範例頁維持歷史成品定位，不必每次重做
23. As a 維護者, I want 發布檢查能在本機先執行, so that 推送 tag 前就能確認會不會失敗
24. As a 維護者, I want 發布檢查失敗時逐項列出原因, so that 一次修完而不是反覆推送 tag
25. As a 維護者, I want 發布步驟寫成文件, so that 不必靠記憶完成發布
26. As a 維護者, I want 發布文件說明如何修正推錯的 tag, so that 檢查失敗後知道怎麼重來
27. As an agent, I want AGENTS.md 指向發布文件, so that 被要求協助發布時知道流程與界線
28. As an agent, I want 明確知道自己不推送 tag, so that 不會在未經人確認時對使用者發布
29. As an agent, I want 能依文件起草 tag 訊息, so that 維護者只需審閱與推送
30. As a 透過 CLI 安裝的使用者, I want 我拿到的技能與網站和 README 描述一致, so that 照著文件使用不會遇到落差
31. As a 手動下載 Release 的使用者, I want 每個 Release 都有說明文件與網站狀態的 notes, so that 我知道這個版本的文件是否可信
32. As a 網站訪客, I want 網站持續反映 master 的現況, so that 看到的介紹與 CLI 安裝到的技能一致

## Implementation Decisions

- **ADR 0006 發布模型**：記錄 master 即發布管道、tag 為 changelog 檢查點、不設版本欄位、網站隨 master 部署。依據是 skills CLI 未指定 ref 時抓預設分支、以技能資料夾的 tree hash 判斷更新（已從 vercel-labs/skills 原始碼查證）。列出被否決的替代方案：README 改以固定 ref 安裝（會讓 `update` 失效）、另設 release 分支為預設分支（多一層分支管理）、網站只在 release 時部署（與 CLI 使用者實際拿到的版本脫節）。推翻條件寫成可檢查的形式，並以反引號標出依賴的檔案（README 的安裝段落所在檔、網站部署 workflow）。
- **檢查器維持單一入口**：所有新判斷都加在既有的檢查器命令列，不另立腳本。
- **staged 模式新增文件提醒**：判斷依據是 Git index 相對於 HEAD 的變更路徑。條件為「有路徑位於技能資料夾下，且沒有任何路徑是 README 或介紹頁」。輸出寫到 stderr，不影響結束碼。非 staged 模式不輸出此提醒（沒有「這次變更」的概念）。
- **新增發布模式，參數為 tag 名稱**：檢查項目逐項收集後一次回報，任一失敗以非零狀態結束。檢查項目：
  - tag 存在且為 annotated tag
  - tag 訊息中有一行以「文件與網站：」開頭且冒號後有內容
  - 網站範例頁中「由 answer-me vX.Y.Z 產生」標記的每個版本都是 repo 中已存在的 tag；範例頁的檢查以該 tag 指向的 commit 內容為準，而不是工作區
  - 該 commit 的快速檢查本身通過
- **CI 檢查 workflow**：在推送到 master 時觸發（不限路徑），步驟為取得 validator、安裝檢查依賴、執行快速檢查、執行網站瀏覽器檢查，並把瀏覽器檢查的輸出目錄上傳為 workflow artifact。Node 版本需符合瀏覽器檢查的 22+ 要求，瀏覽器使用 runner 內建的 Chrome。
- **validator 取得方式**：從 openai/codex repo 的 skill-creator 範例資料夾，以固定 commit SHA 下載 `quick_validate.py`（Apache-2.0；內容已確認與本機 Codex 安裝的版本一致，而 openai/skills 上的版本較舊）。以既有的 `SKILL_VALIDATOR` 環境變數指給檢查器。pin 的 SHA 寫在 workflow 中；本機與 CI 結果出現分歧時手動更新。
- **release workflow**：在推送符合 `v*` 的 tag 時觸發。執行發布模式檢查，通過後以 tag 訊息為 notes 建立 GitHub Release，標題沿用既有慣例「Answer Me vX.Y.Z」。需要 `contents: write` 權限。release workflow 不重跑瀏覽器檢查，以 master 的 CI 結果為準。
- **網站部署 workflow 不變**。
- **發布文件**：放在 docs 下，涵蓋發布模型摘要（連結 ADR，不重述取捨）、tag 訊息格式與「文件與網站」一行的寫法、本機先跑發布模式、推送 tag、檢查失敗後刪除並重推 tag 的步驟。`docs/checks.md` 補上新提醒與發布模式的說明。
- **AGENTS.md**：新增一節指向發布文件，並註明 agent 不推送 tag、不建立 Release，可起草 tag 訊息與執行檢查。

## Testing Decisions

- 好的測試只透過檢查器的命令列觀察外部行為：結束碼、stdout/stderr 是否包含特定訊息。不測內部函式。
- 沿用 `tests/test_checks.py` 的既有模式：在暫存 git repo 中建立檔案、stage 或建立 tag，再以 subprocess 呼叫檢查器。
- staged 提醒的情境：只動技能 → 有提醒且結束碼 0；技能加 README → 無提醒；技能加介紹頁 → 無提醒；只動文件 → 無提醒；技能變更只在工作區、未 stage → 無提醒；README 修改只在工作區、技能已 stage → 有提醒。
- 發布模式的情境：合法 annotated tag 通過；tag 不存在失敗；輕量 tag 失敗；缺「文件與網站」一行失敗；該行冒號後空白失敗；範例頁標記不存在的版本失敗；範例頁標記較舊但存在的版本通過；多項錯誤同時出現時全部列出；範例頁內容以 tag 的 commit 為準，工作區修改不影響結果。
- 兩個 workflow 沒有自身邏輯，不寫單元測試；驗收方式是推送到 master 一次確認 CI 綠燈並取得截圖 artifact，以及推送一個測試 tag 確認失敗與成功兩條路徑，之後刪除測試 tag 與 Release。

## Out of Scope

- 改用 PR 流程或設定 branch protection；CI 在 master 上是事後揭露。
- 自動判斷文件內容是否在語意上跟上技能變更；只做路徑層級的提醒與人工審視紀錄。
- 範例頁隨發布重新產生。
- 在技能或網站中顯示版本號，或新增版本欄位。
- 變更 skills CLI 的安裝方式或 README 的安裝指令。
- 開發者文件（檢查說明、演練說明、ADR、詞彙表）的同步把關；它們隨提交走，由 code review 處理。
- 自動同步本機與 CI 的 validator 版本。

## Further Notes

- 此規格源自一次 grilling，關鍵事實已查證：skills CLI 的抓取與更新行為（vercel-labs/skills 原始碼）、validator 上游位置與授權（openai/codex）、repo 沒有 PR 或 merge 紀錄。
- 範例頁目前標示 v0.1.3，該 tag 已存在，現狀可通過發布檢查。
- v0.1.3 之後已有 15 個提交未發布，包含網站改版；落地後的第一次發布可作為完整流程的實地驗收。
