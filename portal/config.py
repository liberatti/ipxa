import os
import pytz
import json

APP_BASE = os.environ.get("APP_BASE", ".")

APP_VERSION = json.load(open(os.path.join(APP_BASE, "package.json")))["version"]

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TZ = pytz.timezone("UTC")

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()

WORKERS = int(os.environ.get("WORKERS", 4))
THREADS = int(os.environ.get("THREADS", 4))

IPXA_API_URL = os.environ.get("IPXA_API_URL", "dev_api_key")
IPXA_API_KEY = os.environ.get("IPXA_API_KEY", "dev_api_key")
