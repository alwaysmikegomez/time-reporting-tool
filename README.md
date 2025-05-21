# Time Reporting Tool

## Caching Strategy

To reduce latency and limit API/Sheets calls, we use [Flask-Caching](https://flask-caching.readthedocs.io/) with:

- **SimpleCache** in development  
- **RedisCache** in production (just change `CACHE_TYPE` and point `CACHE_REDIS_URL` at your Redis instance)

### What’s Cached

| Function                     | Module                | TTL           |
|------------------------------|-----------------------|---------------|
| `list_client_tabs()`         | `backend/sheets.py`   | 1 hour        |
| `fetch_planned_hours(...)`   | `backend/sheets.py`   | 15 minutes    |
| `fetch_time_entries(...)`    | `backend/harvest.py`  | 5 minutes     |

### Configuration

All cache settings live in `config.py` and default to:

```env
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300
CACHE_LIST_CLIENT_TABS_TIMEOUT=3600
CACHE_FETCH_PLANNED_HOURS_TIMEOUT=900
CACHE_FETCH_TIME_ENTRIES_TIMEOUT=300
```

To override, set the corresponding `CACHE_*` environment variable.

### Cache Busting

- **Manual:** call `cache.clear()` in the Python REPL or restart the app.  
- **Force-refresh (optional):** implement a `?refresh=1` query parameter that calls:
  ```python
  cache.delete_memoized(fetch_planned_hours, start, end, client)
  cache.delete_memoized(fetch_time_entries, start, end)
  ```
  before running the helper.
