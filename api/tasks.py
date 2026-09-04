import json
import os
import traceback
from datetime import timedelta, datetime

from nxcore.middleware.logging_manager import logger

import bcrypt
import config
from api.repository.feed_model import FeedDao
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao
from api.repository.oauth_model import UserDao
from api.tools import feed_tool

INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
}


def __should_update(feed):
    """
    Checks if a feed should be updated based on its update interval and last update time.

    Args:
        feed (dict): The feed dictionary containing 'update_interval' and 'updated_on'.

    Returns:
        bool: True if the feed should be updated, False otherwise.
    """
    if "embedded" in feed.get("format", ""):
        return False
    update_type = feed.get("update_interval", "hourly")
    updated_on = feed.get("updated_on")
    if not updated_on:
        return True

    if isinstance(updated_on, str):
        try:
            updated_on = datetime.fromisoformat(updated_on)
        except Exception:
            try:
                from email.utils import parsedate_to_datetime

                updated_on = parsedate_to_datetime(updated_on)
            except Exception:
                return True

    if not isinstance(updated_on, datetime):
        return True

    now = datetime.now(config.TZ)
    if updated_on.tzinfo is None and now.tzinfo is not None:
        now = datetime.now()
    elif updated_on.tzinfo is not None and now.tzinfo is None:
        updated_on = updated_on.replace(tzinfo=None)

    interval = INTERVALS.get(update_type, timedelta(hours=1))
    return now - updated_on >= interval


def install_task():
    """
    Performs initial setup tasks, including creating the database schema,
    initializing feeds and other repositories.
    """
    os.makedirs(config.DB_PATH, exist_ok=True)
    with UserDao() as dao:
        dao.create_schema()
    with FeedDao() as dao:
        dao.create_schema()
        for c in os.listdir(config.APP_BASE + "/config"):
            with open(config.APP_BASE + "/config/" + c) as f:
                feed = json.load(f)
                logger.info(f"Install feed {feed['provider']} : {feed['name']}")
                dao.persist(feed)

    with RBLDao() as dao:
        dao.create_schema()

    with GeoIpDao() as dao:
        dao.create_schema()
    logger.info("Database created")


def update_task(override_existing=False):
    """
    Updates all feeds that are due for an update based on their intervals.

    Args:
        override_existing (bool): If True, updates all feeds regardless of their update interval.
    """
    logger.info(f"Update task started with override = {override_existing}")
    with UserDao() as dao:
        secure_password = bcrypt.hashpw(
            config.ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user = dao.get_by_email(config.ADMIN_EMAIL)
        if not user:
            dao.persist(
                {
                    "name": "Administrator",
                    "email": config.ADMIN_EMAIL,
                    "password": secure_password,
                    "role": "superuser",
                }
            )
        else:
            if not bcrypt.checkpw(
                config.ADMIN_PASSWORD.encode("utf-8"), user["password"].encode("utf-8")
            ):
                user["password"] = secure_password
                dao.update_by_id(user["_id"], user)

    with FeedDao() as fdao:
        config_dir = os.path.join(config.APP_BASE, "config")
        existing_feeds = fdao.get_all().get("data", [])
        existing_slugs = {f.get("slug") for f in existing_feeds if f.get("slug")}

        if os.path.isdir(config_dir):
            for filename in sorted(os.listdir(config_dir)):
                if filename.endswith(".json"):
                    file_path = os.path.join(config_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            feed_data = json.load(f)
                            slug = feed_data.get("slug") or feed_data.get("name")
                            if slug and slug not in existing_slugs:
                                logger.info(
                                    f"Install feed {feed_data.get('provider')} : {feed_data.get('name')}"
                                )
                                fdao.persist(feed_data)
                                existing_slugs.add(slug)
                    except Exception as e:
                        logger.error(f"Failed to load feed config {filename}: %s", e)

        feeds = fdao.get_all()["data"]
        for feed in feeds:
            if override_existing or __should_update(feed):
                try:
                    provider = feed.get("provider")
                    # logger.info(f"Processing feed {provider} : {feed['name']}")
                    match provider:
                        case "ipverse":
                            feed_tool.update_ipverse(feed)
                        case "iptoasn":
                            feed_tool.update_ip2asn(feed)
                        case "ipinfo":
                            if config.IPINFO_TOKEN:
                                feed_tool.update_ipinfo(config.IPINFO_TOKEN, feed)
                            else:
                                logger.warning("ipinfo token not provided")
                        case "maxmind":
                            if config.MAXMIND_ACCOUNT_ID and config.MAXMIND_LICENSE_KEY:
                                feed_tool.update_maxmind(
                                    config.MAXMIND_ACCOUNT_ID,
                                    config.MAXMIND_LICENSE_KEY,
                                )
                            else:
                                logger.warning("MaxMind credentials not provided")
                        case None:
                            logger.warning("Provider not supported")
                        case _:
                            feed_tool.update_feed(feed)
                    feed["updated_on"] = datetime.now(config.TZ)
                    fdao.update_by_id(feed["_id"], feed)
                except Exception as e:
                    logger.error(f"Failed to load {feed['name']}: %s", e)
                    logger.error(traceback.format_exc())
    logger.info("Database updated")
