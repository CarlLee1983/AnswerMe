# Request

`get_ticket` returns the cached dict itself, so a caller that edits the result also changes the cache. Make it return a copy. Keep the API responses unchanged.
