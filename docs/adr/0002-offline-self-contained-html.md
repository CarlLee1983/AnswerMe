---
status: accepted
---

# HTML 成果須單檔離線可讀與可操作

HTML 交付是可保存、以 `file://` 直接開啟的檔案，CSS、JavaScript、SVG 與資料全部內嵌；不依賴 CDN、執行期網路請求、套件安裝或本機伺服器。引入圖表函式庫或開發伺服器看似更省事，但使用者要能保存、轉寄並在無網路時閱讀與操作。唯一例外是預設模板的 Google Fonts：只增強外觀，載入失敗時退回本機字型。決策過程見 `.scratch/karpathy-concept-skill/issues/04-media-scope.md`。

**Falsified if:** `skills/answer-me/SKILL.md` 或 `skills/answer-me/references/html-style.md` 允許成果依賴遠端腳本或伺服器，或 `tests/answer-me/browser/verify.mjs` 不再在離線模式下斷言零 HTTP(S) 請求。
