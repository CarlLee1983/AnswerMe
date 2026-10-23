# PR #412: Bounded retries for the cache gateway (fictional teaching material)

## What changed

- `CacheGateway.read` now stops retrying the origin after `retry_budget` attempts (default 3). Before this PR it retried until the 5-second request timeout.
- The retry budget is now a first-class citizen of the service config: `retry_budget` lives in `config/cache.yaml` instead of a hard-coded constant.
- The admin view now surfaces stale cache entries: entries older than `STALE_AFTER_S=120` are listed with their age.
- Redis plays the role of a write-through layer in front of the origin; this PR does not change that.

## Why

Unbounded retries were load-bearing in the worst way: one slow origin could pin every worker. Capping them changes the shape of the request path under failure.

## Evidence

- Staging, 2026-10-02, three runs with the origin delayed by 2 seconds: p99 latency for `GET /items` dropped from 840 ms to 310 ms.
- `pytest tests/cache` passed locally (38 tests). CI has not run on this branch yet.
- We believe this should also reduce on-call pages, but we have not measured it.

This marks a major milestone in our reliability journey.

## Not in this PR

- Moving eviction to a background worker is planned as a follow-up; no date yet.
