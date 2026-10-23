import json
from flask import Blueprint, Response
from nxcore.controllers.base_controller import response_data
import config
from api.repository.feed_model import FeedDao
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao

routes = Blueprint("config", __name__)


@routes.route("", methods=["GET"])
def get_config() -> Response:
    """
    Returns the configuration.

    Returns:
        Response: A Flask Response object containing the configuration.
    """
    return response_data({"security_enabled": config.SECURITY_ENABLED})


@routes.route("/geo", methods=["GET"])
def get_geo_countries() -> Response:
    """
    Returns the geo countries.

    Returns:
        Response: A Flask Response object containing the geo countries.
    """
    data = []
    with open(f"{config.APP_PATH}/config/config-geo.json", "r") as f:
        data = json.load(f)
    return response_data(data)


@routes.route("/stats", methods=["GET"])
def get_stats() -> Response:
    """
    Returns active entry counts and sizes for cache, feeds, RBL, and GeoIP.

    Returns:
        Response: A Flask Response object containing cache_size, feeds_reputation,
                  feeds_bypass, rbl_size, and geoip_entries.
    """
    with FeedDao() as feed_dao:
        feeds_reputation = feed_dao.count_all(
            where_clause="type = ?", params=("reputation",)
        )
        feeds_bypass = feed_dao.count_all(where_clause="type = ?", params=("bypass",))

    with RBLDao() as rbl_dao:
        rbl_size = rbl_dao.count_all(params=())

    with GeoIpDao() as geoip_dao:
        geoip_entries = geoip_dao.count_all(params=())

    return response_data(
        {
            "cache_size": config.cache.currsize,
            "feeds_reputation": feeds_reputation,
            "feeds_bypass": feeds_bypass,
            "rbl_size": rbl_size,
            "geoip_entries": geoip_entries,
        }
    )
