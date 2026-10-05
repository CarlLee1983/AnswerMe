# 檢查與回歸演練

以下命令皆從 repository 根目錄執行。專案用途與使用範例見 [README](../README.md)。

## 快速檢查

需求：Python 3.10+、PyYAML，以及已安裝的 `skill-creator/scripts/quick_validate.py`。

```sh
python3 -m venv "$HOME/.cache/answer-me/check-env"
"$HOME/.cache/answer-me/check-env/bin/python" -m pip install -r requirements-check.txt
"$HOME/.cache/answer-me/check-env/bin/python" scripts/check.py
```

若目前 Python 已有 PyYAML，可直接執行 `python3 scripts/check.py`；建立環境只是缺少依賴時的一次性準備。

檢查器優先使用 `SKILL_VALIDATOR` 指定的檔案，否則使用 `${CODEX_HOME:-~/.codex}/skills/.system/skill-creator/scripts/quick_validate.py`。沒有 validator 或 PyYAML 時會失敗並提示設定，不略過檢查。這沿用 Codex 安裝中的驗證器；乾淨 checkout 仍須先準備上述檢查依賴，沒有將其複製進技能。

快速檢查涵蓋 skill frontmatter、`agents/openai.yaml` 必要顯示欄位，以及專案文件的行內相對檔案連結。外部網址、絕對路徑、頁內 anchor 及歷史演練產物中的來源連結不在連結檢查範圍；它不驗證解說語意或使用者理解。

若 repository 根目錄有 `site/`，檢查器也會靜態掃描其中的檔案：不得含 `file://` 或 `/Users/`、`/home/` 形式的本機路徑；HTML 的 `href` / `src` 站內相對連結必須指向存在的檔案；範例頁（`site/index.html` 以外的 `.html`）不得以 `script`、`link`、`img`、`iframe` 等標記或 CSS 的 `url()` / `@import` 載入 http(s) 資源，介紹頁 `site/index.html` 只例外允許 `fonts.googleapis.com` 與 `fonts.gstatic.com`。站內連結必須留在 `site/` 內（只有該目錄會部署），指向目錄時該目錄需有 `index.html`，以 `/` 開頭的根絕對連結會被拒絕，因為專案網站部署在 `/AnswerMe/` 之下。介紹頁的例外只適用於 `<link>`。CSS 的 `url()` / `@import` 掃描只涵蓋 HTML 內嵌的 `<style>` 與 `style` 屬性，網站頁面是單檔，不含獨立 CSS。一般 `<a href>` 的外部網址不受限；這只是靜態掃描，不執行頁面，也不驗證內容語意。

## 提交檢查

```sh
sh scripts/install-hooks.sh
```

安裝器只設定本 repository 的 `core.hooksPath`，遇到既有 hooks 路徑或啟用的 hooks 會保留並停止。pre-commit 呼叫同一檢查器的 `--staged` 模式：從 Git index 建立暫存快照，檢查即將提交的內容，避免未暫存的修正掩蓋待提交錯誤。

`--staged` 另外會在 stderr 印出一行文件提醒：Git index 相對於 HEAD 的變更路徑中，有路徑位於 `skills/answer-me/` 下，且沒有任何路徑是 `README.md` 或 `site/index.html`。判斷只看 index，未暫存的修改不影響；尚無 HEAD 的初始提交則所有 staged 路徑都算變更。提醒只是提示，絕不阻擋提交，也不改變結束碼；非 `--staged` 模式不輸出。它只在路徑層級判斷，不檢查文件內容是否跟上。

Hook 預設使用 `.venv/bin/python`（若存在），否則 `python3`；可用 `ANSWERME_PYTHON` 指定已備妥依賴的 Python，例如 `export ANSWERME_PYTHON="$HOME/.cache/answer-me/check-env/bin/python"`。若本次是首次安裝，移除設定可停用：`git config --local --unset core.hooksPath`。未來 checkout 須執行安裝命令；Git 不會自動啟用版本庫內的 hooks。

## 發布檢查

推送 tag 前，在本機以 tag 名稱執行發布模式（需先建立 annotated tag）：

```sh
python3 scripts/check.py --release v0.1.4
```

檢查項目逐項收集，有錯一次全部列到 stderr 並以非零狀態結束，通過時以零結束：

- tag 存在且為 annotated tag（輕量 tag 沒有訊息可作為 Release notes）。
- tag 訊息中有一行以「文件與網站：」（全形冒號）開頭，且冒號後有內容。
- 範例頁（`site/` 下 `index.html` 以外的 `.html`）中每個「由 answer-me vX.Y.Z 產生」標記的版本，都是 repository 中已存在的 tag；較舊但存在的版本通過。
- tag 指向的 commit 通過上述快速檢查。

範例頁與快速檢查都以暫時 index 取出的 tag commit 內容為準（與 `--staged` 共用同一個快照程式），工作區的修改不影響結果。`--release` 與 `--staged` 不能併用。

## 行為與瀏覽器驗證

技能行為有變更時，依[演練說明](../tests/answer-me/README.md)用原始材料重新產出答案，再檢查語意及 HTML。已保存的範例可驗證瀏覽器檢查程式與既有成果，不能證明更新後的技能仍會產生相同品質。

預設 HTML 模板變更時，執行 `node tests/answer-me/browser/verify-templates.mjs`，並檢視輸出的桌面、手機與列印截圖。它驗證模板的離線呈現、簡報導覽與降級閱讀；樣式選擇規則變更時，另依演練說明的 Default HTML style evaluations 重新產生成品。

重跑已保存 HTML 的瀏覽器檢查：

```sh
node tests/answer-me/browser/verify.mjs
```

需要 Node.js 22+ 與 Google Chrome 或 Chromium；非標準安裝位置可透過 `CHROME_BIN` 指定瀏覽器執行檔。檢查使用 `file://` 與離線模式，將新截圖和 JSON 結果寫入新的暫存目錄，並印出路徑。情境範圍與自訂輸出目錄的參數見[演練說明](../tests/answer-me/README.md)。

網站（`site/`）變更時，手動檢查所有頁面並檢視輸出的桌面與手機截圖：

```sh
node tests/answer-me/browser/verify-site.mjs [siteRoot] [artifactDir]
```

檢查以 `file://` 與離線模式開啟 `site/` 下每個 `.html`（找不到任何頁面視為失敗），斷言沒有執行期例外、桌面（1200 px）與手機（390 px）寬度皆無水平溢出。範例頁不得有任何 http(s) 請求，介紹頁 `site/index.html` 只允許 `fonts.googleapis.com` 與 `fonts.gstatic.com`；載入後會先等 2 秒，讓延遲發出的請求被記錄，若有互動則在互動後再等 2 秒。自動操作的控制項只有 `input[type=range]`、`input[type=number]` 與 `select`：頁面若有，會把第一個控制項改成另一個合法值，並在最多 2 秒內輪詢頁面文字是否改變；按鈕驅動的互動（例如簡報換頁）仍須人工檢查。

單頁的例外（載入失敗、CDP 逾時等）記為該頁的失敗，不會中斷其餘頁面；所有頁面的失敗都收集到 `results.json`，任一失敗則以非零狀態結束。截圖與 `results.json` 寫入新的暫存目錄並印出路徑，不寫入 repository。與其他瀏覽器檢查相同，需要 Node.js 22+ 與 Chrome 或 Chromium（可用 `CHROME_BIN` 指定），不接 pre-commit。它不驗證內容語意。檢查程式本身的測試：

```sh
node --test tests/answer-me/browser/verify-site.test.mjs
```

檢查器或 hook 改動時，執行：

```sh
python3 -m unittest discover -s tests -p 'test_checks.py'
```
