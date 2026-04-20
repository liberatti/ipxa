import os

import pytz
from cachetools import TTLCache
import json

APP_BASE = os.environ.get("APP_BASE", ".")

APP_VERSION = json.load(open(os.path.join(APP_BASE, "web/package.json")))['version']

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TZ = pytz.timezone("UTC")

MAINTENANCE_WINDOW = "01:00"

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
DB_PATH = os.environ.get("DB_PATH", 'data')

IBLOCKLIST_USERNAME = os.environ.get("IBLOCKLIST_USERNAME", None)
IBLOCKLIST_PASSWORD = os.environ.get("IBLOCKLIST_PASSWORD", None)

MAXMIND_ACCOUNT_ID = os.environ.get("MAXMIND_ACCOUNT_ID", None)
MAXMIND_LICENSE_KEY = os.environ.get("MAXMIND_LICENSE_KEY", None)

cache = TTLCache(maxsize=1000, ttl=int(os.environ.get("CACHE_TTL", 30)))
WORKERS = int(os.environ.get("WORKERS", 4))
THREADS = int(os.environ.get("THREADS", 4))

TELEMETRY_ENABLE = os.environ.get("TELEMETRY_ENABLE", "true") == "true"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tdyemcybdhpuuvkqmqox.supabase.co/rest/v1")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRke"
    "WVtY3liZGhwdXV2a3FtcW94Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4NDgzMjIsImV4cCI"
    "6MjA5MTQyNDMyMn0.I5-JgP2qdavo7o8ncH4TQqKmibfH8aeoRFXdRmQ0Cg0"
)
