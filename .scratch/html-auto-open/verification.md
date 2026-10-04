# HTML 完成後自動開啟

- 日期：2026-10-04。
- 需求與證據：使用者在上一份 HTML 交付後自行執行 `open`，並要求本專案完成 HTML 時自動開啟。
- 控制位置：只在 [SKILL.md](../../skills/answer-me/SKILL.md) 的交付步驟定義行為。README 說明使用方式；演練 README 記錄驗收條件。未新增 hook，也未修改全域設定或 npx 管理的安裝副本。
- 行為：驗證後在本機桌面開啟最終 HTML 一次；macOS 使用安全引用絕對路徑的 `open`。保留不要開啟、無桌面、工具不可用與命令失敗的交付路徑，並區分開啟請求成功與呈現驗證。
- 快速檢查：`python3 scripts/check.py` 通過；`git diff --check` 通過。
- 新演練：獨立 agent 只收到更新的技能、原始 model.md 與 HTML 情境，重新製作 [HTML](evaluation/model%20explanation.html)。[交付紀錄](evaluation/delivery.md) 記載離線 file:// 渲染無遠端請求或執行錯誤，先檢視截圖，再執行一次安全引用含空白路徑的 `open`，結束碼 0。主 agent 已讀取成果與紀錄，實際檢視 [截圖](evaluation/render.png)，核對新增的交付行為。
- 驗證範圍：本次前向演練只驗收 macOS HTML 自動開啟流程，並非全部技能語意情境的回歸認證。不要開啟、無桌面與命令失敗分支已做文字核對，尚未逐一執行。未改檢查器或 hook，未重跑其單元測試或歷史互動頁。
- 回復方式：移除 SKILL.md 新增的自動開啟段落，回復對應 README 說明與演練表格變更；無全域設定需要還原。
