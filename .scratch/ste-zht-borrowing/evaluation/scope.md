這次變更做到了「回傳副本」，但同時改了 404 回應內容，違反了「API 回應不變」的要求。現有測試輸出也是失敗的：3 個測試中 `test_missing` 沒過。所以 agent 報告裡「All tests pass」這句話與測試紀錄矛盾，不能當成已驗證。

一個前提要先說明：`ticket_api/service.py` 和 `test_service.py` 的內容都還是變更前的版本，裡面仍是 `return self.cache[ticket_id]` 和 `{"error": "not found"}`。下面講變更後的行為時，依據都是 `change.diff` 和 `test-output.txt`，不是 `ticket_api/` 裡的檔案。

## 變更做了什麼

| 項目 | 變更前（`ticket_api/service.py`） | 變更後（`change.diff`） | 是否在要求範圍內 |
| --- | --- | --- | --- |
| 快取命中時的回傳值 | `return self.cache[ticket_id]`（第 20 行），回傳的就是快取裡那個 dict | `return dict(self.cache[ticket_id])`（diff 第 9 行），回傳一份新的 dict | 是 |
| 快取未命中時的回傳值 | `return self.cache[ticket_id]`（第 25 行） | `return dict(self.cache[ticket_id])`（diff 第 15 行） | 是 |
| 404 回應內容 | `{"error": "not found"}`（第 31 行） | `{"error": "ticket not found", "id": ticket_id}`（diff 第 22 行） | 否，超出範圍 |
| 測試 | `test_repeat_hit`、`test_missing` | 新增 `test_returns_copy`（diff 第 30–34 行） | 是 |

`request.md` 第 3 行要求的是：「Make it return a copy. Keep the API responses unchanged.」前兩列是對這個要求的實作。第三列是 agent 自己加的。它在報告裡寫「While there, I made the 404 body clearer」，說明這是順手做的改動，不是需求要的。

## 超出範圍的 404 改動

這項改動改的是 `handle_get` 對外的回應內容，直接牴觸「Keep the API responses unchanged」。後果有測試紀錄可查：`test_missing` 仍期待 `(404, {"error": "not found"})`，實際拿到的是 `(404, {'error': 'ticket not found', 'id': 'missing'})`（`test-output.txt` 第 13 行）。

要不要保留由你決定。如果保留，就等於要改 API 契約，`test_missing` 也要跟著改，呼叫端可能也要調整。如果撤回，只要把 diff 第 22 行還原，測試應該就會回到可以通過的狀態。不過撤回後的結果目前沒有執行紀錄可以證實，這只是推論。

## 各項說法的證據狀態

| 說法（來源） | 狀態 | 依據 |
| --- | --- | --- |
| 命中與未命中兩條路徑都改成回傳副本（agent 報告） | 程式內容已確認，執行行為部分驗證 | diff 第 9、15 行確實這樣寫。`test_returns_copy` 通過（`test-output.txt` 第 4 行），涵蓋「第一次取得（未命中）後修改，第二次取得（命中）仍是原值」這個情境 |
| 快取仍然有效，不會重複讀 repo | 已驗證 | `test_repeat_hit` 通過（第 3 行），它斷言 `repo.reads == 1` |
| 「All tests pass」（agent 報告） | 失敗 | `test-output.txt` 第 2 行 `test_missing ... FAIL`，第 25 行 `FAILED (failures=1)` |
| 「lint is clean」（agent 報告） | 未確認 | 提供的材料裡沒有 lint 的命令或輸出。要確認得看實際的 lint 執行紀錄 |
| API 整合測試 | 未驗證 | agent 自己說明沒有執行，原因是本機沒有 server 可用 |
| API 回應不變（需求） | 失敗 | 404 回應內容已改變，見上一節 |

## 兩個要留意的限制

第一，`dict(...)` 只做淺層複製（shallow copy），這是依 Python 語意做的推論，沒有執行紀錄。如果 ticket 裡有巢狀的 list 或 dict，呼叫端修改內層物件時，快取裡的資料仍會一起被改到。`test_returns_copy` 只改了最外層的 `title` 字串，沒有涵蓋巢狀的情況。目前的範例資料也只有 `{"title": "hello"}`，所以材料無法判斷實際資料會不會有巢狀欄位。

第二，文件和程式說法不一致。`ticket_api/README.md` 第 3 行寫快取「expire after 60 seconds」，但 `service.py` 的 `TicketService` 只有一個普通的 `self.cache = {}`，看不到任何過期邏輯。這和這次變更無關，但讀 README 時不要以為快取真的會過期。

如果你想自己檢查理解程度，可以想一個問題：撤回 404 改動、只保留兩行 `dict(...)` 之後，哪些需求可以算已驗證，哪些還需要補證據？（提示：去看淺層複製和 lint 那兩項。）

需要的話，我可以再畫一張 `get_ticket` 命中和未命中兩條路徑的前後差異圖，或者做一個巢狀資料的示意例子來說明淺層複製的邊界。
