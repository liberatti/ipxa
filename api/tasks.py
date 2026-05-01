import json
import os
from datetime import timedelta, datetime

from nxcore.common_utils import gen_random_string
from nxcore.middleware.logging import logger

import bcrypt
import config
from api.repository.feed_model import FeedDao
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao
from api.repository.workspace_model import WorkspaceDao
from api.tools import feed_tool
from api.tools.telemetry import get_instance_uid, send_telemetry
from config import TZ

INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
}


def should_update(feed):
    """
    Checks if a feed should be updated based on its update interval and last update time.

    Args:
        feed (dict): The feed dictionary containing 'update_interval' and 'updated_on'.

    Returns:
        bool: True if the feed should be updated, False otherwise.
    """
    update_type = feed.get("update_interval", "hourly")
    updated_on = feed.get("updated_on")
    if not updated_on:
        return True
    interval = INTERVALS.get(update_type, timedelta(hours=1))
    return datetime.now(TZ) - updated_on >= interval


def install_task():
    """
    Performs initial setup tasks, including creating the database schema,
    persisting a default workspace, and initializing feeds and other repositories.
    """
    os.makedirs(config.DB_PATH, exist_ok=True)
    with WorkspaceDao() as dao:
        dao.create_schema()
        workspace = {
            "name": "default",
            "apikey": gen_random_string(),
            "instance_uid": get_instance_uid()
        }
        dao.persist(workspace)
    with FeedDao() as dao:
        dao.create_schema()
        for c in os.listdir(config.APP_BASE + "/config"):
            with open(config.APP_BASE + "/config/" + c) as f:
                feed = json.load(f)
                dao.persist(feed)

    with RBLDao() as dao:
        dao.create_schema()

    with GeoIpDao() as dao:
        dao.create_schema()
    logger.info("Database created")


def update_task():
    """
    Updates all feeds that are due for an update based on their intervals.
    """
    with FeedDao() as fdao:
        feeds = fdao.get_all()['data']
        for feed in feeds:
            if not should_update(feed):
                logger.info(f"Skip feed {feed['name']} updated on {feed['updated_on']}")
                continue
            provider = feed.get('provider')
            match provider:
                case 'ipverse':
                    feed_tool.update_ipverse(feed)
                case 'iptoasn':
                    feed_tool.update_ip2asn(feed)
                case 'maxmind':
                    if config.MAXMIND_ACCOUNT_ID and config.MAXMIND_LICENSE_KEY:
                        feed_tool.update_maxmind(config.MAXMIND_ACCOUNT_ID, config.MAXMIND_LICENSE_KEY)
                    else:
                        logger.warning("MaxMind credentials not provided")
                case None:
                    logger.warning("Provider not supported")
                case _:
                    feed_tool.update_feed(feed)
            feed['updated_on'] = datetime.now(TZ)
            fdao.update_by_id(feed['_id'], feed)
    logger.info("Database updated")


def send_telemetry_task():
    """
    Sends telemetry data to the remote server.
    """
    send_telemetry()
