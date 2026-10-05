One thing changed: all work items in a batch now share one connection. None of the numbers in the note shows that this change made anything faster, and the sample output shows only that a request was accepted, not that a notification was delivered. Callers are advised, but not required, to log `request_id`. Logging it does not stop duplicate notifications. (Source: `tests/answer-me/clarity/input/change-note.md`. The file calls itself fictional teaching material, line 1. Line numbers below refer to this file.)

A term first: the project calls a batch 「批次」 and defines it as "a group of work items submitted together" (line 3). I use "batch" for this term throughout.

**What changed**

The note marks one change as done: each batch now shares a single connection (line 5). The note says nothing about how connections worked before, so I can't describe the old behavior. I can only say that per-batch connection sharing is now in place.

**What the numbers actually establish**

The note contains two measurements and one claim. None of them is a before/after comparison.

| Item | What the note says | What is missing | What it supports |
| --- | --- | --- | --- |
| "Throughput improved significantly" | The author's claim (line 5) | Any measured comparison | It is the author's opinion, not a verified result |
| 120 work items per second | Recorded in the note (line 5) | Old-version value, machine, load, measurement date (line 5) | A value was recorded once. It can't show an improvement because there is no baseline |
| p95 latency 42 ms | 2026-09-15, test environment, fixed 10 concurrent requests (line 7) | Machine model. Also no statement that it came from the same test run as the throughput figure (line 7) | p95 latency was 42 ms under those conditions on that date. It has no earlier value to compare against |

Do not combine the two numbers into one result, such as "120 items/s at 42 ms p95". The note describes the latency record as a separate observation and does not link it to the throughput run (lines 7). It also does not say whether the 42 ms was measured before or after the connection-sharing change, or whether it came from batch calls at all. That is my reading of what the note leaves out. The note does not say it directly.

**What the raw output shows**

```text
batch_id=B-17 status=accepted request_id=req_02
```

This line (line 16) shows that batch `B-17` was accepted and carries `request_id` `req_02`. It does not show that a notification was delivered. The note states this directly: "an accepted request does not mean the notification has been delivered" (line 9). It is also a single line. It is not a test run and does not confirm throughput, latency, or deduplication behavior.

**What callers are advised to do**

The note says duplicate notifications **may** still occur (line 9). The advice for batch callers is a recommendation, not a requirement:

1. Log the `request_id` from each batch call (line 9).

Expected result: you can trace a call by its `request_id`. You do **not** get deduplication. The note says `request_id` "is currently used only for tracing and does not guarantee removal of duplicate notifications" (line 9). If your code must not act twice on the same notification, the note gives no mechanism for that today. It also does not say who handles duplicates. That responsibility is a gap in the source.

**What is planned, not implemented**

The next version **may** add deduplication of notifications by `request_id`. It is not implemented, and no delivery date is committed (line 11). Don't design on the assumption that it will arrive.

**Evidence gaps that affect judgment**

- No baseline throughput, and no machine, load, or date for the 120 items/s figure (line 5).
- No machine model for the latency record, and no link between it and the throughput record (line 7).
- No description of the connection behavior before the change (line 5 only gives the new state).
- No test results of any kind. The note has no test run or pass/fail record. The only raw output is one accepted-status line (line 16).
- No owner named for handling duplicate notifications (line 9).

Verification performed: I read only `change-note.md` and checked each claim above against its line. I ran nothing and could not reproduce any measurement.

Optional check question: if a notification for `req_02` arrives twice, what in the current system tells your code to ignore the second one? (Per the note, nothing does yet.)
