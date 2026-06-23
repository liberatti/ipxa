import traceback
from typing import Dict

import bcrypt
from nxcore.controllers.base_controller import response_data

from flask import Blueprint, request, Response
from marshmallow import ValidationError

from config import JWT_EXPIRE

routes = Blueprint("config", __name__)


@routes.route("/", methods=["GET"])
def get_config() -> Response:
    """
    Returns the configuration.

    Returns:
        Response: A Flask Response object containing the configuration.
    """
    return response_data({"portal_enabled": config.PORTAL_ENABLED})
