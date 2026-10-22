# Agent change report

Done. `get_ticket` now returns a copy on both cache hits and misses, and I added `test_returns_copy`. While there, I made the 404 body clearer by adding the ticket id. All tests pass and lint is clean. I did not run the API integration tests because no local server was available.
