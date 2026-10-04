# 回顧改善與驗證

日期：2026-10-04。依使用者「依建議改善」完成；原始基準為 `2450aa6`。改善與驗證階段未建立 commit，後續提交依使用者另行授權。

## 變更與依據

| 回顧發現 | 改善位置 | 可觀察結果 |
| --- | --- | --- |
| 演練材料只在 `/tmp` | [tests/answer-me](../../tests/answer-me/README.md) | 保存合成輸入、代表輸出與原 JSON；瀏覽器路徑可設定，結果另存，跨目錄可執行。 |
| 沒有自動檢查入口 | [scripts/check.py](../../scripts/check.py)、[pre-commit](../../.githooks/pre-commit)、[checks](../../docs/checks.md) | 技能結構、顯示 YAML、文件行內相對檔案連結有統一入口；提交檢查讀取 index 快照。 |
| 決策之間多一次續行回覆 | 安裝中的 `/Users/carl/.agents/skills/wayfinder/SKILL.md` | 整張地圖請求會接續下一張票的實質問題；保留 HITL、單票、暫停及完成的範圍邊界。 |
| 過大的指令檔／配置搜尋 | 本次工具參數 | 只讀目前目錄及祖先的指令檔、需要的配置欄位與角色；沿用既有 scout 發現，沒有新增全域規則。 |

## 專案驗證

環境：Python 3.14.7、PyYAML 6.0.3、Node 24.21.0、Chrome 154.0.8037.93。檢查依賴沒有重新安裝。

- 快速檢查通過。既有 `answer-me` 技能內容未改，保留原行為驗證結果。
- 10 個 guardrail 回歸測試通過：有效／無效 metadata、缺失 validator、壞連結、兩種部分暫存方向、未追蹤目標、hook 執行與既有 hook 保存。
- 從包含空白的新路徑建立獨立 Git 副本，依序執行工作目錄檢查、暫存區檢查、10 個測試、hook 安裝與執行、離線瀏覽器檢查，全部通過；沒有對原專案暫存或提交。[原始命令與結果](integration-results.json)
- 瀏覽器檢查涵蓋 10 組數值、4 個情境按鈕、鍵盤、390 px 版面、修復頁四組數值；最終頁面沒有 HTTP(S) 請求或 runtime error。破損輸入仍被辨識。另在拷貝的樣本改壞公式，檢查以非零狀態失敗。[本次瀏覽器結果](browser-results.json)
- 獨立 reviewer 核對程式及技能差異，沒有重大發現。新啟動的只讀 agent 經 `AGENTS.md` 找到檢查文件、相對連結與瀏覽器命令，正確區分保存範例和新技能行為的驗證。
- 已在本專案設定 `core.hooksPath=.githooks`。原本沒有啟用的 Git hooks；安裝器會拒絕覆蓋其他設定。新 checkout 仍須執行安裝命令。

## Wayfinder 校準

只改三處續行指引；不更動全域 `AGENTS.md`、Codex hooks、模型或權限設定。獨立 agent 使用三份隔離材料，實際結果為：

1. 整張地圖：記錄第一票，claim 下一票，直接提出排序問題，沒有替使用者回答。
2. 指定單票：只解決指定票，下一票仍為 open。
3. 地圖完成：完成記錄後交接，沒有實作程式。

本機 validator 不接受 wayfinder **原本就有**的 `disable-model-invocation` 欄位。直接驗證回報此相容性限制；在暫存副本移除該欄位後，其餘 frontmatter 與本文驗證通過，並另外確認安裝版本的欄位仍為 `true`。未為通過 validator 改變呼叫方式。

校準證據：`/Users/carl/.codex/calibration/evidence/wayfinder-continuation-20261004.json`。原檔備份：`/Users/carl/.codex/backups/wayfinder-continuation-20261004-bsw8zm8k/SKILL.md`。安裝版本 SHA-256：`03dbef3b674fb5f412a793b46a2c3dfc1b188ca2de8f1d017bae38ac37bf4502`。

## 限制與回復

保存的 HTML 重跑驗證的是這組成果與 harness；技能行為變更時仍須依 README 重新生成、核對語意。快速檢查需要已安裝的 skill-creator validator 及 PyYAML，缺少時會報錯；沒有把外部依賴缺失當作通過。這些檢查不證明使用者理解或所有瀏覽器相容。

停用本次首次安裝的 hook：`git config --local --unset core.hooksPath`。Wayfinder 可比對上述備份，反向套用本次三處修改並保留後續編輯；詳見 `~/.codex/calibration/ledger.md`。專案檔案變更仍可供檢視；既有未追蹤 `.gitignore`、`.ignore` 保留原狀。
