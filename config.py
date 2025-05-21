# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Cache configuration
CACHE_TYPE                         = os.getenv("CACHE_TYPE", "SimpleCache")
CACHE_DEFAULT_TIMEOUT             = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
CACHE_LIST_CLIENT_TABS_TIMEOUT    = int(os.getenv("CACHE_LIST_CLIENT_TABS_TIMEOUT", 3600))
CACHE_FETCH_PLANNED_HOURS_TIMEOUT = int(os.getenv("CACHE_FETCH_PLANNED_HOURS_TIMEOUT", 900))
CACHE_FETCH_TIME_ENTRIES_TIMEOUT  = int(os.getenv("CACHE_FETCH_TIME_ENTRIES_TIMEOUT", 300))

# Only relevant when using RedisCache:
CACHE_REDIS_URL                   = os.getenv("CACHE_REDIS_URL", "")

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
GOOGLE_SHEET_ID                = os.getenv("GOOGLE_SHEET_ID")

# Harvest
HARVEST_ACCOUNT_ID    = os.getenv("HARVEST_ACCOUNT_ID")
HARVEST_ACCESS_TOKEN  = os.getenv("HARVEST_ACCESS_TOKEN")
HARVEST_USER_AGENT    = os.getenv("HARVEST_USER_AGENT")

# Basic validation
missing = [
    var for var in [
        "GOOGLE_SHEETS_CREDENTIALS_JSON",
        "GOOGLE_SHEET_ID",
        "HARVEST_ACCOUNT_ID",
        "HARVEST_ACCESS_TOKEN",
        "HARVEST_USER_AGENT",
    ] if not os.getenv(var)
]
if missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
