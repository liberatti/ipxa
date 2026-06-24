import os
import secrets
import pytz
from cachetools import TTLCache
import json

APP_BASE = os.environ.get("APP_BASE", ".")

APP_VERSION = json.load(open(os.path.join(APP_BASE, "package.json")))["version"]

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TZ = pytz.timezone("UTC")

MAINTENANCE_WINDOW = "01:00"

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
DB_PATH = os.environ.get("DB_PATH", "data")

IBLOCKLIST_USERNAME = os.environ.get("IBLOCKLIST_USERNAME", None)
IBLOCKLIST_PASSWORD = os.environ.get("IBLOCKLIST_PASSWORD", None)

MAXMIND_ACCOUNT_ID = os.environ.get("MAXMIND_ACCOUNT_ID", None)
MAXMIND_LICENSE_KEY = os.environ.get("MAXMIND_LICENSE_KEY", None)

cache = TTLCache(maxsize=1000, ttl=int(os.environ.get("CACHE_TTL", 30)))

WORKERS = int(os.environ.get("WORKERS", 4))
THREADS = int(os.environ.get("THREADS", 4))

# Security config
SECURITY_ENABLED = True
KEY_SIZE = 2048
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_EXPIRE = 3600
JWT_AUD = "ipxa"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@local")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
API_KEY = os.environ.get("API_KEY", "dev_api_key")
PORTAL_ENABLED = os.environ.get("PORTAL_ENABLED", "false").lower() == "true"
