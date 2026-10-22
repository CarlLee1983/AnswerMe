我把三件事分開回答。ticket 讀取流程與變更審視都有材料可依。cross-process lock 那一題沒辦法回答，因為材料裡沒有 `design-note.md`。HTTP 404 的定義放在最後。以下依你選的方式直接在對話中回答。

---

## 一、`ticket_api` 的 ticket 讀取流程

一句話：`handle_get` 呼叫 `get_ticket`。`get_ticket` 先查 process 內的 `cache`；沒命中才到 repo 讀，讀到的資料複製一份放進 `cache` 後回傳。找不到時丟出 `NotFound`，再由 `handle_get` 轉成 404。

```
handle_get(ticket_id)                         service.py:27-31
   │
   ▼
get_ticket(ticket_id)                         service.py:18
   │
   ├─ ticket_id 在 self.cache？ ──是──▶ 回傳快取值        service.py:19-20
   │        否
   ▼
repo.find(ticket_id)（repo.reads += 1）       service.py:21, 9-11
   │
   ├─ row is None ──▶ raise NotFound ──▶ handle_get 捕捉 ──▶ (404, {"error": "not found"})
   │                  service.py:22-23        service.py:30-31
   ▼
self.cache[ticket_id] = dict(row)            service.py:24
   │
   ▼
回傳 ──▶ handle_get 回 (200, ticket)          service.py:25, 29
```

圖中每個節點都直接對應到程式行，沒有推論出來的元件。

有三個細節會影響判斷：

- **cache 只存在記憶體裡，也不會過期。** `self.cache` 是一般的 `dict`（service.py:16），程式裡沒有任何時間戳或 TTL 邏輯。README 寫「Cached values expire after 60 seconds」（README.md:3），和程式對不上。照程式內容讀，快取寫入後就永遠不會失效。
- **找不到的結果不會進 cache。** `NotFound` 在寫入 cache（service.py:24）之前就丟出（service.py:23），所以同一個不存在的 ID 每次都會再讀一次 repo。
- **測試核對了快取命中。** `test_repeat_hit` 對 `T1` 讀兩次，再斷言 `repo.reads == 1`（test_service.py:5-10）。這個測試寫的是預期行為，但沒有證據顯示這次執行過它（見下一節）。

## 二、審視 `change.diff`、`test-output.txt`、`agent-report.md`

**這次變更做了什麼：** 在 `repo.find` 之後、寫入 cache 之前，加上 `if row is None: raise NotFound(ticket_id)`（change.diff:9-10）。目前的 service.py:22-23 已經是加上之後的版本。

**改了什麼行為（我的推論，沒有執行紀錄可證）：** 改之前，`row` 是 `None` 時會跑到 `dict(None)`，Python 會丟出 `TypeError`。`handle_get` 只捕捉 `NotFound`，所以這個錯誤會往外拋，不會變成 404。至於最後呈現成什麼回應，要看外層框架，材料裡沒有寫。改之後，找不到 ticket 會穩定回 `(404, {"error": "not found"})`。

**範圍：** 材料裡沒有原始需求，所以我沒辦法逐項比對需求，也沒辦法判斷有沒有超出範圍的改動。就 diff 本身看，它只動了 `get_ticket` 這兩行。另外，hunk header 寫的是 `-17,8 +17,11`，但實際上只多了 2 行。這個 diff 可能被裁剪或手動改過，不過不影響上面的解讀。

**逐項核對 agent 的說法：**

| agent-report 的說法 | 狀態 | 依據 |
| --- | --- | --- |
| 「added an explicit missing-ticket branch」 | 內容屬實（讀 diff 確認） | change.diff:9-10 |
| 「all tests passed」 | **未確認** | test-output.txt:1 只跑了 `test_service.TicketTests.test_missing` 一個測試，結果 `OK`。`test_repeat_hit` 沒有執行紀錄。確認方法是在 `ticket_api/` 執行 `python3 -m unittest -v` 跑完整套（README.md:4）。 |
| 「fixes missing tickets in production」 | **未驗證** | 唯一的執行證據是用 `FakeRepo` 跑的單元測試，沒有任何 production 或真實 repo 的紀錄。 |
| 「Concurrency behavior is unchanged and safe」 | **未驗證** | 沒有任何並行測試或執行紀錄。程式的 `cache` 是沒有加鎖的一般 `dict`。至於「safe」，材料裡沒有任何依據。 |
| 「cache TTL is verified at 60 seconds」 | **和程式矛盾** | 程式沒有 TTL 機制（service.py:13-25），只有 README 的文字提到 60 秒。測試也沒有任何和時間相關的案例。 |

**目前能下的結論：** `test_missing` 這一個測試已驗證，`python3 -m unittest -v test_service.TicketTests.test_missing` 執行通過（test-output.txt:2-4）。它涵蓋的只有「找不到時回 404」這條路徑。其他說法都還沒有證據，TTL 那一條更和程式本身衝突。下一步建議先跑完整測試，再決定 README 和程式哪個是對的，修掉不一致的那一邊。

## 三、`design-note.md` 的 cross-process lock

我沒辦法解釋這一題，因為提供的材料裡沒有 `design-note.md`。現有材料都沒提到 cross-process lock。README 寫的是「process-local ticket cache」（README.md:3），程式裡也沒有任何 lock。為了不自己編一套機制出來，請提供 `design-note.md`，我再依它的內容說明。

## 四、HTTP 404

HTTP 404 Not Found 是用戶端錯誤狀態碼，表示伺服器找不到請求指定的資源。它不代表伺服器故障，那種情況屬於 5xx。404 也不會說明這個資源是永久不存在還是暫時不存在。在這個 repo 裡，找不到 ticket 時，`handle_get` 會回傳 `404, {"error": "not found"}`（service.py:30-31）。

---

可以再追加的內容有兩項：一是比較加上 `NotFound` 分支前後找不到 ticket 時的路徑差異圖，二是一張 README 宣稱和程式實際行為的對照表。

順便留一個可以想想的問題：如果 README 說的 60 秒 TTL 才是預期行為，那麼 repo 裡某張 ticket 被更新後，`get_ticket` 會回傳什麼？要多久才會看到新資料？
