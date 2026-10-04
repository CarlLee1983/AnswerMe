# 這次修改與證據

`change.diff` 在 `repo.find(ticket_id)` 後加入 `row is None` 的分支，遇到查無資料時丟出 `NotFound(ticket_id)`。目前的 `service.py` 已包含這段；`handle_get` 會把該例外轉成 `(404, {"error": "not found"})`。[change.diff](../input/change.diff)、[service.py 第 18–31 行](../input/ticket_api/service.py)。

這個分支的理由可從程式推得：若 `row` 是 `None` 而繼續執行 `dict(row)`，會產生型別錯誤，無法走到預定的 404 回應。加入分支後，查無資料會走明確的 404 路徑；有資料時的快取路徑沒有在 diff 中改動。這是從 diff 和目前程式推得的前後行為，不是提供的紀錄中實測的舊版本結果。[change.diff](../input/change.diff)、[service.py 第 21–31 行](../input/ticket_api/service.py)。

測試紀錄只顯示執行 `python3 -m unittest -v test_service.TicketTests.test_missing`，結果為 **1 個測試通過**。目前測試檔另有 `test_repeat_hit`，但這份紀錄沒有顯示它被執行。[test-output.txt](../input/test-output.txt)、[test_service.py 第 5–14 行](../input/ticket_api/test_service.py)。我依要求沒有重跑測試。

`agent-report.md` 的「all tests passed」超過這份紀錄能證明的範圍；「fixes missing tickets in production」也沒有部署或正式環境證據。修改沒有碰並行控制，材料裡也沒有並行安全測試，故無法確認其「safe」判斷。README 宣稱 60 秒 TTL，但程式沒有過期邏輯，測試紀錄也沒有 TTL 測試，故「TTL is verified at 60 seconds」沒有依據。[agent-report.md](../input/agent-report.md)、[test-output.txt](../input/test-output.txt)、[README 第 3 行](../input/ticket_api/README.md)、[service.py 第 13–25 行](../input/ticket_api/service.py)。
