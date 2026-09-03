import os
import secrets
import pytz
from cachetools import TTLCache
import json

APP_BASE = os.environ.get("APP_BASE", ".")

try:
    APP_VERSION = json.load(open(os.path.join(APP_BASE, "package.json")))["version"]
except Exception:
    APP_VERSION = "develop"

APP_CONTEXT = "/ipxa"

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TZ = pytz.timezone("UTC")

MAINTENANCE_WINDOW = "01:00"

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
DB_PATH = os.environ.get("DB_PATH", "data")

IBLOCKLIST_USERNAME = os.environ.get("IBLOCKLIST_USERNAME", None)
IBLOCKLIST_PASSWORD = os.environ.get("IBLOCKLIST_PASSWORD", None)

MAXMIND_ACCOUNT_ID = os.environ.get("MAXMIND_ACCOUNT_ID", None)
MAXMIND_LICENSE_KEY = os.environ.get("MAXMIND_LICENSE_KEY", None)

IPINFO_TOKEN = os.environ.get("IPINFO_TOKEN", None)

cache = TTLCache(maxsize=1000, ttl=int(os.environ.get("CACHE_TTL", 30)))

WORKERS = int(os.environ.get("WORKERS", 4))
THREADS = int(os.environ.get("THREADS", 4))

# Security config
SECURITY_ENABLED = os.environ.get("SECURITY_ENABLED", "true") == "true"
KEY_SIZE = 2048
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_EXPIRE = 3600
JWT_AUD = "ipxa"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@local")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
API_KEY = os.environ.get("API_KEY", "dev_api_key")
CORS = {
    r"/.*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": "*",
        "expose_headers": [
            "Content-Type",
            "Authorization",
            "X-Total-Count",
            "X-Page",
            "X-Size",
        ],
        "supports_credentials": False,
        "max_age": 3600,
    }
}
