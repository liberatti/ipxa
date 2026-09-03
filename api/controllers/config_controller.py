from flask import Blueprint, Response
from nxcore.controllers.base_controller import response_data
import config

routes = Blueprint("config", __name__)


@routes.route("", methods=["GET"])
@routes.route("/", methods=["GET"])
def get_config() -> Response:
    """
    Returns the configuration.

    Returns:
        Response: A Flask Response object containing the configuration.
    """
    return response_data({"security_enabled": config.SECURITY_ENABLED})
