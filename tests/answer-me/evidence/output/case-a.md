# Ticket API 的一次讀取

這裡的「get ticket」是 `TicketService.handle_get(ticket_id)`，它回傳 `(狀態碼, 內容)`；材料沒有展示 HTTP server 或路由。對第一次讀取 `T1`（且 repo 有資料）而言，流程是：

```text
handle_get("T1")
  → get_ticket("T1")
  → cache 沒有 T1
  → repo.find("T1")（reads 加 1）
  → 複製 row 為 dict，放入 cache["T1"]
  → 回傳 (200, 該 dict)
```

依據：[service.py 第 9–11、18–29 行](../input/ticket_api/service.py)。同一個 `TicketService` 再讀 `T1` 時，會直接回傳 cache 中的 dict，不再呼叫 repo；測試用兩次 `handle_get` 後 `repo.reads == 1` 表達這個預期。[service.py 第 18–20 行](../input/ticket_api/service.py)、[test_service.py 第 5–10 行](../input/ticket_api/test_service.py)。快取綁在 service 物件上；README 稱它是「process-local」，所以不能據此推定跨程序共用。[README 第 3 行](../input/ticket_api/README.md)。

若 repo 找不到 ticket，`find` 回傳 `None`，`get_ticket` 丟出 `NotFound`；`handle_get` 捕捉後回傳 `(404, {"error": "not found"})`。這條路沒有寫入 cache，因此下次查同一個不存在的 ID 仍會查 repo。[service.py 第 21–31 行](../input/ticket_api/service.py)。

**快取過期有文件與程式的落差。** README 寫「60 秒後過期」，但目前 `get_ticket` 沒有時間戳、計時器或過期判斷；只要同一個 service 物件持續存在，已快取項目就會持續命中。新建 service 物件會建立空 cache。現有測試也沒有驗證 60 秒過期。[README 第 3 行](../input/ticket_api/README.md)、[service.py 第 13–25 行](../input/ticket_api/service.py)、[test_service.py](../input/ticket_api/test_service.py)。
