from flask import Blueprint, Response
from nxcore.controllers.base_controller import response_data
import config
import json

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
