One change shipped: each batch now shares a single connection. Separately, the note warns that duplicate notifications may still happen. The note recommends that batch callers record `request_id`, but `request_id` does not prevent duplicates. Deduplication by `request_id` is only a possible future feature. The numbers don't show how much the change helped. The output line shows only that one batch was accepted. (Source: `change-note.md`, a fictional teaching note. Line numbers below refer to that file.)

**Terms.** The project uses "batch" (批次) to mean a group of work items submitted together in one submission (line 3). I use "batch" in that sense throughout.

**What changed (done, not planned).** All work items in a batch now use one shared connection (line 5). That is the only completed behavior change the note reports. The note doesn't say what the old behavior was. "One connection per work item" is a plausible guess, but the source doesn't state it.

**What the numbers establish.** The note has three performance statements. They are separate and can't be combined.

| Statement | Kind | Conditions given | What it can support |
| --- | --- | --- | --- |
| "Throughput improved significantly" (吞吐量大幅改善) | The author's claim | None | Only that the author believes it improved. No measurement backs the size of the improvement (line 5). |
| 120 work items per second | A recorded value | No old-version value, machine, load or measurement date (line 5) | One throughput reading under unknown conditions. With no baseline, it can't show an improvement or how big one was. |
| p95 latency 42 ms | A recorded observation | 2026-09-15, test environment, fixed 10 concurrent requests. No machine model (line 7) | The latency of 95% of requests was 42 ms or lower under those conditions. It has no before value, so it doesn't show whether latency changed. |

The note says explicitly that the latency record is an independent observation. It also says the latency record isn't stated to come from the same test as the throughput record (line 7). So don't read "120 items/s at 42 ms p95" as one measured operating point. The note supports two unrelated readings and doesn't link them to each other or to the connection change. My inference is that the evidence doesn't yet show that sharing the connection caused any measured change.

**What the raw output establishes.** The only raw output is:

```text
batch_id=B-17 status=accepted request_id=req_02
```

(lines 15–17). It shows only that batch `B-17` reached status `accepted` and that the batch carries `request_id` `req_02`. It doesn't show:

- that a notification was delivered. The note says an accepted request doesn't mean the notification was delivered (line 9).
- that duplicates were avoided. `request_id` is currently used only for tracing (line 9).
- anything about throughput, latency or the shared connection.

**What callers are advised to do.** The note *recommends* (建議), and doesn't require, that batch callers record `request_id` (line 9). Keep the reason in mind: today `request_id` helps you trace a request. It does not guarantee that duplicate notifications are removed. Duplicate notifications may still occur (line 9). The note doesn't say how often duplicates happen or when.

The note gives no handling instructions beyond recording `request_id`. My inference is that callers should not rely on `status=accepted` as proof of delivery, and should not assume that notifications arrive exactly once. The note doesn't say what a caller should do when a duplicate arrives. That is a gap in the source, so I can't give you a step for it.

**What is planned (not built).** The next version *may* add deduplication of notifications by `request_id`. It isn't implemented, and no delivery date is committed (line 11). Until it ships, treat `request_id` as a tracing aid only.

**Evidence gaps that affect your judgment.**

- No baseline for throughput or latency, so the size of any improvement is unknown.
- The throughput reading has no machine, load or date.
- The latency reading has no machine model, and its link to the throughput test is unknown.
- The frequency of duplicate notifications is unknown, and the note doesn't say what to do when one arrives.

**Optional check question.** Suppose a caller gets two notifications for `req_02`. Which statement in the note explains why that can happen today? And which planned change, if it ships, might stop it?
