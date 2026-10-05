# 發布步驟

以下命令皆從 repository 根目錄執行。檢查器的細節見[檢查與回歸演練](checks.md)。

## 發布模型

master 就是 skills CLI 使用者的發布管道，tag 與 GitHub Release 只是 changelog 檢查點，版本只以 tag 表示。為什麼這樣設計見 [ADR 0006](adr/0006-master-is-the-release-channel.md)。實際的後果是：文件要在變更進 master 之前就跟上，不能等到打 tag。

推送 `v*` tag 會觸發 `.github/workflows/release.yml`：先跑發布模式檢查，通過才以 tag 訊息為 notes 建立標題為 `Answer Me <tag>` 的 GitHub Release；檢查失敗則不建立。它不重跑瀏覽器檢查，以 master 上的 CI 結果為準。

## Tag 訊息格式

tag 必須是 annotated tag，訊息就是 Release notes，所以直接寫給讀者看：第一行是摘要，接著列出這個版本的變更。訊息中必須有一行以「文件與網站：」（全形冒號）開頭、冒號後有內容的紀錄，說明這次發布時 README、介紹頁與網站有沒有跟上技能的變更。兩種寫法：

```text
文件與網站：已審視 README 安裝段落與介紹頁，新增的輸出格式說明已補上
```

```text
文件與網站：無需變更（本版只修正內部檢查器，使用者可見行為不變）
```

「無需變更」後面的括號理由不可省略；只寫「已審視」時，要寫出審視了哪些文件。

## 發布步驟

1. 確認 master 上最近一次 CI 為綠燈，且工作區乾淨、位於要發布的 commit。
2. 把 tag 訊息寫進一個檔案，再以它建立 annotated tag：

   ```sh
   git tag -a v0.1.5 -F v0.1.5-tag.md --cleanup=whitespace
   ```

   `--cleanup=whitespace` 不可省略：git 預設會把 `#` 開頭的行當成註解刪除，不論訊息來自 `-m`、`-F` 或編輯器，Markdown 標題會因此從 Release notes 消失。訊息檔放在 repository 之外，或用完即刪，不要提交。

3. 推送前在本機執行發布模式，有錯會一次全部列出：

   ```sh
   python3 scripts/check.py --release v0.1.5
   ```

4. 通過後推送 tag，workflow 隨即建立 Release：

   ```sh
   git push origin v0.1.5
   ```

## 檢查失敗後重來

Release 不會在檢查失敗時建立，但 tag 已在遠端。修正後必須刪除舊 tag 再重建。若 workflow 已建立了 Release，先在 GitHub 刪除該 Release 再刪 tag，避免留下指向舊 commit 的 Release。只有 repository 啟用 immutable releases 時，已發布 Release 的 tag 才會被鎖定、無法刪除或移動，那種情況下只能改發新版本號；未啟用時 tag 仍可刪除重建：

```sh
git push origin --delete v0.1.5
git tag -d v0.1.5
```

修正問題（補上訊息、或將修正提交到 master）後，從「建立 annotated tag」重新開始。

## Agent 的界線

agent 可以依本文件起草 tag 訊息並執行發布模式檢查，但不推送 tag、不建立 Release；這兩步由維護者自行執行。
