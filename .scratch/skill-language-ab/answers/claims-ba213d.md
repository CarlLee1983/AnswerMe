The one completed change is that all work items in a batch now share one connection. The note has a throughput figure and a latency figure, but neither one shows that this change made the system faster. Callers are advised to log `request_id`. That ID does not prevent duplicate notifications yet, so callers still need to expect duplicates. (Source: `change-note.md`, a fictional teaching note. Line numbers below refer to that file.)

**Terms.** The project calls a "batch" (批次) a group of work items submitted together in one call (line 3). I use "batch" in that sense throughout. A "batch caller" is the client code that submits a batch.

## What changed

The note marks one item as done: **each batch shares a single connection** (line 5). The note does not say how work items connected before, so the "before" behavior comes from the wording, not from the source. The usual reading is one connection per work item, but that is my inference.

A second item is **planned, not done**. A later release *may* add deduplication of notifications based on `request_id`. It is not implemented and has no committed delivery date (line 11). Treat it as a possibility, not as an upcoming feature you can design around.

## What the numbers actually establish

The note has two separate observations. Neither one supports a before/after comparison.

| | Throughput record | Latency record |
| --- | --- | --- |
| Value | 120 work items per second | p95 latency 42 ms |
| Date | Not given | 2026-09-15 |
| Environment | Not given | Test environment |
| Load | Not given | Fixed 10 concurrent requests |
| Machine | Not given | Not given |
| Baseline (old version) | Not given | Not given |
| Source | Line 5 | Line 7 |

- **"Throughput improved significantly" is the author's claim, not a verified result** (line 5). The only throughput figure is 120 work items/s, with no old-version value, machine, load, or date. Without a baseline, 120/s cannot show an improvement of any size, and without test conditions it cannot be reproduced or compared.
- **The 42 ms p95 is a single measurement under stated conditions.** It shows that in the test environment, with 10 concurrent requests, 95% of requests completed within 42 ms on 2026-09-15. It has no old-version value, so it says nothing about whether latency got better or worse. It also does not tell you what latency would be under other loads or in production.
- **The two records cannot be combined.** The note says explicitly that it does not state whether the latency and throughput records came from the same test run (line 7). So you cannot read them as "at 120 items/s, p95 is 42 ms."

Evidence gaps that affect any judgment about the change: no baseline for either metric, no conditions for the throughput figure, no machine model for either, and no link between the two runs.

## What the raw output shows

```text
batch_id=B-17 status=accepted request_id=req_02
```

(lines 15–17)

This line shows that the system accepted batch `B-17` and assigned or echoed `request_id=req_02`. It does **not** show that any notification was delivered. The note states directly that an accepted request does not mean the notification has arrived (line 9). It also does not show how many work items were in the batch, or whether they completed.

## What callers are advised to do

The note says duplicate notifications **may** still occur (line 9). For batch callers, the note *recommends* (it does not require) logging `request_id`. Its stated purpose is tracing only. The note says explicitly that `request_id` does not guarantee deduplication (line 9).

In practice, that means:

1. Log the `request_id` returned for each batch call, so you can trace a request later.
2. Do not treat `status=accepted` as confirmation of delivery. If you need to know a notification arrived, you need another signal. The note does not say what that signal is.
3. Do not rely on `request_id` to filter duplicates today. If duplicate notifications would cause harm in your code, handle that on your side. The note does not tell you how (my inference, not a recommendation from the source).
4. Do not plan around the `request_id` deduplication feature. It is unimplemented and undated (line 11).

## Gaps in the source

The note does not explain why sharing a connection would raise throughput, what was measured to support "significantly," or what causes the duplicate notifications. It also does not say which component sends the notifications, or which mechanism a caller should use to confirm delivery.

---

Optional check question: if the same notification for `req_02` arrives twice, what in the current system stops the second one from being processed, and what does the note say about that?
