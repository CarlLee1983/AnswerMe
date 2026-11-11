# 借鑑 Understand Anything

日期：2026-11-11。使用者要求借鑑 Egonex-AI/Understand-Anything，強化跨檔案、跨模組的程式理解，同時維持 Answer Me 的輕量、跨 agent 與證據核心。

## 研究範圍

以 [commit 532a2e9](https://github.com/Egonex-AI/Understand-Anything/tree/532a2e97dc007104f9a1b8d11b6cc16ae7c8cd3a)（MIT）固定範圍，在暫存目錄 clone 後只讀原始碼與 agent 提示，沒有安裝或執行。讀到的實作事實：

- tree-sitter（WASM）抽出函式、類別、import 與同檔 callGraph（`packages/core/src/plugins/tree-sitter-plugin.ts`）；跨檔的 `calls` 邊由 file-analyzer LLM「依 import 與函式名稱推斷」（`agents/file-analyzer.md`），weight 固定 0.8，沒有證據或信心欄位。
- 業務流程（domain → flow → step）由 LLM 產生（`agents/domain-analyzer.md`）。
- Guided Tour：拓撲腳本算 fan-in／fan-out 與入口 BFS，LLM 決定 5–15 步的順序（`agents/tour-builder.md`）；另有 Kahn 排序的確定性備案。
- Diff impact：檔案以 `filePath` 完全相等對到節點，展開一層 `contains`，取不分方向、不分邊類型的一跳鄰居（`src/diff-analyzer.ts:22-88`）。
- 過期判斷：`gitCommitHash` 對 HEAD（`packages/core/src/staleness.ts`）；增量更新用 `.ua/fingerprints.json` 的 SHA-256 與結構簽名分級。圖本身不含檔案雜湊。
- 對外：唯讀 stdio MCP server（6 個工具）、slash skills，或直接讀 `.ua/knowledge-graph.json`。需要 Node 22+、pnpm，以及 agent 平台派 LLM 子代理。

## 逐項判斷

| 能力 | Answer Me 現況 | 判斷 | 做法 |
| --- | --- | --- | --- |
| 沿流程追到實際程式 | 有一句原則 | 可輕量補強 | `references/code-tracing.md`：起點／終點、逐跳附位置、間接呼叫找註冊處、停止點 |
| 區分結構／執行／業務／推論關係 | 圖解有「推論以虛線區分」 | 可輕量補強 | 四種關係的依據與對應形式 |
| Guided Tour | 無 | 借概念、不建引擎 | 「入口 → 核心邏輯 → 資料存取 → 外部依賴 → 例外處理」的導覽順序 |
| Diff impact | 有驗證狀態、範圍外改動、差異圖 | 可輕量補強 | 已確認變更／靜態潛在影響（附深度）／需執行確認三層；其一跳演算法不分方向，不照搬 |
| 圖解規模控制 | 已有約 9 節點上限 | 已具備 | 沿用樣式指引 |
| 證據與驗證狀態 | 已具備 | 無須變更 | 沿用 |
| 過期判斷 | 無圖可判 | 透過可選工具 | `scripts/ua_graph.py check`：commit 對 HEAD、未提交變更、列出變更路徑 |
| 讀取既有知識圖 | 無 | 可選 adapter | 同一腳本的 `find`、`neighbors`，結果附 `[changed since graph]`／`[missing now]` 並提醒回原始碼確認 |
| tree-sitter 解析、多代理建圖、增量 fingerprint | — | 不導入 | 需 Node 建置、LLM 管線與長期維護，違背輕量與跨 agent |
| MCP server、dashboard、domain graph | — | 不導入 | 已有其專案提供；離線 HTML 不依賴圖的檢視器 |

決策記錄見 [ADR 0007](../../docs/adr/0007-knowledge-graph-as-lead-index.md)。

## 演練

素材：`tests/answer-me/flow/input/`（13 檔訂單服務、`coupon-threshold.diff`、含一條錯誤 `calls` 邊的圖、讓圖過期的改名 diff），以及 Understand Anything repo 本身（528 個追蹤檔，附其 dashboard 範例圖，建於 `58cfb20`，對 HEAD 落後 378 個路徑）。每次由獨立子代理執行，只拿到技能、題目與素材副本；改動前的技能以 `git archive HEAD` 取得。token 數為子代理回報的 `subagent_tokens`，單次樣本，含讀技能本身的成本。

| 情境 | 改動前 | 改動後 | 觀察 |
| --- | --- | --- | --- |
| S1 單一函式 | 57.2k、讀 3 檔 | 57.4k、讀 3 檔 | 改動後未載入跨檔指引，未追呼叫者；成本相同 |
| S2 跨模組流程 | 61.3k | 65.1k | 兩者都正確。改動後多標出「`POST /orders` 對到 `post_order` 是推論，repo 無路由註冊」與停止點；收據一跳寫成經註冊 |
| S3 diff 影響 | 62.3k | 66.9k | 兩者都找出 `monthly_revenue` 重算、無折扣碼測試、agent 說法被反駁。改動後以深度欄區分直接與傳遞影響，並說明排除 `validation.py`；改動前把路由與收據也稱為「呼叫者」 |
| S8 大型 repo | 68.4k、8 次工具 | 74.8k、13 次（第二輪附過時圖 77.9k） | 兩者都正確。改動後行號精確（改動前自承 `:111` 是估計值，實際 `:131-139`），並指出工具描述寫 downstream、程式實際不分方向 |
| S4 新鮮圖 | — | 第一輪未偵測 `.ua/`；修正指引後第二輪執行 `check`（fresh） | 兩輪都沒有把錯誤的 `post_order → send_receipt` 當直接呼叫；但也沒查圖的邊，圖未提供額外上下文 |
| S6 過時圖 | — | 第一輪 `--root` 指錯得到 `missing` 並退回；修正後第二輪 `stale`，`neighbors` 標出 `reports.py [missing now]` | 引用 `analytics.revenue_for`，並在解說中說明圖與原始碼的差異 |
| S7 離線 HTML | — | 99.4k | 主 agent 以 `verify-site.mjs` 複查：離線、零請求、零執行錯誤、1200／390 px 無頁面溢出 |

結論：

- 在兩份素材上，改動後的追蹤更可追溯（深度、推論標示、停止點、行號精確），正確性與改動前相當；跨檔情境多花約 6–14% token，單一函式情境不變。樣本各一次，不足以宣稱穩定的成本或品質差異。
- 知識圖在這些樣本中沒有幫助定位：小 repo 直接讀更快，大 repo 的範例圖已過時。實際價值是防護：過時時把消失的位置標為 `[missing now]`，避免引用。新鮮且大型的圖能否省下搜尋成本，未量測。
- 腳本輸出比整份圖小得多（真實圖 101,755 bytes；`find diff` 輸出 462 bytes），但這是 bytes，不是 token 量測。

## 自動化檢查

- `python3 -m unittest tests/test_ua_graph.py`：25 tests OK，系統 Python 3.9.6 亦通過（缺檔、格式錯誤、惡意欄位、版本不相容、fresh／dirty／stale／unknown、懸空邊、子目錄根目錄、截斷、輸出跳脫、根目錄外路徑、不改寫 `.git/index`）。程式碼審查的 2 項 HIGH、6 項 MEDIUM 與 5 項 LOW 已修正並各有測試，檔案大小上限未做。
- `python3 scripts/check.py`：PASS。
- `python3 -m unittest discover -s tests -p 'test_checks.py'`：49 tests OK。`node tests/answer-me/browser/verify.mjs`：exit 0。`git diff --check`：通過。

## 限制

- S7 成品在 390 px 時頁面未溢出，但時序圖在自己的容器內被截在右側，需要橫向捲動才能看完；這是該次產出的品質問題，未改動模板。
- 未重跑 `evidence`、`conditions` 等既有演練；技能只新增一段指向跨檔指引的文字，單一函式樣本顯示未觸發，但不能證明所有既有情境不受影響。
- 腳本假設 `--root` 是被分析的目錄；圖的 `filePath` 若是其他基準，旗標會不準。
- 第二輪演練後，指引又做了三處措辭修正（任何狀態都只當線索、`unknown` 時位置一律未確認、搜尋時排除 `.ua/`），這三處沒有再跑演練。
